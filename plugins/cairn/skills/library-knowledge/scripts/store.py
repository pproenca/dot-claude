#!/usr/bin/env python3
"""Storage port for library-knowledge. The ONLY module that touches the store.

Backend today: JSONL — one self-describing record per line. Reads STREAM the
file, so a name lookup parses lines until it matches and returns ONE record; the
caller (and the agent's context) never receives the whole store, no matter how
many libraries it holds. The index returns three fields per line; search scans
records (cheap at this scale).

This is a PORT. lib_lookup and lib_refresh call these functions and never touch
the file directly. Swapping the backend to SQLite / FTS5 — the move that earns
its place only when capability-search across a large store becomes hot — changes
ONLY this module; every caller is unaffected. JSONL makes that migration trivial
(one row per line).

Back-compat: if lib-knowledge.jsonl is absent but a legacy lib-knowledge.json
(single {"libraries": {name: entry}} object) exists, reads fall back to it and
the next upsert writes JSONL. upsert keeps one line per name (no duplicates), so
read_one can stop at the first match.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

JSONL_NAME = "lib-knowledge.jsonl"
LEGACY_NAME = "lib-knowledge.json"


def jsonl_path(repo: Path, store: str | None) -> Path:
    return Path(store) if store else repo / JSONL_NAME


def _legacy(repo: Path) -> Path:
    return repo / LEGACY_NAME


def _legacy_records(repo: Path) -> Iterator[dict]:
    p = _legacy(repo)
    if not p.exists():
        return
    try:
        libs = json.loads(p.read_text(encoding="utf-8")).get("libraries", {})
    except (json.JSONDecodeError, OSError):
        return
    for name, entry in libs.items():
        yield {"name": name, **entry}


def read_one(repo: Path, store: str | None, name: str) -> dict | None:
    """Stream the store and return the record for `name` (early exit), or None.
    Only the matching record is materialized — the token-cheap path."""
    p = jsonl_path(repo, store)
    if p.exists():
        with p.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("name") == name:
                    return rec
        return None
    # legacy fallback
    for rec in _legacy_records(repo):
        if rec.get("name") == name:
            return rec
    return None


def iter_records(repo: Path, store: str | None) -> Iterator[dict]:
    p = jsonl_path(repo, store)
    if p.exists():
        with p.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
        return
    yield from _legacy_records(repo)


def read_index(repo: Path, store: str | None) -> list[dict]:
    """Cheap top-level view: name + confirmed_version + confirmed_on only."""
    return [
        {"name": r.get("name"), "confirmed_version": r.get("confirmed_version"),
         "confirmed_on": r.get("confirmed_on")}
        for r in iter_records(repo, store)
    ]


def _locked(p, fn):
    """Hold an exclusive advisory lock across the WHOLE read-modify-write."""
    import os, time
    lock = p.with_suffix(p.suffix + ".lock")
    p.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(500):
        try:
            os.close(os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)); break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > 10:
                    os.unlink(lock); continue
            except OSError:
                pass
            time.sleep(0.01)
    try:
        return fn()
    finally:
        try: os.unlink(lock)
        except OSError: pass


def _atomic_write_lines(p, lines):
    import os, tempfile
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".tmp-", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("".join(line + "\n" for line in lines)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def upsert(repo: Path, store: str | None, name: str, entry: dict) -> None:
    """Write/replace one record, keeping the file one-line-per-name (JSONL).
    Migrates a legacy json store to jsonl on first write."""
    p = jsonl_path(repo, store)
    def _rmw():
        records = {r["name"]: r for r in iter_records(repo, store) if r.get("name")}
        records[name] = {"name": name, **{k: v for k, v in entry.items() if k != "name"}}
        _atomic_write_lines(p, [json.dumps(records[n], ensure_ascii=False) for n in sorted(records)])
    _locked(p, _rmw)


def search(repo: Path, store: str | None, terms: str) -> list[tuple[int, dict]]:
    """Capability search: rank records by how many query terms appear in the
    name / capability / key_facts. Scan-backed today; the seam where SQLite FTS
    would slot in behind this port. Returns (score, record) sorted desc."""
    wants = [t for t in terms.lower().split() if t]
    scored: list[tuple[int, dict]] = []
    for r in iter_records(repo, store):
        hay = " ".join([
            str(r.get("name", "")), str(r.get("capability", "")),
            " ".join(r.get("key_facts", [])),
        ]).lower()
        score = sum(1 for w in wants if w in hay)
        if score:
            scored.append((score, r))
    scored.sort(key=lambda s: -s[0])
    return scored


# --- repo dependency reads (the freshness-comparison input, not the store) ---
import re as _re


def installed_version(repo: Path, name: str) -> str | None:
    """Read the version `name` is pinned to in the repo's package.json."""
    pkg = repo / "package.json"
    if not pkg.exists():
        return None
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    for field in ("dependencies", "devDependencies"):
        v = (data.get(field) or {}).get(name)
        if v:
            return v
    return None


def major(spec: str | None) -> str | None:
    if not spec:
        return None
    m = _re.search(r"(\d+)", spec)
    return m.group(1) if m else None


def staleness(entry: dict, installed: str | None) -> str:
    cm, im = major(entry.get("confirmed_version")), major(installed)
    if installed is None or cm is None or im is None:
        return "UNKNOWN"
    return "FRESH" if cm == im else "STALE"

#!/usr/bin/env python3
"""Storage port for specialist-knowledge. The ONLY module that touches the store.

Backend today: JSONL — one self-describing profile per line, keyed by `domain`.
Reads STREAM the file, so a domain lookup parses lines until it matches and
returns ONE profile; the caller never receives the whole store. This mirrors
library-knowledge's store port exactly — same pattern, different schema (craft
profiles, not version facts).

This is a PORT. specialist_lookup and specialist_refresh call these functions and
never touch the file directly. Swapping the backend changes ONLY this module.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

JSONL_NAME = "specialist-profiles.jsonl"


def jsonl_path(repo: Path, store: str | None) -> Path:
    return Path(store) if store else repo / JSONL_NAME


def _records(repo: Path, store: str | None) -> Iterator[dict]:
    p = jsonl_path(repo, store)
    if not p.exists():
        return
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                yield rec


def read_one(repo: Path, store: str | None, domain: str) -> dict | None:
    """Stream the store and return the profile for `domain` (early exit), or None."""
    for rec in _records(repo, store):
        if rec.get("domain") == domain:
            return rec
    return None


def read_index(repo: Path, store: str | None) -> list[dict]:
    """Return a compact index: domain + confirmed_on + pinned_libs per profile."""
    out = []
    for rec in _records(repo, store):
        out.append({
            "domain": rec.get("domain", "?"),
            "confirmed_on": rec.get("confirmed_on", "?"),
            "pinned_libs": rec.get("pinned_libs", {}),
        })
    return out


def read_all(repo: Path, store: str | None) -> list[dict]:
    return list(_records(repo, store))


def _locked(p, fn):
    """Hold an exclusive advisory lock across the WHOLE read-modify-write."""
    import os, time
    lock = p.with_suffix(p.suffix + ".lock")
    p.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    for _ in range(500):
        try:
            os.close(os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)); acquired = True; break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > 10:
                    os.unlink(lock); continue
            except OSError:
                pass
            time.sleep(0.01)
    if not acquired:
        raise TimeoutError(f"timed out waiting for lock {lock}")
    try:
        return fn()
    finally:
        if acquired:
            try: os.unlink(lock)
            except OSError: pass


def _atomic_write_lines(p, lines):
    import os, tempfile
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".tmp-", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("".join(line + "\n" for line in lines)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def upsert(repo: Path, store: str | None, profile: dict) -> None:
    """Insert or replace the profile for its domain. One line per domain."""
    p = jsonl_path(repo, store)
    def _rmw():
        existing = {r.get("domain"): r for r in _records(repo, store)}
        existing[profile["domain"]] = profile
        _atomic_write_lines(p, [json.dumps(rec, ensure_ascii=False) for rec in existing.values()])
    _locked(p, _rmw)

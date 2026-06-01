#!/usr/bin/env python3
"""Storage port for mental-models. The ONLY module that touches the store.

JSONL, one reframing model per line, keyed by `smell`. Reads stream the file.
Mirrors library-knowledge/specialist-knowledge ports; swapping the backend
changes only this module.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterator

JSONL_NAME = "mental-models.jsonl"


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
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def read_all(repo: Path, store: str | None) -> list[dict]:
    return list(_records(repo, store))


def search(repo: Path, store: str | None, smell: str) -> list[dict]:
    """Rank models by token overlap AND substring overlap between the query and
    stored smells/reframes. Substring matching is essential: distinctive smells
    like 'O(n^2)' normalize to tokens too short to survive a length filter, so
    token-only matching would miss the very smell that should match best."""
    qn = _norm(smell)
    q = {w for w in qn.split() if len(w) > 2}
    qshort = {w for w in qn.split() if w}  # all tokens incl. short (n, 2, o)
    scored = []
    for rec in _records(repo, store):
        hay = _norm(rec.get("smell", "") + " " + rec.get("reframe", ""))
        toks = {w for w in hay.split() if w}
        score = len(q & {w for w in toks if len(w) > 2}) * 2  # weighted token overlap
        # substring: does the stored smell appear in the query or vice-versa?
        sm = _norm(rec.get("smell", ""))
        if sm and (sm in qn or qn in sm):
            score += 3
        # short-token overlap (catches n, 2 from O(n^2)) at low weight
        score += len(qshort & toks)
        if score:
            scored.append((score, rec))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored]


def _locked(p, fn):
    """Hold an exclusive advisory lock across the WHOLE read-modify-write, so two
    concurrent upserts cannot both read stale state and have the last write drop a
    concurrent insert. The read must be inside the lock, not just the write."""
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
    """Temp-file + rename so a crash or concurrent read never sees a half-written store."""
    import os, tempfile
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".tmp-", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("".join(line + "\n" for line in lines)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def upsert(repo: Path, store: str | None, model: dict) -> None:
    p = jsonl_path(repo, store)
    def _rmw():
        existing = {r.get("smell"): r for r in _records(repo, store)}
        existing[model["smell"]] = model
        _atomic_write_lines(p, [json.dumps(rec, ensure_ascii=False) for rec in existing.values()])
    _locked(p, _rmw)


def _norm(s: str) -> str:
    return "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in s)

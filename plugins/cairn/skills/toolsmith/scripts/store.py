#!/usr/bin/env python3
"""Workshop catalogue (JSONL): tools indexed by the motion they replace, plus motion
tallies (how many times a hand-motion has recurred, for the Rule of Three)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterator

JSONL_NAME = "workshop.jsonl"


def jsonl_path(repo: Path, store: str | None) -> Path:
    return Path(store) if store else repo / JSONL_NAME


def _records(repo: Path, store: str | None) -> Iterator[dict]:
    p = jsonl_path(repo, store)
    if not p.exists(): return
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try: rec = json.loads(line)
                except json.JSONDecodeError: pass
                else:
                    if isinstance(rec, dict):
                        yield rec


def read_all(repo, store): return list(_records(repo, store))
def read_one(repo, store, key):
    for r in _records(repo, store):
        if r.get("key") == key: return r
    return None


def _locked(p, fn):
    import os, time
    lock = p.with_suffix(p.suffix + ".lock"); p.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    for _ in range(500):
        try: os.close(os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)); acquired = True; break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > 10: os.unlink(lock); continue
            except OSError: pass
            time.sleep(0.01)
    if not acquired:
        raise TimeoutError(f"timed out waiting for lock {lock}")
    try: return fn()
    finally:
        if acquired:
            try: os.unlink(lock)
            except OSError: pass


def _atomic_write_lines(p, lines):
    import os, tempfile
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".tmp-", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("".join(l + "\n" for l in lines)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def upsert(repo: Path, store: str | None, rec: dict) -> None:
    p = jsonl_path(repo, store)
    def _rmw():
        ex = {r.get("key"): r for r in _records(repo, store)}
        ex[rec["key"]] = rec
        _atomic_write_lines(p, [json.dumps(r, ensure_ascii=False) for r in ex.values()])
    _locked(p, _rmw)

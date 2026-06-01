#!/usr/bin/env python3
"""Storage port for capability-ledger (JSONL, keyed by problem_class)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterator
JSONL_NAME = "capability-ledger.jsonl"
def jsonl_path(repo: Path, store: str | None) -> Path:
    return Path(store) if store else repo / JSONL_NAME
def _records(repo: Path, store: str | None) -> Iterator[dict]:
    p = jsonl_path(repo, store)
    if not p.exists(): return
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: yield json.loads(line)
            except json.JSONDecodeError: continue
def read_one(repo: Path, store: str | None, cls: str) -> dict | None:
    for r in _records(repo, store):
        if r.get("problem_class") == cls: return r
    return None
def read_all(repo: Path, store: str | None) -> list[dict]:
    return list(_records(repo, store))
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


def upsert(repo: Path, store: str | None, entry: dict) -> None:
    p = jsonl_path(repo, store)
    def _rmw():
        ex = {r.get("problem_class"): r for r in _records(repo, store)}
        ex[entry["problem_class"]] = entry
        _atomic_write_lines(p, [json.dumps(r, ensure_ascii=False) for r in ex.values()])
    _locked(p, _rmw)

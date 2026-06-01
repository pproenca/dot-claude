#!/usr/bin/env python3
"""Retrieval port — the seam where smarter search slots in WHEN EARNED.

Cairn's learning is only as good as its recall: a lesson learned under one
phrasing must surface when the same problem appears under different words. Today,
with sparse stores, a dependency-free token+substring matcher is the right and
honest backend — semantic search over two entries would be theatre. This module
is the BOUNDARY behind which a heavier engine (e.g. a local hybrid BM25+vector
reranker like qmd) can later replace the matcher with zero change to any skill.

The swap is promote-on-evidence, not install-at-birth: when the knowledge-ratchet
has logged enough 'learned-but-did-not-recall' frictions, this port's backend is
swapped. Until then, the matcher stands. Building the seam costs nothing and
commits to nothing; building the engine must be earned.

Contract:
    rank(query, records, fields) -> list[(score, record)] sorted desc, score > 0
A record is a dict; fields names which keys to search. Backend is selected by the
CAIRN_RETRIEVAL env var ('matcher' default; 'qmd' reserved for the earned swap).
"""
from __future__ import annotations
import os


def _norm(s: str) -> str:
    return "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in str(s))


def _match_rank(query: str, records: list[dict], fields: list[str]) -> list[tuple[float, dict]]:
    """Dependency-free backend: weighted token overlap + substring containment.
    Correct for sparse stores; this is the matcher hardened across the adversarial
    passes (substring catches distinctive short smells like 'O(n^2)')."""
    qn = _norm(query)
    q_long = {w for w in qn.split() if len(w) > 2}
    q_all = {w for w in qn.split() if w}
    scored: list[tuple[float, dict]] = []
    for rec in records:
        hay = _norm(" ".join(str(rec.get(f, "")) for f in fields))
        toks = {w for w in hay.split() if w}
        score = len(q_long & {w for w in toks if len(w) > 2}) * 2.0
        # substring containment in either direction (the key per-field smell)
        primary = _norm(str(rec.get(fields[0], ""))) if fields else ""
        if primary and (primary in qn or qn in primary):
            score += 3.0
        score += len(q_all & toks)  # short-token overlap, low weight
        if score > 0:
            scored.append((score, rec))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def _qmd_rank(query: str, records: list[dict], fields: list[str]) -> list[tuple[float, dict]]:
    """Reserved earned-swap backend. Intentionally not implemented at birth: a
    semantic engine is promote-on-evidence (see module docstring). When the ratchet
    earns it, this is where a local hybrid retriever is wired — same contract, so no
    skill changes. Until then we fail SAFE back to the matcher rather than pretend."""
    return _match_rank(query, records, fields)


def rank(query: str, records: list[dict], fields: list[str]) -> list[tuple[float, dict]]:
    backend = os.environ.get("CAIRN_RETRIEVAL", "matcher")
    if backend == "qmd":
        return _qmd_rank(query, records, fields)
    return _match_rank(query, records, fields)

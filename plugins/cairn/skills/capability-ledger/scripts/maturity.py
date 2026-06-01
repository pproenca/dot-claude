#!/usr/bin/env python3
"""Pure maturity function — license is computed from solves, never hand-set.

This module is part of Cairn's FIXED substrate: the entity cannot change it by
learning, so its correctness must not depend on accumulated knowledge. Two
hardening notes drive the design below:

- Floor semantics are not one-size. A *ratio* to a floor only makes sense when the
  floor is a positive quantity (a frame time, an allocation count > 0). For
  correctness-shaped classes the floor is ZERO (0 defects, 0 allocations), and a
  ratio is undefined. Such a solve must declare `floor_kind: "count"` with an
  absolute `count` (0 = at floor); a ratio solve declares `floor_kind: "ratio"`
  (default) with `floor_ratio`. A solve whose floor kind is ambiguous does NOT
  count — silence here would inflate competence.

- Dates are compared as real dates, never as raw strings, because a malformed or
  non-zero-padded date string can sort wrong lexicographically and silently
  un-stick a demotion. If a date cannot be parsed, we fail SAFE: the demotion cap
  holds (we do not treat an unparseable solve as post-demotion evidence).
"""
from __future__ import annotations
import datetime as _dt

# A SEED, not law. "Near-floor" within 2x is a starting parameter Cairn can evolve
# from its own history (like inquiry's calibration thresholds): a problem class may
# carry its own `near_floor` once Cairn has enough solves to know what "near" means
# for that class. The mechanism (judge against floor, not baseline) is fixed; the
# threshold value is Cairn's to tune, per class, from evidence — never my constant.
NEAR_FLOOR_SEED = 2.0


def _parse_date(s) -> _dt.date | None:
    try:
        return _dt.date.fromisoformat(str(s))
    except (ValueError, TypeError):
        return None


def _is_credited_solve(s: dict, threshold: float) -> bool:
    """A solve counts only if benchmarked AND demonstrably at/near the floor, with
    a floor kind that is unambiguous."""
    if not s.get("benchmark_ref"):
        return False
    kind = s.get("floor_kind", "ratio")
    if kind == "ratio":
        fr = s.get("floor_ratio")
        return isinstance(fr, (int, float)) and fr <= threshold
    if kind == "count":
        # absolute count: at-floor means count <= the class's allowed count (default 0)
        c = s.get("count")
        allowed = s.get("count_allowed", 0)
        return isinstance(c, (int, float)) and isinstance(allowed, (int, float)) and c <= allowed
    return False  # unknown floor kind -> no credit (no silent inflation)


def credited(solves: list[dict], threshold: float = NEAR_FLOOR_SEED) -> list[dict]:
    return [s for s in solves if _is_credited_solve(s, threshold)]


def compute_maturity(solves: list[dict], threshold: float = NEAR_FLOOR_SEED) -> str:
    c = credited(solves, threshold)
    domains = {s.get("domain") for s in c if s.get("domain")}
    if len(c) >= 3 and len(domains) >= 2:
        return "proven"
    if len(c) >= 3:
        return "practiced"
    return "novice"


def effective_maturity(entry: dict, threshold: float = NEAR_FLOOR_SEED) -> str:
    """The maturity actually in force — demotion is STICKY. A recorded miss caps the
    rung until NEW credited solves arrive AFTER the demotion. Dates are compared as
    real dates; an unparseable solve date fails SAFE (does not lift the cap)."""
    # a class may carry its OWN near_floor, tuned from its history — Cairn's value,
    # not the seed. Falls back to the seed only until Cairn has evolved one.
    threshold = entry.get("near_floor", threshold)
    computed = compute_maturity(entry.get("solves", []), threshold)
    dem = entry.get("last_demotion")
    if not dem:
        return computed
    dem_date = _parse_date(dem.get("date"))
    after = []
    for s in credited(entry.get("solves", []), threshold):
        sd = _parse_date(s.get("date"))
        # post-demotion evidence requires BOTH dates parse AND solve is strictly later
        if sd is not None and dem_date is not None and sd > dem_date:
            after.append(s)
    if len(after) >= 1:
        return computed
    rank = {"novice": 0, "practiced": 1, "proven": 2}
    cap = dem.get("to", "novice")
    return cap if rank.get(computed, 0) > rank.get(cap, 0) else computed


def licenses(maturity: str) -> dict:
    return {
        "novice":    {"plan_gate_autopass": False, "may_delegate": False, "larger_blast_radius": False},
        "practiced": {"plan_gate_autopass": True,  "may_delegate": False, "larger_blast_radius": False},
        "proven":    {"plan_gate_autopass": True,  "may_delegate": True,  "larger_blast_radius": True},
    }[maturity]


def demote(maturity: str) -> str:
    return {"proven": "practiced", "practiced": "novice", "novice": "novice"}[maturity]

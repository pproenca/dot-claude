#!/usr/bin/env python3
"""The freshness meter — learning whether caching a fact is economically worth it.

Caching is a BET: that the fact is still true when next recalled, and that the work
saved by not re-deriving exceeds the cost of being wrong. The meter measures the
outcome of that bet over a fact's life and lets the MEASURED track record force the
trust/re-derive decision — Cairn does not judge volatility by hand, and is not handed
a list of "volatile knowledge types". It discovers which of its OWN knowledge is
volatile, from its OWN stale-rates, and owns the verdict.

The economics (why the verdict is derived, not authored):
  A FRESH hit saves one re-derivation: value = +D (the derive cost avoided).
  A STALE hit is strictly worse than never caching: you tried the cache, it failed,
  and you re-derive anyway — paying ~k*D (the wasted attempt + the re-derivation;
  k ~= 2 by default, refinable from measured cleanup cost).
  Expected value of caching, per recall:
      EV = fresh_rate*D - stale_rate*(k*D) = D*(fresh_rate - k*stale_rate)
  EV > 0  (cache is worth it)  iff  fresh_rate > k/(1+k)   -> ~0.67 for k=2.
  Below that breakeven, RE-DERIVING UPFRONT is the measurably faster path — which is
  exactly the efficiency reward: avoiding the slow try-fail-redo loop.

The breakeven is not my constant; it falls out of k (the relative cost of a stale
hit), which is transparent and itself refinable from what Cairn measures. The
readings (fresh/stale counts) are entirely Cairn's.
"""
from __future__ import annotations

STALE_COST_K = 2.0  # a stale hit costs ~k x a fresh re-derive (try-fail-redo). Refinable.
MIN_OBSERVED = 3    # below this many recalls, not enough evidence to flip the policy


def breakeven(k: float = STALE_COST_K) -> float:
    """Fresh-rate above which caching has positive expected value."""
    return k / (1.0 + k)


def fresh_rate(uses: int, stale_hits: int) -> float | None:
    if uses <= 0:
        return None
    return (uses - stale_hits) / uses


def cache_ev(uses: int, stale_hits: int, k: float = STALE_COST_K) -> float | None:
    """Expected value of caching this fact, per recall, in units of derive-cost D."""
    fr = fresh_rate(uses, stale_hits)
    if fr is None:
        return None
    sr = 1.0 - fr
    return fr - k * sr


def verdict(entry: dict, k: float = STALE_COST_K, min_observed: int = MIN_OBSERVED) -> dict:
    """The trust policy for a fact, DERIVED from its measured recall outcomes.
    Returns {policy, fresh_rate, ev, basis}. policy is one of:
      'trust'      — caching pays off; recall and use it.
      'verify'     — borderline; recall but confirm before acting.
      're-derive'  — caching is a losing bet here; do not trust the cache, look fresh.
      'unproven'   — too few recalls to judge; trust for now, but watch.
    """
    uses = int(entry.get("uses", 0))
    stale = int(entry.get("stale_hits", 0))
    fr = fresh_rate(uses, stale)
    ev = cache_ev(uses, stale, k)
    be = breakeven(k)
    if uses < min_observed:
        return {"policy": "unproven", "fresh_rate": fr, "ev": ev,
                "basis": f"only {uses} recall(s); need {min_observed} to judge the bet"}
    if fr >= be + 0.15:
        pol = "trust"
    elif fr >= be:
        pol = "verify"
    else:
        pol = "re-derive"
    return {"policy": pol, "fresh_rate": fr, "ev": ev,
            "basis": f"fresh {fr:.0%} over {uses} recalls (breakeven {be:.0%}); "
                     f"caching EV {ev:+.2f}D — {'worth it' if ev > 0 else 'a losing bet'}"}


def record_outcome(entry: dict, fresh: bool) -> dict:
    """Update a fact's recall track record. Returns the mutated entry."""
    entry["uses"] = int(entry.get("uses", 0)) + 1
    if not fresh:
        entry["stale_hits"] = int(entry.get("stale_hits", 0)) + 1
    return entry

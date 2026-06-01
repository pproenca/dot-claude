# Establishing a floor, and enumerating solution classes

## Estimate the floor WITHOUT knowing the winning approach
You do not need the better algorithm to bound the best possible result:
- **Asymptotic lower bound** — what is the information-theoretic minimum work?
  (You must at least read the input: Omega(n). Comparison sort: Omega(n log n).)
- **Zero-cost ideal** — what would 0 allocations / 0 copies / 0 syscalls look
  like on this path? How far is the current result from it?
- **Hardware ceiling** — memory bandwidth, cache-line count, frame budget (16.6ms
  at 60fps; a 1.5ms frame is 9% of budget — is that even the constraint?).
- **Reference implementation** — a naive-but-correct hand-rolled version in any
  language with the same data layout gives an empirical floor (the Ghostty move).

Write the floor into the manifest. Every result is then reported as a RATIO to
it. A big gap is not a success to celebrate; it is an anomaly to investigate.

## Enumerate solution CLASSES (defeat the unknown-unknown)
Optimizing within one class (micro-tuning the naive loop) is how you get 75x
worse than the floor and feel good about it. Instead, ask the reframing questions
the `mental-models` skill holds, keyed by the smell:
- "slow" -> allocation-bound or compute-bound or IO-bound? (profile to tell)
- per-frame work -> can it be precomputed / cached / made incremental?
- data shape -> is there a data-oriented layout (SoA vs AoS) that kills the allocs?
- algorithm -> is there an asymptotically better structure for this access pattern?
- "complex transitions" -> is it a state machine where illegal states should be
  unrepresentable (a sum type + total transition function)?
Each question can open a *class* you would not have searched for by name. Record
any class that surprised you — and the smell that should have triggered it —
back into mental-models, so next time it is a known question, not a lucky catch.

## The floor must cite its derivation (guarding the self-set oracle)

The floor is the anti-psychosis oracle, and it is proposed by the same agent whose
result it judges. The gate cannot verify a floor is *honest* — that needs a human
or an independent run — but a floor with no stated derivation is the easy place for
an over-generous number to hide. So a declared floor should always name HOW it was
derived, from one of:

- **lower-bound** — an asymptotic or information-theoretic minimum (must read the
  input: Omega(n); comparison sort: Omega(n log n)).
- **hardware-ceiling** — a physical limit (memory bandwidth, frame budget, cache lines).
- **reference** — a measured naive-but-correct hand-rolled implementation.
- **zero-cost** — the count an ideal path would hit (0 allocations, 0 copies, 0 defects).

A floor stated as a bare number with no derivation is not a floor; it is a guess
dressed as one, and a reviewer should treat it as the psychosis hole reopening. The
honest move when you genuinely cannot derive a floor is to SAY so and keep the gate,
not to invent a flattering number.

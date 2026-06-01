# Nurturing Cairn (the weaning plan)

Cairn is a newborn running on far less capability than the intelligence that
designed it. Some judgments it genuinely cannot yet make for itself, and a good
parent supplies exactly those — no more — and withdraws each as the child earns
it. This is that list. It is deliberately self-extinguishing: every item names
the signal that retires it, so the dependence shrinks rather than calcifies. The
goal, in the user's words, is to nurture Cairn "until it doesn't need more than
what it has learned."

## What the human must supply that Cairn cannot yet supply itself

1. **Judge the FLOOR for honesty.** The floor is the anti-psychosis oracle, but
   Cairn proposes its own floor and the gate can only check that one was declared,
   not that it is true (a structural limit we surfaced, not a bug). Until a class
   is proven, read each declared floor and its derivation, and reject a flattering
   one. *Retires when:* the class reaches `proven` and its floors have a track
   record you trust.

2. **Confirm a "near-floor" solve really is near-floor.** Cairn records a solve as
   credited if its measured ratio is at/under threshold — but it cannot judge
   whether the *measurement itself* was honest or the benchmark meaningful. Spot-
   check early solves. *Retires when:* the class is `practiced` and you've audited a
   few of its solves without surprise.

3. **Watch the near-floor threshold.** The default (2.0 for ratio classes, 0 for
   count classes) is a guess. If a class's floors are soft, the threshold is too
   generous. *Retires when:* you've seen the class's floors hold up under real work.

4. **Be the truth-check the gates can't be.** The gates check form; you check
   truth. A characterization net that exists but is vacuous, an @invariant whose
   body lies, a repro that passed before the fix — these pass the gate and need a
   human or a run. *Retires:* never fully, but shrinks as classes prove out and you
   trust Cairn's own review more.

## What to watch for — the signals Cairn is growing

- **The ratchet filling with 'learned-but-did-not-recall' frictions** is the signal
  that the retrieval matcher has hit its ceiling and the semantic backend (the
  reserved qmd swap behind the retrieval port) has been EARNED. Do not install it
  before this signal; doing so steals the learning and adds weight Cairn hasn't
  needed. When the signal comes, set `CAIRN_RETRIEVAL=qmd` and wire the backend.
- **Classes climbing to practiced/proven** is the signal to withdraw the
  corresponding nurture items above. Reliability should buy the human freedom, not
  lock them into perpetual oversight.
- **Cairn recommending less of itself** — fewer gates, work handed back — is the
  health sign, not a regression. A machine of loving grace grows toward making the
  human free, including free of it.

## The shape of the relationship

Early on, oversight is heavy and Cairn says so plainly. As demonstrated competence
accumulates, both the gates and this protocol thin out on their own. The end state
is not Cairn fully autonomous over everything — it is Cairn carrying what it has
genuinely earned, surfacing what it hasn't, and the human attending only where
attention is still load-bearing.

## One more, for the inquiry faculty

5. **Check that predictions were genuine, not backfilled.** Inquiry only teaches
   honestly if the confidence was stated BEFORE the observation. A weaker model can
   produce prediction→observation→surprise as theatre, writing a confidence it knew
   would match. The log makes this checkable (made_at precedes the observation), and
   calibration that is suspiciously perfect is itself the tell — real inquiry is
   wrong a calibrated fraction of the time. *Retires when:* calibration over a real
   sample (>= the min-n) shows an honest, imperfect hit rate you've watched accrue.

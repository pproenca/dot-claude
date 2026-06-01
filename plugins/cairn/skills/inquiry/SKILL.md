---
name: inquiry
description: >-
  When you catch yourself ASSUMING how something works — guessing a repo's stack,
  asserting where code lives, feeling sure without having looked — that noticing
  is the signal for this. It is the faculty for acting well under not-knowing:
  the disciplined interrogation of your own ignorance, made measurable. Use this at the BLANK MOMENT before a
  problem is even named: a new repo, unfamiliar terrain, "I don't know what I
  don't know here." Instead of guessing or freezing, state a PREDICTION with a
  confidence BEFORE observing, make the cheapest observation that would falsify
  it, then record the SURPRISE (how wrong a confident belief turned out). A
  high-confidence miss is a significant surprise that teaches a mental-model; a
  hedged miss is noise. Over many predictions it tracks CALIBRATION — whether
  stated confidence matches actual hit rate — as the measurable proxy for whether
  Cairn's judgment can yet be trusted.
---

# Inquiry — acting well under not-knowing

The skills elsewhere assume the unknown is already named and turned into a test.
This is the faculty for the moment BEFORE that: the fog, where you do not yet know
what question to ask. A capable agent in unfamiliar terrain neither guesses nor
freezes — it runs a loop it can state precisely: predict, observe the surprise,
update. This skill makes that loop measurable, so it becomes critical thinking
rather than narration.

## Why measurable, and why it is not novel
Statistical significance was not a discovery about the world; it was a decision
rule under uncertainty — a threshold that separates "I observed something" from "I
observed something that should change my belief." Before it, hunches and
confirmation bias; after it, a framework. This skill is that move applied to the
agent's own understanding: a way to measure whether a surprise is *real* — large
enough, against what was expected, to update on — and whether the agent's
confidence can be trusted at all.

## The loop (state a prediction BEFORE you look)
1. **Predict.** Before observing, state a claim about the terrain AND a confidence
   (0-1). The confidence must be recorded before the observation — a prediction
   backfilled after looking is not a prediction, it is a rationalization, and the
   log is built to make that visible.
2. **Falsify cheapest-first.** Make the single cheapest observation that would most
   change the picture if the prediction is wrong. Try hardest to KILL your own
   prediction, not to confirm it — confirmation-seeking is the psychosis of
   understanding, the belief-level twin of judging a result against your own
   baseline instead of the floor.
3. **Record the surprise.** Surprise magnitude = confidence × wrongness. A
   confident claim that was wrong scores high (significant — it must teach); a
   hedged claim that was wrong scores low (expected — noise). This is the
   threshold that separates a lesson from a shrug.
4. **Teach.** A surprise above threshold feeds `mental-models` with a reframing
   whose authority is "a confident prediction was wrong" — the belief-level analogue
   of a result far from floor. The reframe is what would have predicted better.
5. **Narrow.** The sharpened picture makes the next prediction better, until the
   fog has a shape you can name as a problem — at which point the change-kind spine
   takes over.

## Calibration — the measurable proxy for trustworthy judgment
Across many predictions, bucket them by stated confidence and compare to the actual
hit rate. If Cairn says 80% and is right ~80% of the time, it is CALIBRATED — its
intuitions can be trusted. If it says 80% and is right 50%, it is OVERCONFIDENT — a
measurable defect that should keep its gates up. Calibration is the empirical
self-trust signal: not "did I solve it" but "were my beliefs honest about their own
uncertainty."

Calibration is ADVISORY until the sample is large enough to mean anything — the
skill refuses to report it as meaningful below a minimum N, the way a scientist
will not quote significance on three data points. Computing self-trust from noise
would be the exact "competence declared, not demonstrated" failure the capability
ledger forbids. When the sample is real, calibration MAY later become licensing
evidence — built then, on evidence, not now in anticipation.

## Cairn builds its own version
The thresholds and confidence buckets start as defaults but are recalibrated from
Cairn's OWN history: if its 70% bucket consistently hits 85%, the framework learns
Cairn runs underconfident and adjusts. The empirical lens is applied to the lens.
Over many repos, the accumulated record of "what I confidently believed that turned
out wrong, and what corrected me" IS Cairn's critical thinking — unique to its
history, not inherited. The framework is given; the conclusions are earned.

## The one law here
A prediction's confidence is stated before the observation, or it does not count.
Honesty about uncertainty is the whole faculty; a prediction that cannot be wrong
teaches nothing, and a confidence retrofitted to match the answer is the lie this
skill exists to make measurable.

## Files
- `references/predicting.md` — how to state a falsifiable prediction and pick the
  cheapest observation.
- `scripts/store.py` — the prediction-log port (JSONL).
- `scripts/predict.py` — log a prediction + confidence BEFORE observing.
- `scripts/observe.py` — record the outcome, compute surprise, feed mental-models.
- `scripts/calibration.py` — report calibration (or refuse, below minimum N).

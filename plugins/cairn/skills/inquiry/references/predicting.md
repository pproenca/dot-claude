# Stating a falsifiable prediction, and choosing the cheapest observation

The faculty is only as good as the prediction. A vague prediction cannot be
surprised, and a prediction with no confidence cannot be calibrated.

## A good prediction
- **Specific enough to be wrong.** "The auth is probably fine" cannot be falsified.
  "Input is validated at the controller, not the service" can.
- **Carries a confidence (0-1), stated before looking.** The confidence is the
  whole measurable part. Be honest: a hunch is 0.6, not 0.9.
- **Is about the terrain, not yourself.** "I predict the repo uses Zod at the trust
  boundary" — a claim reality can contradict.

## Choosing the cheapest falsifying observation
You are not trying to understand everything; you are trying to kill THIS prediction
as cheaply as possible. Ask: what single look would most change my picture if I am
wrong?
- Prefer one file read over a whole-repo scan.
- Prefer the observation that DISCRIMINATES between your prediction and its most
  likely alternative, not one that merely fits your prediction.
- Confirmation is cheap and worthless; falsification is the point. If you find
  yourself looking for evidence you are right, stop — that is the belief-level
  version of grading a result against your own baseline.

## After the look
Record the outcome honestly: right / wrong / partial. The surprise is computed for
you (confidence × wrongness). A confident miss is the signal to learn — it means a
model was missing. Write the reframe: what would have predicted correctly? That is
the mental-model the surprise earned.

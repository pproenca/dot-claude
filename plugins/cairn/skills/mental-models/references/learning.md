# Turning a gap into a recorded model

A model is earned, not invented. The trigger to record one is a **gap**: a result
far from its floor, or a post-hoc discovery that a whole class of approach was
missed. The gap is the authority.

## Procedure
1. **Name the smell.** What symptom *should* have triggered a better question?
   Make it the symptom you'll actually notice next time: "150K allocations per
   frame", "O(n^2) over a list that grows", "I compared to my own baseline".
2. **Extract the reframe.** The question that opens the door: "allocation-bound
   or compute-bound?", "is there a data-oriented layout?", "what's the floor?".
   The reframe must be *transferable* — useful beyond this exact problem.
3. **List the solution CLASSES it opens** — distinct approaches, not tweaks within
   one. (For "allocation-bound": arena/pool allocation, SoA layout, reuse buffers,
   avoid boxing — each a different class.)
4. **Record the provenance.** What gap taught this? Keeping `taught_by_gap` makes
   the catalog honest: every model traces to a real surprise, not speculation.
5. **Keep it horizontal.** If the lesson is "this RN API is faster", that's
   specialist-knowledge. If it's "per-frame work should be incremental/cached",
   that's a transferable model — it belongs here.

## Then it compounds
Next time the smell appears, `models_lookup.py --smell` surfaces the reframe
*before* you commit — so the class you once missed is now a question you always
ask. That is the monotonic climb: unknown-unknown -> known-unknown -> known-known.

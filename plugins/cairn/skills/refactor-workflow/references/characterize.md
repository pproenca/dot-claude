# Capturing a characterization net

The goal is not coverage; it is to **parse the current behavior into something
trusted** so you can change structure without silent regression.

## Procedure
1. **Identify the observable surface** — the public outputs/contracts that must
   not change (return values, emitted events, rendered output, side effects at
   the rim). Internals are explicitly NOT pinned; that is what you are free to move.
2. **Pin it at the seam, not the internals.** Test through the stable interface
   so the net survives the refactor. A net that tests internals breaks when you
   move them and proves nothing about behavior.
3. **Run it GREEN first.** Green-before-touch is the proof the net captures
   *actual* current behavior. A net written after the change can be vacuously
   green — the same reason an unverified test proves nothing.
4. **Golden-master for wide surfaces.** For complex output (rendered frames,
   serialized trees), snapshot the current output as the oracle.
5. **Property tests for invariants.** Where behavior is "for all inputs, P
   holds", a property test pins more than examples can.

## Then change under it
Refactor one move at a time, re-running the net each move. The net green after =
behavior preserved. If it goes red, the last move changed behavior — revert and
reconsider; do not "update the test to match", that discards the spec.

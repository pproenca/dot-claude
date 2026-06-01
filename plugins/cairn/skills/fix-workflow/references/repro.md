# Writing a repro that fails for the right reason

The repro is the trust boundary of a fix: it parses "this is broken in way Y"
into a trusted, permanent artifact.

## Procedure
1. **Reproduce at the boundary that owns the behavior**, through the stable
   interface — not by poking internals. The repro must still make sense after
   the fix.
2. **Make it FAIL first, for the stated reason.** Read the failure: does it fail
   because of *this* bug, or something else? A repro that passes before the fix
   proves nothing; a repro that fails for the wrong reason fixes the wrong thing.
3. **Minimize.** The smallest input that triggers the bug isolates the cause and
   becomes a fast, durable regression test.
4. **Root cause, not symptom.** Trace to the boundary that violated its
   invariant. Fix there. If the right home is a missing invariant, this fix may
   feed a `knowledge-ratchet` promotion (annotation -> enforced -> type).
5. **Keep it.** The repro stays in the suite as the regression lock. That is what
   converts "fixed once" into "cannot recur silently".

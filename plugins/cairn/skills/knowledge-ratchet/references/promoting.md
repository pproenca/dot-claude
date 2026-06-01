# Promoting a friction

A ripe friction earns a *durable* fix — one that stops it recurring without
anyone remembering to watch for it. Choosing the right sink is the whole skill.

## First: is it a defect or an abstraction?

- **Defect** — something is just wrong (a scanner false-positive, a flaky check,
  a misleading message). Fix on sight; one occurrence is enough. The Rule of
  Three does not apply — waiting for a defect to recur twice more is silly.
- **Abstraction** — a candidate generalization (extract a shared primitive, add
  a lint rule, write a new skill). Gated by the Rule of Three. Two uses is a
  coincidence; three is a pattern. Promoting earlier risks fitting the
  abstraction to one case and paying for it on every later one.

## Then: pick the leftmost durable sink

This is the maturity ladder (from boundary-discipline) applied to process
learning — prefer the fix that needs the least vigilance:

1. **type-constraint** — make the bad state unrepresentable (a union, a branded
   type, a clamp). Strongest: the compiler enforces it, nobody has to remember.
2. **scan-pattern / lint-rule** — automated detection. The machine flags
   recurrence; humans don't police it. (A scanner false-positive is fixed *here*
   — tighten the pattern.)
3. **reference** — durable written guidance inside the relevant skill, so the
   next agent reads it in context.
4. **convention** — a line in the repo's `AGENTS.md` "Repo conventions &
   learnings" section. Weakest (documentation only), but the right home for
   repo-specific judgment that can't be mechanized.

Prefer higher on the list. A convention that could have been a lint rule will be
ignored; a lint rule that could have been a type will be worked around.

## Repo-local or federation skill?

A friction that is **specific to this project** (its design-system conventions,
its domain quirks) promotes to a repo-local sink — `AGENTS.md` or a reference in
the repo — *not* a new federation skill. Minting a skill for project-specific
guidance is skill-sprawl; the federation is for cross-project capabilities.

A friction that is a **reusable, cross-project capability** (a whole missing kind
of work — like the ecosystem trust boundary that became `library-knowledge`) is
the rare case that justifies a new skill. Apply the same VENDOR-style cost test:
a new skill is a new maintenance surface; it earns its place only when the
capability is genuinely general.

## Record it

`ratchet.py --promote <key> --as <sink> --landed <where>` closes the friction and
notes where the fix lives, so the log shows not just what recurred but what was
done about it — the audit trail of the harness improving itself.

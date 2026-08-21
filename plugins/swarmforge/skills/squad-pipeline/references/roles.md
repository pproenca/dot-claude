# Role ownership

Each agent owns exactly one artifact and one concern. The value of the pipeline is
the separation; collapsing two roles into one agent defeats it.

| Agent | Writes | Never writes | Hands back |
|---|---|---|---|
| analyst | `plan.md` | code, tests, Gherkin, sibling stories | plan |
| gherkin-writer | `<story-id>.feature` | code, tests, plans | feature file |
| qa-procedure-writer | `qa-procedure.md`, `implementer-notes.md` | code, tests, Gherkin | both, one commit |
| implementer | production code + unit tests | reviews, refactors beyond the story, tooling manifests | commit + verify output |
| cleaner | refactors, added coverage | new behavior, new public API | commit + verify output |
| code-reviewer | `review.md` | any source file | recommendations only |
| hardener | code changes applying review recs, then edge-case tests | new features | commit + verify output |
| qa-runner | `qa-result.md` | production code | pass/fail per procedure step |
| architect | `architecture.md` | any source file | recommendations only |
| senior-implementer | code applying architect recs | new behavior | commit + verify output |

## Invariants every agent obeys

- Implement or describe **this story alone**. Behavior owned by another backlog item
  is a port: name it, stub it, do not build it.
- Read `.squad/constitution.md` before writing anything. It carries the project's
  real language, test command, and house rules.
- Run `verify.test` when the role touched executable code. Report the command and
  its result verbatim. Never claim a pass that was not observed.
- Hand back to the main session only. Never dispatch another agent.
- When the assignment cannot be done honestly, hand back a blocker naming the
  single specific obstacle, rather than widening scope or inventing state.

## Recommendation-only roles

`code-reviewer` and `architect` are read-only by contract. They produce a numbered
list of recommendations, each with a file path, a severity, and a concrete change.
A separate role applies them — hardener for review recommendations,
senior-implementer for architecture recommendations. This is what stops a reviewer
from quietly rewriting the thing it was meant to judge.

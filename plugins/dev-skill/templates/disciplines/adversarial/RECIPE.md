# Adversarial Recipe

Adversarial turns a rule set into a **pass/fail gate**: two blind, identical reviewer subagents independently judge a piece of work against the rules, and the work passes only if both say PASS. It is the method for **Adversarial Review** skills.

Start from this premise: **a single reviewer with conversation context is biased toward passing.** It saw the work being made, it wants to be helpful, and it grades on effort. The gate removes both failure modes: reviewers are blind (self-contained prompt, no conversation history) and redundant (two independent verdicts must agree on PASS). Disagreement is signal, not noise — it means the verdict was not stable, and an unstable PASS is a FAIL.

## What adversarial produces

```
{skill-name}/
├── SKILL.md                  # Entry point: when to apply + the review protocol
├── metadata.json             # discipline: "adversarial", type: "adversarial-review"
├── references/
│   ├── _sections.md          # Category definitions        ┐ owned-rules mode
│   ├── {prefix}-{slug}.md    # Rules, distillation format  ┘
│   ├── rules-source.md       # Pointer to the source skill — companion mode
│   └── reviewer-prompt.md    # The self-contained prompt each reviewer receives
├── assets/templates/
│   └── verdict.md            # Verdict report template
└── gotchas.md
```

Exactly one of the two rule modes exists per skill:

| Mode | When | Rules live in |
|------|------|---------------|
| **Owned rules** | No existing distillation skill covers the domain | `references/{prefix}-{slug}.md`, derived fresh (same format and doctrine as distillation) |
| **Companion** | A distillation skill already holds the rules | The source skill; `references/rules-source.md` records its path and the checkable subset |

Companion mode references rules by path rather than copying them, so the gate stays in sync as the source skill evolves. The cost: if the source skill is missing at review time, the protocol must **fail loudly — never silently pass**. `rules-source.md` records the source path, version, and date so drift is detectable.

## The one test that matters: is the rule decidable?

Distillation asks "what wrong default does this rule correct?" Adversarial asks a stricter question: **can a reviewer decide PASS or FAIL from evidence in the artifact alone?** Apply it to every candidate rule:

1. **What evidence would prove a violation?** Name it: a file, a line, a missing test, a query without an index. If you cannot name the evidence, the rule is not checkable.
2. **Would two competent reviewers, given the same artifact, reach the same verdict?** "Prefer small functions" splits reviewers; "no function over 80 lines touches the database and the network" does not. Judgment calls make the gate flaky — every contested verdict traces back to an undecidable rule.
3. **Is the rule still a rule?** Decidability doesn't excuse hand-holding. A check the model never fails is dead weight in every review; cut it.

An undecidable rule is not deleted knowledge — it belongs in a distillation skill, where it teaches. The gate keeps only what it can enforce.

**No rule-count target.** The set of decidable, actually-violated checks *is* the scope. In companion mode this means filtering: import only the source rules that pass the decidability test, and list the exclusions with reasons in `rules-source.md` so the gap is visible rather than silent.

## The reviewer prompt: self-contained or worthless

`references/reviewer-prompt.md` is the heart of the skill. Both reviewers receive it verbatim — same prompt, same rules, same target. Its requirements:

- **Self-contained.** The composed prompt carries everything: the rules (inline or as file paths to read), the review target, the output format. A reviewer that needs conversation context is not blind.
- **Adversarial stance.** Instruct the reviewer to hunt for violations, not to confirm compliance. The default posture is skepticism.
- **Evidence both ways.** A FAIL cites the violating evidence (`file:line` or a quote). A PASS cites what was checked — an evidence-free PASS is a rubber stamp and the prompt must forbid it.
- **Verdict only.** The reviewer reports; it never fixes. Mixing repair into review contaminates the verdict.
- **Structured output.** Per-rule `PASS | FAIL | N/A`, evidence, and — for every FAIL — what is missing to reach PASS. The dispatching agent must be able to merge two of these mechanically.

## Merging verdicts: fail-closed

| Reviewer A | Reviewer B | Final verdict |
|-----------|-----------|---------------|
| PASS | PASS | **PASS** |
| FAIL | FAIL | **FAIL** |
| PASS | FAIL (either order) | **FAIL**, rule marked **CONTESTED** |

N/A splits: N/A vs N/A → N/A; N/A vs PASS → PASS; N/A vs FAIL → CONTESTED (counts as FAIL — one reviewer found the rule applicable *and* violated).

- Overall verdict is PASS only when both reviewers' overall verdicts are PASS.
- A contested rule counts as FAIL — the failing reviewer saw something; the burden is on the work to make the verdict unanimous. Both rationales are shown so the human can judge whether the rule itself is flaky.
- Recurring contested verdicts on the same rule are a decidability bug. Fix the rule, don't override the gate. Record the pattern in `gotchas.md`.

## Suggestions, not lectures

Every FAIL must name **the missing change and where it goes** — "add a `context.Context` parameter to `FetchInvoices` and thread it into the HTTP call (`billing/client.go:41`)", not "improve context handling". The verdict report aggregates these into a fix list ordered by category importance, so a failed review is directly actionable. A FAIL without a suggestion is a validation error, not a style choice.

## Generation workflow

1. **Rule source** — ask the user: derive fresh rules, or build a companion to an existing distillation skill (get its path and read it).
2. **Derive or filter** — *fresh:* distillation-style research, but every rule must also pass the decidability test. *Companion:* apply the decidability test to each source rule; keep the checkable subset, record exclusions with reasons.
3. **Planning checkpoint** — show categories, each rule's evidence-of-violation, mode, and (companion) the excluded rules; get approval.
4. **Generate** — rules or `rules-source.md` → `reviewer-prompt.md` → `assets/templates/verdict.md` → `SKILL.md` → `metadata.json` → `gotchas.md`.
5. **Validate** — `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-dir}`, then the `skill-reviewer` agent with this discipline's `RUBRIC.md`.
6. **Prove** — dry-run the gate on a real artifact that should FAIL and one that should PASS. A gate that has never failed anything is unproven; a contested verdict on the dry run means a rule needs sharpening before release.

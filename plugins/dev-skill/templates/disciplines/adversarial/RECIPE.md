# Adversarial Recipe

Adversarial turns a rule set into a **pass/fail gate**: a single blind reviewer subagent, dispatched with an adversarial mandate, judges a piece of work against the rules. It is the method for **Adversarial Review** skills.

Start from this premise: **a reviewer with conversation context is biased toward passing.** It saw the work being made, it wants to be helpful, and it grades on effort. The gate removes this with blindness and stance, not redundancy: the reviewer gets a self-contained prompt with no conversation history, an explicit mandate to hunt for violations, and an evidence requirement in both directions (an evidence-free PASS is forbidden). With no second reviewer to catch a flaky verdict at runtime, verdict stability rests entirely on **rule decidability** — which is why the decidability test below is the heart of the discipline, and why unstable verdicts in the field are treated as rule bugs, never as noise.

## What adversarial produces

```
{skill-name}/
├── SKILL.md                  # Entry point: when to apply + the review protocol
├── metadata.json             # discipline: "adversarial", type: "adversarial-review"
├── references/
│   ├── _sections.md          # Category definitions        ┐ owned-rules mode
│   ├── {prefix}-{slug}.md    # Rules, distillation format  ┘
│   ├── rules-source.md       # Pointer to the source skill — companion mode
│   └── reviewer-prompt.md    # The self-contained prompt the reviewer receives
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
2. **Would two competent reviewers, given the same artifact, reach the same verdict?** This is a thought experiment applied at authoring time, not a runtime mechanism — the gate dispatches one reviewer, so an undecidable rule has no disagreement signal to expose it; it just produces verdicts that flip between runs. "Prefer small functions" splits reviewers; "no function over 80 lines touches the database and the network" does not. Every unstable verdict traces back to an undecidable rule.
3. **Is the rule still a rule?** Decidability doesn't excuse hand-holding. A check the model never fails is dead weight in every review; cut it.

An undecidable rule is not deleted knowledge — it belongs in a distillation skill, where it teaches. The gate keeps only what it can enforce.

**No rule-count target.** The set of decidable, actually-violated checks *is* the scope. In companion mode this means filtering: import only the source rules that pass the decidability test, and list the exclusions with reasons in `rules-source.md` so the gap is visible rather than silent.

## The gate reviews frozen targets — never moving ones

The gate family's worst field failure (July 2026, three sessions on a production iOS app) was not bad verdicts — it was gates dispatched as *cleanup drivers* on code that kept changing. Reviews were started, discarded when the target moved, and restarted; zero verdicts were rendered across ~11 hours while the diff ballooned to 33 files and commit discipline collapsed into 90–162-file opaque sweeps. Every generated SKILL.md must therefore carry two dispatch preconditions:

1. **Frozen target.** Dispatch only against a fixed ref (commit SHA, stash, saved diff) recorded as a target manifest. A target change mid-review voids the run, and the void is *recorded* (`GATE VOID — target changed`) — a dispatched gate always ends in a rendered verdict, a `GATE NOT APPLICABLE`, or a recorded void, never silence. Silence is indistinguishable from "reviewed", which is how ungated work ships.
2. **Verdicts, not cleanup.** The gate is a terminal check on finished work; "run the gate and fix everything aggressively" inverts the contract. After a FAIL, fixes stay inside the original target, and the re-gate runs a fresh blind review against the **same manifest** — the reviewable surface never widens between rounds. An elastic surface plus fail-closed reruns never converges (the field case burned ~10 rerun cycles and ~100M tokens without reaching PASS).

Two operational corollaries: the reviewer reads rules from an immutable snapshot (`git archive`) when other agents may be mutating the workspace, and skill directories are read-only infrastructure excluded from every cleanup scope (a parallel "cleanup" subagent once deleted the vendored gate wholesale mid-review).

## Rules that judge cost need a materiality leg

A performance or efficiency rule without a materiality predicate becomes a treadmill: every `.reduce` on the main actor is *individually* defensible to flag, so successive reviews keep relocating the boundary until a scoped review has driven an app-wide rearchitecture. The evidence-of-violation for any cost-based rule must include **why the input is large at the target's real data scale** (an unbounded collection cited via its loading site); small, bounded-by-construction inputs are N/A, not FAIL. Relatedly: a fix that satisfies a rule's letter through an unsafe escape hatch (`@unchecked Sendable`, `any`, suppressions) does not flip the rule — say so in the rule text.

## Rules that judge runtime behavior need rendered evidence

A rule about motion, gestures, or interaction feel that is decided from code alone turns the gate into a generator: "absence of `withAnimation`" FAILs once produced a fix list that sprayed 32 templated animation calls across 18 files. For gates whose subject renders (UI, motion, interaction): make evidence capture a mandatory protocol step (screenshots, recordings, filmstrips) with a **capability preflight before dispatch**; let code alone *nominate candidates reported as N/A* — never FAIL, never PASS; and for gesture-driven interactions require **repeated trials in one session** (≥3 consecutive) because recognizer arbitration fails intermittently — a single green run is not evidence. The `adversarial-ios-design` skill in dot-skills is the proven reference implementation of this pattern.

## The reviewer prompt: self-contained or worthless

`references/reviewer-prompt.md` is the operative artifact of the skill. The reviewer receives the composed prompt verbatim, and it is the reviewer's entire world. Its requirements:

- **Self-contained.** The composed prompt carries everything: the rules (inline or as file paths to read), the review target, the output format. A reviewer that needs conversation context is not blind — and blindness is the gate's whole defense against pass bias, so this requirement has no exceptions.
- **Adversarial stance.** Instruct the reviewer to hunt for violations, not to confirm compliance. The default posture is skepticism.
- **Evidence both ways.** A FAIL cites the violating evidence (`file:line` or a quote). A PASS cites what was checked — an evidence-free PASS is a rubber stamp and the prompt must forbid it.
- **Verdict only.** The reviewer reports; it never fixes. Mixing repair into review contaminates the verdict.
- **Structured output.** Per-rule `PASS | FAIL | N/A`, evidence, and — for every FAIL — what is missing to reach PASS. The dispatching agent must be able to render the final verdict from it mechanically.

## Fail-closed without redundancy

There is no merge step: the reviewer's structured output *is* the verdict. Overall verdict is PASS only when every rule is PASS or N/A; any single FAIL fails the gate. The reviewer never averages, weighs severity, or waives a rule — a "minor" FAIL is a FAIL.

Redundancy used to catch flaky verdicts at runtime; without it, instability must be caught two other ways:

- **At authoring time** — the decidability test. Every rule that survives generation must name the evidence that decides it.
- **In the field** — the instability signal. If the same rule flips verdicts across re-reviews of an unchanged target, or a human reads the evidence and overrides the verdict, that is a decidability bug in the rule. Fix the rule, don't override the gate. Record the pattern in `gotchas.md`.

## Suggestions, not lectures

Every FAIL must name **the fix that flips the rule to PASS once applied** — "add a `context.Context` parameter to `FetchInvoices` and thread it into the HTTP call (`billing/client.go:41`)", not "improve context handling" and never a restatement of the violation. The verdict report aggregates these into a fix list ordered by category importance, so a failed review is directly actionable. A FAIL without a flip-test fix is a validation error, not a style choice.

But frame the fix list as **verification material, not a work queue** — a FAIL list that reads like a task list invites callers to use the gate as a rewrite engine. Every fix is the *minimal* change that flips its rule (removal preferred over addition, nothing beyond the rule's named remedy), it stays inside the declared target, and anything the reviewer noticed outside the target lands in an out-of-scope observations section — reported, never fixed, never counted.

## Generation workflow

1. **Rule source** — ask the user: derive fresh rules, or build a companion to an existing distillation skill (get its path and read it).
2. **Derive or filter** — *fresh:* distillation-style research, but every rule must also pass the decidability test. *Companion:* apply the decidability test to each source rule; keep the checkable subset, record exclusions with reasons.
3. **Planning checkpoint** — show categories, each rule's evidence-of-violation, mode, and (companion) the excluded rules; get approval.
4. **Generate** — rules or `rules-source.md` → `reviewer-prompt.md` → `assets/templates/verdict.md` → `SKILL.md` → `metadata.json` → `gotchas.md`.
5. **Validate** — `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-dir}`, then the `skill-reviewer` agent with this discipline's `RUBRIC.md`.
6. **Prove** — dry-run the gate on a real artifact that should FAIL and one that should PASS. A gate that has never failed anything is unproven; a dry-run verdict that doesn't match the expected outcome, or that you cannot defend from the cited evidence alone, means a rule needs sharpening before release.

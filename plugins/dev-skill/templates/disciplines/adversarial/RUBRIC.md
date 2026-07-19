# Adversarial Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Rule Decidability (check every rule the gate enforces)

For each rule (in `references/` for owned-rules mode, or the imported subset listed in `references/rules-source.md` for companion mode):

1. **Evidence named.** Can you state what artifact evidence would prove a violation (a file, a line, a missing test, a pattern)? If no concrete evidence is nameable, the rule is undecidable — flag it.
2. **Verdict stability.** Would two competent reviewers given the same artifact reach the same PASS/FAIL? (This is an authoring-time thought experiment — the gate runs a single reviewer, so an unstable rule has no runtime disagreement signal to expose it.) Flag rules that hinge on taste words ("clean", "appropriate", "reasonable", "prefer") without a measurable boundary.
3. **Not dead weight.** Is this a check a capable model's output could actually fail? A rule that always passes is hand-holding; flag it for removal.
4. **Materiality on cost rules.** For any rule judging performance or efficiency: does its evidence-of-violation require citing why the input is large at real data scale (unbounded collection via its loading site), with small bounded inputs N/A? A cost rule without a materiality leg drives refactor treadmills — flag it.
5. **Rendered evidence on runtime-behavior rules.** For any rule judging motion, gestures, or interaction feel: does the rule require rendered evidence (recording/filmstrip) to FAIL, with code alone only nominating N/A candidates? A code-decidable motion rule turns the gate into an animation generator — flag it.

Record each finding: rule file, check performed, result (PASS/FAIL).

## Reviewer Prompt (references/reviewer-prompt.md)

1. **Self-containment.** Does the prompt (once composed with rules + target) carry everything a reviewer needs? Flag any reference to conversation context, prior discussion, or "as described above".
2. **Adversarial stance.** Does it instruct the reviewer to hunt for violations rather than confirm compliance?
3. **Evidence required both ways.** Does it require evidence for PASS as well as FAIL? An evidence-free PASS must be forbidden explicitly.
4. **Verdict only.** Does it forbid the reviewer from fixing or rewriting the work?
5. **Structured output.** Does it specify per-rule `PASS | FAIL | N/A` plus overall verdict, in a format the dispatcher can render into the verdict report mechanically? For every FAIL, does it require "what is missing to reach PASS"?

## Review Protocol (SKILL.md)

1. **One blind reviewer.** Does the protocol dispatch a single subagent whose composed prompt is its entire input — no conversation context, no commentary alongside it? Flag any design where the reviewer can see the work being made or discussed.
2. **Fail-closed verdict.** Overall PASS requires every rule to be PASS or N/A; any single FAIL fails the gate, with no severity-weighing or waiving. Is this stated unambiguously?
3. **Instability surfacing.** Does the protocol treat verdict instability (the same rule flipping across re-reviews of an unchanged target, or a human overriding a verdict) as a decidability bug to record in gotchas.md and fix in the rule — never by overriding the gate?
4. **Actionable failure.** Does the protocol require the final report to aggregate per-FAIL "missing for PASS" suggestions with locations?
5. **Companion-mode loud failure.** (Companion mode only) If the source skill path is missing or unreadable at review time, does the protocol stop with an error rather than pass or skip? Is the source path + version recorded in `rules-source.md`, with excluded rules listed with reasons?
6. **Frozen-target preconditions.** Does the protocol refuse to dispatch against a moving target (fixed ref recorded as a target manifest), void the run when the target changes mid-review, and require every dispatched gate to end in a rendered verdict, GATE NOT APPLICABLE, or a recorded void — never silence?
7. **Fix-scope contract.** Does the protocol state that the gate is a terminal check (not a cleanup driver), that fixes stay inside the declared target, that the re-gate uses the same target manifest without widening, and that out-of-target findings are reported but never fixed?

## Verdict Template (assets/templates/verdict.md)

1. **Per-rule table.** Rule, verdict, evidence — evidence present for PASS rows as well as FAIL rows.
2. **Overall verdict.** A single unambiguous PASS/FAIL line, PASS only when every rule is PASS or N/A.
3. **Fix list.** A section for aggregated suggestions on FAIL, ordered by category importance, with the completeness (every FAIL rule appears with an apply-as-written change) and minimality (smallest change that flips the rule, no escape hatches) requirements stated.
4. **Status header.** Target manifest (frozen ref) and gate status (RENDERED / NOT APPLICABLE / VOID — reason) fields present.
5. **Gotchas enforcement.** An instruction that unstable or overridden verdicts get an entry appended to gotchas.md naming the rule and the ambiguity.
6. **Out-of-scope section.** A place for violations outside the target manifest, marked report-only.

## Usefulness Assessment

1. **Gate value.** Is this domain one where a wrong PASS is costly enough to justify a reviewer dispatch per check? If a single linter rule or script could decide every rule deterministically, the skill should be a script, not a reviewer gate — flag it.
2. **Proven both ways.** Is there evidence (dry run, gotchas entry) that the gate has both passed a good artifact and failed a bad one? A gate that has never failed anything is unproven.

## Verdict

- **SHIP**: Every enforced rule is decidable with nameable evidence. Reviewer prompt is self-contained, adversarial, evidence-both-ways, structured. Verdict is fail-closed with instability routed to gotchas. Failures produce located, actionable suggestions. Companion mode fails loudly.
- **NEEDS WORK**: Protocol sound but some rules undecidable or dead weight, or the prompt allows evidence-free PASS, or suggestions lack locations. Specific fixes identified.
- **REJECT**: Context-contaminated reviewer design (the reviewer sees conversation history or the work being made), verdict not fail-closed, companion mode can silently pass without its source, or the majority of rules are judgment calls.

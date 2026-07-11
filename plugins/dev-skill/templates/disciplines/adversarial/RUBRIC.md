# Adversarial Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Rule Decidability (check every rule the gate enforces)

For each rule (in `references/` for owned-rules mode, or the imported subset listed in `references/rules-source.md` for companion mode):

1. **Evidence named.** Can you state what artifact evidence would prove a violation (a file, a line, a missing test, a pattern)? If no concrete evidence is nameable, the rule is undecidable — flag it.
2. **Verdict stability.** Would two competent reviewers given the same artifact reach the same PASS/FAIL? Flag rules that hinge on taste words ("clean", "appropriate", "reasonable", "prefer") without a measurable boundary.
3. **Not dead weight.** Is this a check a capable model's output could actually fail? A rule that always passes is hand-holding; flag it for removal.

Record each finding: rule file, check performed, result (PASS/FAIL).

## Reviewer Prompt (references/reviewer-prompt.md)

1. **Self-containment.** Does the prompt (once composed with rules + target) carry everything a reviewer needs? Flag any reference to conversation context, prior discussion, or "as described above".
2. **Adversarial stance.** Does it instruct the reviewer to hunt for violations rather than confirm compliance?
3. **Evidence required both ways.** Does it require evidence for PASS as well as FAIL? An evidence-free PASS must be forbidden explicitly.
4. **Verdict only.** Does it forbid the reviewer from fixing or rewriting the work?
5. **Structured output.** Does it specify per-rule `PASS | FAIL | N/A` plus overall verdict, in a format the dispatcher can merge mechanically? For every FAIL, does it require "what is missing to reach PASS"?

## Review Protocol (SKILL.md)

1. **Two blind reviewers.** Does the protocol dispatch exactly two subagents, in parallel, with the identical composed prompt and no shared state?
2. **Fail-closed merge.** PASS requires both reviewers to PASS; any FAIL fails; PASS/FAIL splits are marked CONTESTED and count as FAIL; N/A splits are covered (N/A vs PASS → PASS, N/A vs FAIL → CONTESTED). Is this merge table present and unambiguous?
3. **Contested surfacing.** Are both rationales shown for contested rules, with guidance that recurring contests mean a decidability bug in the rule?
4. **Actionable failure.** Does the protocol require the final report to aggregate per-FAIL "missing for PASS" suggestions with locations?
5. **Companion-mode loud failure.** (Companion mode only) If the source skill path is missing or unreadable at review time, does the protocol stop with an error rather than pass or skip? Is the source path + version recorded in `rules-source.md`, with excluded rules listed with reasons?

## Verdict Template (assets/templates/verdict.md)

1. **Per-rule table.** Rule, reviewer A verdict, reviewer B verdict, final verdict, evidence.
2. **Overall verdict.** A single unambiguous PASS/FAIL line.
3. **Fix list.** A section for aggregated suggestions on FAIL, ordered by category importance.

## Usefulness Assessment

1. **Gate value.** Is this domain one where a wrong PASS is costly enough to justify two reviewer dispatches per check? If a single linter rule or script could decide every rule deterministically, the skill should be a script, not a reviewer gate — flag it.
2. **Proven both ways.** Is there evidence (dry run, gotchas entry) that the gate has both passed a good artifact and failed a bad one? A gate that has never failed anything is unproven.

## Verdict

- **SHIP**: Every enforced rule is decidable with nameable evidence. Reviewer prompt is self-contained, adversarial, evidence-both-ways, structured. Merge is fail-closed with contested surfacing. Failures produce located, actionable suggestions. Companion mode fails loudly.
- **NEEDS WORK**: Protocol sound but some rules undecidable or dead weight, or the prompt allows evidence-free PASS, or suggestions lack locations. Specific fixes identified.
- **REJECT**: Single-reviewer or context-contaminated design, merge not fail-closed, companion mode can silently pass without its source, or the majority of rules are judgment calls.

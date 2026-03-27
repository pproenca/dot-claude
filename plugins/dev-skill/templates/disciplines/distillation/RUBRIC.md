# Distillation Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Claim Verification (pick 3 random CRITICAL/HIGH rules)

For each selected rule:

1. **WebSearch the core claim.** Does authoritative documentation agree with the rule's advice? If the rule says "avoid X because Y," search for evidence that Y actually happens.
2. **Evaluate the "incorrect" example.** Would a real developer write this code? Is the stated problem genuine and significant, or is it a strawman? Could the incorrect example sometimes be the right choice?
3. **Evaluate the "correct" example.** Could you paste this into a production codebase and have it work? Does it handle the stated scenario completely, or does it silently break on edge cases?
4. **Check impact calibration.** Is this rule's impact level consistent with sibling rules? A rule rated CRITICAL should genuinely cause more damage than one rated HIGH.
5. **Verify impact description.** Is it quantified ("2-10x improvement") or vague ("significant improvement")? Vague claims fail.

Record each finding: rule file, check performed, result (PASS/FAIL), evidence (URL or reasoning).

## Cross-Rule Consistency (scan all rules)

1. **Contradictions.** Are there two rules that give opposing advice? (e.g., "always use X" in one rule, "avoid X" in another without qualifying context)
2. **Duplication.** Are there rules giving the same advice in different words? Flag for merging.
3. **Category ordering.** Is the highest-impact category genuinely the most impactful for this technology? Would a senior engineer agree with the ranking?
4. **Impact inflation.** Count the rules at each impact level. If >30% are CRITICAL, impact is inflated. Expect: 1-2 CRITICAL categories, 2-3 HIGH, rest MEDIUM/LOW.
5. **Prefix consistency.** Does every rule's first tag match its category prefix? Do all rules in a category use the same prefix?

## Reference Verification (spot-check 3-5 URLs)

For each reference URL:

1. **Liveness.** Is the URL still accessible? (Use WebSearch to check)
2. **Relevance.** Does the linked content actually support the claim the rule makes?
3. **Authority.** Is the source from official docs, framework maintainers, or recognized experts? Flag tutorial sites, Stack Overflow answers, or personal blogs.
4. **Currency.** For fast-moving technologies (React, Node.js, etc.), is the source from the last 2 years?

## Completeness

1. **Major gaps.** WebSearch "{technology} performance best practices {current year}" and "{technology} common mistakes." Are there patterns that appear in 3+ authoritative sources but are missing from the skill?
2. **Exception coverage.** Do rules with important exceptions include "When NOT to use this pattern" sections?
3. **Rule count.** Is the total between 40-60? Under 30 = gaps. Over 70 = padding.
4. **Category balance.** No category should have 0 rules. No category should have >10 rules (split it). Major categories: 5-8 rules. Minor categories: 2-4 rules.

## Code Example Quality (sample 5 rules)

1. **Language correctness.** Do code examples use the correct syntax for the stated language/framework version?
2. **Realistic names.** No `foo`, `bar`, `data`, `MyComponent`, `doSomething`. Variable names should reflect a realistic domain.
3. **Minimal diff.** The incorrect and correct examples should differ minimally — same variable names, same structure, only the key insight changes.
4. **Comments.** Code comments explain consequences, not syntax. Max 1-2 comments per block.

## Verdict

- **SHIP**: All 3 sampled rules pass claim verification. No contradictions. References live. Category ordering defensible.
- **NEEDS WORK**: 1-2 sampled rules fail claim verification, or minor contradictions found, or some references dead. Specific fixes will resolve.
- **REJECT**: Systematic inaccuracy (majority of sampled rules fail). Contradictions in CRITICAL rules. Category ordering fundamentally wrong. Needs significant rework.

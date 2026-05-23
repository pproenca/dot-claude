# Distillation Validation Rubric

Read by the `skill-reviewer` agent. These are verifiable checks with evidence — not subjective taste. Record for each finding: what you checked, the result (PASS/FAIL), and the evidence (a URL, a file:line, or concrete reasoning).

The skill's job is to correct where a capable model is *wrong by default* — not to re-teach the language. Review against that bar.

## 1. Sufficiency — does every rule earn its place? (the primary check)

For **each** rule, answer:

1. **What is the wrong default it corrects?** State, in one sentence, what a competent model would do here *without* this rule. If you can't name a wrong default, the rule is filler — **FAIL it for deletion.**
2. **Is the default actually wrong, or just phrased differently?** If a capable model already does the right thing here, the rule restates the obvious — **FAIL it for deletion.** (This is the most common defect. Be ruthless: hand-holding rules are the thing this discipline exists to prevent.)
3. **Does it explain WHY, or only dictate?** A rule that says "ALWAYS X" / "NEVER Y" without the consequence is brittle. Flag it to be rewritten as reasoning the model can generalize from.

Then, across the set:

4. **Coverage gaps.** Are there wrong defaults that *do* matter for this technology but aren't covered? Find them by reasoning about the target tasks (and the eval prompts if present), not by comparing to a target count. **There is no minimum or maximum rule count.** A tight 8-rule skill that covers the consequential decisions beats a 45-rule skill padded with restatements.

## 2. Claim verification (sample 3 rules; bias toward the most consequential)

For each sampled rule:

1. **Verify the core claim** against an authoritative source (WebSearch / the library's docs / its source). Does the recommendation actually hold for the current version?
2. **Judge the example.** Could you paste the canonical example into a real codebase and have it work, with realistic names? If the rule uses an Incorrect/Correct foil, is the "incorrect" something a real developer would actually write — or a strawman? (A strawman foil is a defect: flag it to become a single canonical example.)
3. **Check honesty of any impact claim.** If `impactDescription` is present, is it true and traceable — not an invented "2–10×"? Plain consequences ("prevents stale reads") are fine; fabricated numbers are not.

## 3. Cross-rule consistency (scan all rules)

1. **Contradictions.** Two rules giving opposing advice without qualifying context → FAIL.
2. **Duplication.** Two rules making the same point in different words → flag to merge. Merging is conciseness; keep the one with the better WHY.
3. **Ordering.** Are categories in importance order (most frequent / most costly first)? If the skill uses `impact` tiers, is that order non-increasing, and are the tiers honest (not everything CRITICAL)?
4. **Prefixes.** Does every rule's first tag match its category prefix?

## 4. Source authority (spot-check 3–5 sources)

For each source URL:

1. **Authority** — primary maintainer, spec author, or named expert? **Reject** content farms, listicles, w3schools/geeksforgeeks-style pages, undated blogs, and AI-generated SEO filler (no author, no date, restates docs).
2. **Liveness** — reachable?
3. **Support** — does the page actually back the claim, or just share a keyword with it?
4. **Currency** — current with the library's major version?

Any rule whose only support is an SEO-tier source FAILS until re-grounded in docs/spec/code.

## 5. Code example quality (sample 5)

1. **Correct syntax** for the stated language/version.
2. **Realistic names** — no `foo`, `bar`, `data`, `MyComponent`, `doSomething`.
3. **Minimal diff** — when a foil is used, incorrect and correct share names/structure; only the key line differs.
4. **Comments earn their place** — explain the consequence, not the syntax; 1–2 per block at most.

## Verdict

- **SHIP** — Every rule corrects a real wrong default. No restatement filler. Sampled claims verified. Sources authoritative. No contradictions.
- **NEEDS WORK** — Some filler/restatement rules to cut, or 1–2 claims unverified, or some SEO-tier sources, or strawman foils. Name the specific rules and fixes.
- **REJECT** — Pervasive hand-holding (many rules restate correct defaults), systematic inaccuracy, or sources are mostly non-authoritative. Needs rework against the sufficiency bar.

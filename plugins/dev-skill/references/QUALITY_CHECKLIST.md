# Skill Quality Checklist

The bar for a distilled skill is **provable conciseness**: every rule corrects a
wrong default, nothing restates what the model already does, and completeness is
proven by evals rather than by a rule count. Validate in two phases.

| Marker | Meaning | Validator |
|--------|---------|-----------|
| AUTO | Checked mechanically | `node scripts/validate-skill.js {skill}` |
| REVIEW | Needs judgment | `skill-reviewer` agent against the discipline `RUBRIC.md` |
| PROOF | Behavioral | `/dev-skill:eval` |

## The sufficiency bar (REVIEW — most important)

- [ ] Every rule names the **wrong default it corrects** — what a capable model would otherwise do here.
- [ ] No rule restates a correct default (no hand-holding / filler).
- [ ] Every rule explains **WHY**, not just WHAT. No bare `ALWAYS`/`NEVER` in caps.
- [ ] No two rules contradict; near-duplicates are merged into the one with the better reasoning.
- [ ] Coverage is judged by the target tasks, **not** by count. There is no minimum or maximum.

## Structure (AUTO)

- [ ] `SKILL.md`: frontmatter (`name` kebab-case, `description`), `When to Apply`, `Quick Reference`.
- [ ] Categories ordered by importance; prefixes 2–10 chars and consistent.
- [ ] Each rule: H2 matches `title`; first tag = category prefix; ≥1 fenced code block with a language.
- [ ] `metadata.json`: `version`, `organization`, `date`, `abstract`, `references[]`, plus `discipline` + `type`.
- [ ] `AGENTS.md` built by `build-agents-md.js` (use `--verify-generated`), never hand-written.

## Examples (REVIEW)

- [ ] One canonical example by default. A foil (Incorrect/Correct) only where the wrong way is a real, common trap — never a strawman.
- [ ] Realistic names (no `foo`/`bar`/`MyComponent`).
- [ ] When a foil is used, minimal diff (same names, key line changes); comments explain consequences, not syntax.

## Optional — performance skills only

- [ ] `impact` tiers and `impactDescription` appear **only** if the skill is genuinely about performance.
- [ ] Any quantified claim is honest and traceable to a primary source — never fabricated to hit a quota.

## Sources (REVIEW)

- [ ] Every source is a primary maintainer doc, spec, the library's own code, or named-expert writing.
- [ ] No content farms, listicles, undated blogs, or AI-generated SEO filler.
- [ ] Each cited claim traces to a primary source and is current with the library's major version.

## Proof (PROOF)

- [ ] `validate-skill.js` passes with 0 errors.
- [ ] `skill-reviewer` returns SHIP.
- [ ] `/dev-skill:eval` passes on the target tasks. Gaps it reveals are closed with rules that close them — not with padding.

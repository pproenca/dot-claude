# Distillation Quality Checklist

Run before shipping. The bar is **provable conciseness**: every rule corrects a
wrong default, nothing restates what the model already does, and the skill's
completeness is proven by behavior on the target tasks rather than by a rule count.

## The sufficiency bar (most important)

- [ ] Every rule names a **wrong default it corrects** — what a competent model would otherwise do here. If you can't name one, delete the rule.
- [ ] No rule restates a correct default (no hand-holding / filler).
- [ ] Every rule explains **WHY** (the consequence), not just WHAT. No bare `ALWAYS`/`NEVER`.
- [ ] Coverage is judged by the target tasks, **not** a rule count. There is no minimum or maximum.
- [ ] No two rules contradict; near-duplicates are merged into the one with the better reasoning.

## Structure

- [ ] `SKILL.md` has frontmatter (`name` kebab-case, `description`), a `When to Apply` section, and a `Quick Reference`.
- [ ] Categories are ordered by importance; prefixes are 2–10 chars and consistent.
- [ ] Each rule file: H2 matches the `title`; first tag = the category prefix.
- [ ] `metadata.json`: `version`, `organization`, `date`, `abstract`, `references[]`.
- [ ] `AGENTS.md` was built with `build-agents-md.js` (not hand-written).

## Examples

- [ ] Default is a single canonical example. A foil (Incorrect/Correct) appears only where the wrong way is a real, common trap.
- [ ] No strawman "incorrect" examples.
- [ ] Realistic names (no `foo`/`bar`/`MyComponent`); code blocks specify a language.
- [ ] When a foil is used, the diff is minimal (same names, key line changes).

## Optional (performance skills only)

- [ ] `impact` tiers and `impactDescription` are used **only** if the skill is genuinely about performance.
- [ ] Any quantified claim is honest and traceable to a source — never a fabricated number.

## Sources

- [ ] Every source is a primary maintainer doc, spec, the library's own code, or named expert writing.
- [ ] No content farms, listicles, undated blogs, or AI-generated SEO filler.
- [ ] Each cited claim is traceable back to a primary source and current with the library's major version.

## Final gate

- [ ] `node scripts/validate-skill.js {skill}` passes (0 errors).
- [ ] `skill-reviewer` agent run against `RUBRIC.md` returns SHIP.

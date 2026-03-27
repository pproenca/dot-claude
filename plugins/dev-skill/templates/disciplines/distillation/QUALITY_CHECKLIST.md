# Skill Quality Checklist

Use this checklist to validate generated skills before publishing.
Target: <5% structural deviation from template.

---

## Structure

- [ ] All categories derived from execution lifecycle analysis
- [ ] Categories ordered by impact (CRITICAL → LOW)
- [ ] File prefixes are consistent and meaningful (3-8 chars)
- [ ] SKILL.md provides quick reference navigation (~120 lines)
- [ ] Individual rules have full detail
- [ ] AGENTS.md compiles everything correctly

### SKILL.md Sections
- [ ] Frontmatter with name and description
- [ ] When to Apply (5 scenarios)
- [ ] Rule Categories by Priority table
- [ ] Quick Reference (1-line per rule by category)
- [ ] How to Use
- [ ] Full Compiled Document reference

### Rule File Structure
- [ ] YAML frontmatter: title, impact, impactDescription, tags
- [ ] H2 title matching frontmatter
- [ ] Brief explanation (1-3 sentences)
- [ ] Incorrect example with annotation
- [ ] Correct example with annotation
- [ ] Optional sections present where needed

### metadata.json
- [ ] version (semantic versioning)
- [ ] organization
- [ ] date (Month Year format)
- [ ] abstract
- [ ] references (array of URLs)

---

## Content

- [ ] Each rule has incorrect AND correct examples
- [ ] Examples are realistic (production-like code)
- [ ] Impact is quantified where possible
- [ ] References are authoritative (see SKILL.md "Technology-Specific Focus Areas")
- [ ] No vague guidance ("consider", "might want to")
- [ ] Tags include category prefix + technique + tools

### Example Code Quality
- [ ] TypeScript/typed preferred for web
- [ ] Production-realistic (not strawman)
- [ ] Minimal diff between incorrect and correct
- [ ] Comments explain cost/benefit
- [ ] Self-explanatory naming

### Impact Quantification Patterns
- [ ] Multiplier: `N-M× improvement` (e.g., "2-10× improvement")
- [ ] Time: `Nms reduction` or `N-Mms cost` (e.g., "200-800ms import cost")
- [ ] Complexity: `O(x) to O(y)` (e.g., "O(n) to O(1)")
- [ ] Absolute: `Nk ops to Mk ops` (e.g., "1M ops to 2K ops")
- [ ] Outcome: `{verb}s {outcome}` (e.g., "faster initial paint")
- [ ] Prevention: `prevents/avoids {problem}` (e.g., "prevents stale closures")
- [ ] Reduction: `reduces {thing}` (e.g., "reduces reflows/repaints")

---

## Language

- [ ] Imperative mood for instructions
- [ ] Consistent terminology throughout
- [ ] Technical accuracy verified
- [ ] No marketing fluff
- [ ] Annotations explain cost/benefit

### DO Use
- [ ] Imperative verbs: Use, Avoid, Cache, Extract, Defer
- [ ] Quantified claims: 2-10× improvement
- [ ] Definitive statements: "is the #1 performance killer"

### DON'T Use
- [ ] Hedging: "consider", "might", "perhaps"
- [ ] Marketing: "amazing", "revolutionary", "blazing fast"
- [ ] Vague: "faster" without quantification

### Annotation Style
- [ ] Incorrect: "blocks both branches" (not just "bad")
- [ ] Correct: "only blocks when needed" (not just "good")

---

## Completeness

- [ ] Major performance issues covered
- [ ] Each category has at least one rule (target 3-7 for major)
- [ ] Cross-references to related rules where helpful
- [ ] External tools are referenced for complex solutions
- [ ] Browser/platform support noted where relevant

### Rule Count Targets
| Impact Level | Target Rules |
|--------------|--------------|
| CRITICAL | 4-7 rules |
| HIGH | 3-5 rules |
| MEDIUM-HIGH | 3-5 rules |
| MEDIUM | 2-5 rules |
| LOW-MEDIUM | 2-4 rules |
| LOW | 1-3 rules |

---

## Validation Metrics

| Criterion | Expected | Actual | Pass? |
|-----------|----------|--------|-------|
| Category count | 6-10 | | |
| Categories ordered by impact | Yes | | |
| All prefixes 3-8 chars | Yes | | |
| SKILL.md line count | 100-150 | | |
| Rules have incorrect+correct | 100% | | |
| Impact quantified | >80% | | |
| References present | >50% | | |
| First tag = category prefix | 100% | | |
| No vague language | 0 instances | | |

### Structural Deviation Calculation

```
deviation = (missing elements + wrong elements) / total elements
```

Target: <5% deviation on structural elements.

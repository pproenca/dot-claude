# Skill Quality Checklist

Use this checklist to validate a generated performance best practices skill before release.
Target: <5% structural deviation from guidelines.

---

## Validation Types

| Marker | Meaning | Validator |
|--------|---------|-----------|
| ✅ AUTO | Checked automatically | `scripts/validate-skill.js` |
| 🔍 MANUAL | Requires subjective review | `agents/skill-reviewer.md` |

**Two-phase validation:**
1. **Phase A:** Run `node scripts/validate-skill.js ./skills/{name}` - Fix ALL errors
2. **Phase B:** Launch `skill-reviewer` agent - Fix ALL issues before release

---

## Structure

- [ ] 🔍 MANUAL: All categories derived from execution lifecycle analysis
- [ ] ✅ AUTO: Categories ordered by impact (CRITICAL → HIGH → MEDIUM → LOW)
- [ ] ✅ AUTO: File prefixes are consistent and meaningful (3-8 chars)
- [ ] ✅ AUTO: SKILL.md provides quick reference navigation
- [ ] ✅ AUTO: Individual rule files have full detail
- [ ] ✅ AUTO: AGENTS.md compiles everything correctly
- [ ] ✅ AUTO: metadata.json has version, org, date, abstract, references
- [ ] ✅ AUTO: references/_sections.md defines all categories with prefixes

### SKILL.md Requirements
- [ ] ✅ AUTO: Frontmatter has: name (kebab-case), description
- [ ] ✅ AUTO: **MUST:** H1 title format: `# {Organization} {Technology} Best Practices`
- [ ] ✅ AUTO: Intro paragraph has rule count and category count
- [ ] ✅ AUTO: "When to Apply" section has 5 scenarios
- [ ] ✅ AUTO: "Rule Categories by Priority" table has all columns
- [ ] ✅ AUTO: "Quick Reference" sections match category order
- [ ] ✅ AUTO: "How to Use" section references example paths
- [ ] ✅ AUTO: "Full Compiled Document" section references AGENTS.md
- [ ] ✅ AUTO: Line count: ~100-150 lines

### _sections.md Requirements
- [ ] ✅ AUTO: **MUST:** Each section heading follows format: `## N. Category Name (prefix)`
- [ ] ✅ AUTO: **MUST:** Impact line ends with two trailing spaces for markdown line break: `**Impact:** CRITICAL  `
- [ ] ✅ AUTO: **MUST:** Description line follows Impact line
- [ ] ✅ AUTO: All categories listed in impact-descending order
- [ ] ✅ AUTO: Prefix in parentheses matches rule file naming convention

### Rule File Requirements
- [ ] ✅ AUTO: YAML frontmatter: title, impact, impactDescription, tags
- [ ] ✅ AUTO: **MUST:** H2 title matches frontmatter title exactly (character-for-character)
- [ ] 🔍 MANUAL: Brief explanation (1-3 sentences) explains WHY
- [ ] ✅ AUTO: **MUST:** Incorrect annotation describes the PROBLEM/COST in parentheses
- [ ] ✅ AUTO: **MUST:** Correct annotation describes the BENEFIT/SOLUTION in parentheses
- [ ] ✅ AUTO: **MUST:** Code blocks specify language (```typescript, ```cpp, ```javascript, etc.)
- [ ] 🔍 MANUAL: Code uses the primary language for this technology
- [ ] ✅ AUTO: Optional sections follow standard naming patterns

### metadata.json Requirements
- [ ] ✅ AUTO: version (semantic versioning, e.g., "0.1.0")
- [ ] ✅ AUTO: organization
- [ ] ✅ AUTO: date (Month Year format)
- [ ] ✅ AUTO: technology (full technology name)
- [ ] ✅ AUTO: abstract (2-3 sentences)
- [ ] ✅ AUTO: references (array of authoritative URLs)

### README.md Requirements
- [ ] ✅ AUTO: **MUST:** Overview/Structure section with directory listing
- [ ] ✅ AUTO: **MUST:** Getting Started section with commands:
  - [ ] ✅ AUTO: `pnpm install` command
  - [ ] ✅ AUTO: `pnpm build` command
  - [ ] ✅ AUTO: `pnpm validate` command
- [ ] ✅ AUTO: **MUST:** Creating a New Rule section with:
  - [ ] ✅ AUTO: Step-by-step instructions
  - [ ] ✅ AUTO: Prefix reference table matching _sections.md
- [ ] ✅ AUTO: **MUST:** Rule File Structure section with template example
- [ ] ✅ AUTO: **MUST:** File Naming Convention section explaining prefix-description.md pattern
- [ ] ✅ AUTO: **MUST:** Impact Levels section with CRITICAL → LOW definitions
- [ ] ✅ AUTO: **MUST:** Scripts section listing all available commands
- [ ] ✅ AUTO: **MUST:** Contributing section with guidelines
- [ ] ✅ AUTO: Acknowledgments section (if applicable)

---

## Content

- [ ] ✅ AUTO: Each rule has BOTH incorrect AND correct examples
- [ ] 🔍 MANUAL: Examples are production-realistic (not strawman)
- [ ] ✅ AUTO: Impact is quantified where possible (N×, Nms, O(n) to O(1))
- [ ] 🔍 MANUAL: References are authoritative (see SKILL.md "Technology-Specific Focus Areas" for canonical sources)
- [ ] ✅ AUTO: No vague guidance ("consider", "might want to", "perhaps")
- [ ] ✅ AUTO: First tag is always the category prefix
- [ ] ✅ AUTO: Incorrect/Correct annotations are parenthetical style

### Example Code Quality

#### Structure Requirements
- [ ] 🔍 MANUAL: **MUST:** Minimal diff between incorrect and correct (same variable names, same structure, only key lines differ)
- [ ] 🔍 MANUAL: **MUST:** Both examples produce the same functional result (different approach, same output)
- [ ] ✅ AUTO: **MUST:** Realistic domain names (no `foo`, `bar`, `baz`, `data`, `item`, `thing`)
- [ ] ✅ AUTO: **MUST:** Appropriate complexity (5-20 lines for simple patterns, 20-50 for complex)
- [ ] 🔍 MANUAL: TypeScript/typed preferred for web technologies
- [ ] 🔍 MANUAL: Production-realistic (not strawman anti-patterns)

#### Variable and Function Naming
- [ ] ✅ AUTO: **MUST:** Use domain-realistic names: `user`, `order`, `fetchHeader`, `validateUsers`
- [ ] 🔍 MANUAL: **MUST:** Function names are descriptive verbs: `processOrders`, `fetchUserData`, `computeAvatarId`
- [ ] 🔍 MANUAL: **MUST:** Same variable names in incorrect and correct examples (readers spot the diff instantly)
- [ ] 🔍 MANUAL: Component names follow PascalCase: `UserAvatar`, `ThemeWrapper`, `DataDisplay`
- [ ] 🔍 MANUAL: Use realistic types: `User`, `Order`, `Props` (not generic `T` or `any`)

#### Comment Placement & Style
- [ ] 🔍 MANUAL: **MUST:** Comments on KEY LINES ONLY (1-2 per code block, not every line)
- [ ] 🔍 MANUAL: **MUST:** Comments explain consequences/cost, not syntax ("Runs on every render" not "calls useState")
- [ ] ✅ AUTO: **MUST:** Correct examples have FEWER or EQUAL comments to incorrect examples
- [ ] 🔍 MANUAL: Comments in incorrect examples appear on/near the problematic line
- [ ] 🔍 MANUAL: Comments quantify impact where possible: "Called 10 times = 10 storage reads"

**Comment style examples:**
- ✅ Good: `// Runs on EVERY render, even after initialization`
- ✅ Good: `// 3 round trips to server`
- ✅ Good: `// O(n) lookup per item`
- ❌ Bad: `// This creates a new Set` (syntax, not consequence)
- ❌ Bad: `// Call the function` (obvious from code)
- ❌ Bad: (comment on every line)

#### Code Realism
- [ ] Production-ready function signatures (typed params, meaningful returns, async marked)
- [ ] Realistic data shapes: `user.email`, `order.userId`, `session.user.id`
- [ ] Framework-specific idioms: real APIs like `next/dynamic`, `useSWR`, `React.cache()`
- [ ] Import statements shown when using non-obvious APIs
- [ ] No pseudocode without realistic context

### Impact Quantification Patterns
Valid formats (use these):
- Multiplier: `N-M× improvement` (e.g., "2-10× improvement")
- Time: `Nms reduction` or `N-Mms cost` (e.g., "200-800ms import cost")
- Complexity: `O(x) to O(y)` (e.g., "O(n) to O(1)")
- Absolute: `Nk ops to Mk ops` (e.g., "1M ops to 2K ops")
- Outcome: `{verb}s {outcome}` (e.g., "faster initial paint")
- Prevention: `prevents/avoids {problem}` (e.g., "prevents stale closures")
- Reduction: `reduces {thing}` (e.g., "reduces reflows/repaints")

---

## Language

- [ ] ✅ AUTO: Imperative mood for instructions ("Use", "Avoid", "Cache")
- [ ] 🔍 MANUAL: Consistent terminology throughout
- [ ] 🔍 MANUAL: Technical accuracy verified
- [ ] ✅ AUTO: No marketing fluff ("amazing", "revolutionary")
- [ ] 🔍 MANUAL: Terms defined on first use

### DO Use
- Imperative verbs: Use, Avoid, Cache, Extract, Defer
- Quantified claims: "2-10× improvement"
- Definitive statements: "is the #1 performance killer"

### DON'T Use
- Hedging: "consider", "might", "perhaps", "potentially", "probably"
- Marketing: "amazing", "revolutionary", "blazing fast"
- Vague: "faster" without quantification

### Annotation Style (**MUST** requirements)

Incorrect annotations **MUST** describe the problem/cost:
- ✅ Good: `**Incorrect (blocks event loop):**`
- ✅ Good: `**Incorrect (N boundary crossings):**`
- ✅ Good: `**Incorrect (sequential execution, 3 round trips):**`
- ❌ Bad: `**Incorrect:**` (no description)
- ❌ Bad: `**Incorrect (bad):**` (not descriptive)
- ❌ Bad: `**Incorrect (wrong approach):**` (too vague)

Correct annotations **MUST** describe the benefit/solution:
- ✅ Good: `**Correct (non-blocking):**`
- ✅ Good: `**Correct (1 boundary crossing):**`
- ✅ Good: `**Correct (parallel execution, 1 round trip):**`
- ❌ Bad: `**Correct:**` (no description)
- ❌ Bad: `**Correct (good):**` (not descriptive)
- ❌ Bad: `**Correct (better approach):**` (too vague)

### Teaching Effectiveness

#### Rule Content
- [ ] ✅ AUTO: Brief explanation (1-2 sentences) precedes code examples
- [ ] 🔍 MANUAL: Explanation uses imperative/infinitive form ("Use X when Y", "Convert arrays to Set")
- [ ] 🔍 MANUAL: Complex rules include `**Note:**` or `**When NOT to use:**` sections
- [ ] 🔍 MANUAL: Alternative approaches clearly labeled with when to use them

#### Before/After Mental Model (🔍 MANUAL)
Each incorrect/correct pair should create a recognizable pattern:
- "When I see multiple `await` in sequence → consider `Promise.all()`"
- "When I see `array.includes()` in a loop → consider `new Set()`"
- "When I see `useState(expensiveCall())` → consider `useState(() => expensiveCall())`"

---

## Code Example Anti-Patterns

**AVOID these patterns when writing code examples:**

| Anti-Pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| Generic names (`foo`, `bar`, `data`, `item`) | Not recognizable, hard to map to real code | Use `user`, `order`, `fetchHeader` |
| Over-commented code | Clutters the example, distracts from pattern | 1-2 comments on key lines only |
| Syntax explanation comments | States the obvious, doesn't teach | Explain consequences instead |
| Different variable names in incorrect/correct | Forces reader to mentally map names | Use identical names |
| Too much boilerplate | Distracts from the teaching point | Include only relevant code |
| Pseudocode without context | Not copy-pasteable, feels incomplete | Use real APIs and signatures |
| Wrong order (Correct before Incorrect) | Reader doesn't see the problem first | Always Incorrect, then Correct |
| Over-complex examples (100+ lines) | Hard to scan, loses focus | Split into multiple shorter examples |
| Vague impact ("faster") | No actionable metric | Quantify: "2-10×", "200ms", "O(1)" |

---

## Completeness

- [ ] 🔍 MANUAL: Major performance issues for this technology are covered
- [ ] ✅ AUTO: Each category has at least one rule (3-7 for major, 1-3 for minor)
- [ ] 🔍 MANUAL: Cross-references to related rules where helpful
- [ ] 🔍 MANUAL: External tools referenced for complex solutions
- [ ] 🔍 MANUAL: Browser/platform support noted where relevant

### Rule Count Targets
| Impact Level | Target Rules |
|--------------|--------------|
| CRITICAL | 4-7 rules |
| HIGH | 3-5 rules |
| MEDIUM-HIGH | 3-5 rules |
| MEDIUM | 2-5 rules |
| LOW-MEDIUM | 2-4 rules |
| LOW | 1-3 rules |
| **Total** | **40-50 rules** |

---

## AGENTS.md Requirements

- [ ] ✅ AUTO: Version block has version, org, date
- [ ] ✅ AUTO: **MUST:** Note block mentions specific technology context (not just "codebases")
- [ ] ✅ AUTO: Abstract summarizes scope and counts
- [ ] ✅ AUTO: **MUST:** Table of Contents lists ALL subsections for EVERY category (no truncation)
- [ ] 🔍 MANUAL: **MUST:** All titles have zero typos (run spell check)
- [ ] ✅ AUTO: **MUST:** All titles have zero duplicated words (e.g., "prevent prevent" is invalid)
- [ ] ✅ AUTO: All categories appear in correct order
- [ ] ✅ AUTO: All rules within categories appear alphabetically by title
- [ ] ✅ AUTO: Rule numbering is sequential (1.1, 1.2, ... 2.1, 2.2, ...)
- [ ] ✅ AUTO: References section at end lists all sources

---

## Markdown Formatting Requirements

- [ ] ✅ AUTO: **MUST:** Two trailing spaces used for inline line breaks where needed
- [ ] 🔍 MANUAL: **MUST:** Tables have aligned columns using proper markdown syntax
- [ ] ✅ AUTO: **MUST:** All code blocks specify language (```typescript, ```cpp, ```bash, etc.)
- [ ] 🔍 MANUAL: **MUST:** Links use descriptive text (not raw URLs in body text)
- [ ] 🔍 MANUAL: Consistent heading hierarchy (no skipped levels)
- [ ] 🔍 MANUAL: Horizontal rules (---) separate major sections

---

## Final Verification

- [ ] ✅ AUTO: All files are valid Markdown
- [ ] ✅ AUTO: All YAML frontmatter is valid
- [ ] 🔍 MANUAL: All code examples are syntactically correct
- [ ] 🔍 MANUAL: All URLs are reachable (or marked as examples)
- [ ] ✅ AUTO: No TODO comments or placeholders remain
- [ ] 🔍 MANUAL: **MUST:** Spell check passed with zero errors
- [ ] ✅ AUTO: **MUST:** No duplicated words in any title or heading

---

## Validation Metrics

| Criterion | Expected | Actual | Pass? |
|-----------|----------|--------|-------|
| Category count | 6-10 | | |
| Categories ordered by impact | Yes | | |
| All prefixes 3-8 chars | Yes | | |
| SKILL.md line count | 100-150 | | |
| SKILL.md H1 has org name | Yes | | |
| Rules have incorrect+correct | 100% | | |
| Annotations have descriptions | 100% | | |
| Impact quantified | >80% | | |
| References present | >50% | | |
| First tag = category prefix | 100% | | |
| No vague language | 0 instances | | |
| No typos/duplicated words | 0 instances | | |
| README.md has all sections | Yes | | |
| AGENTS.md TOC complete | Yes | | |
| Code blocks have language | 100% | | |
| No generic names in code | 0 instances | | |
| Code example line count | 5-50 lines | | |
| Same variables in incorrect/correct | 100% | | |

### Structural Deviation Calculation

```
deviation = (missing elements + wrong elements) / total elements
```

**Target: <5% deviation on structural elements.**

---

## Two-Phase Validation

### Phase A: Automated Validation (✅ AUTO)

Run the validation script to check structural requirements:

```bash
node scripts/validate-skill.js ./skills/your-skill-name
```

The script checks:
- Required files exist (SKILL.md, AGENTS.md, README.md, metadata.json, references/_sections.md)
- YAML frontmatter is valid
- All rules have incorrect/correct examples
- **MUST:** All annotations have descriptive parenthetical text
- First tag matches category prefix
- Impact quantified in >80% of rules
- No vague language patterns detected
- Categories correctly ordered by impact
- **MUST:** SKILL.md H1 includes organization name
- **MUST:** AGENTS.md TOC lists all subsections
- **MUST:** README.md contains all required sections
- **MUST:** Code blocks specify language
- **MUST:** No typos or duplicated words in titles
- **MUST:** _sections.md has proper line break formatting
- No generic names (`foo`, `bar`, `baz`) in code examples
- Code example line count within 5-50 lines
- Comment balance (correct blocks have ≤ comments than incorrect)

**Fix ALL errors before proceeding to Phase B.**

### Phase B: Subagent Quality Review (🔍 MANUAL)

Launch the `skill-reviewer` agent to validate subjective quality criteria:

```
Use the Task tool with subagent_type="plugin-dev:skill-reviewer" to review ./skills/{tech-slug}
```

The agent checks:
- Teaching effectiveness (explanations clearly explain WHY)
- Code example realism (production-realistic, not strawman)
- Minimal diff philosophy (identical variable names in incorrect/correct)
- Comment quality (explain consequences, not syntax)
- Impact claim accuracy (realistic performance claims)
- Conceptual accuracy (current best practices)
- Reference authority (authoritative sources)
- Spell check (zero typos)

**DO NOT release until BOTH phases pass with 0 errors/issues.**

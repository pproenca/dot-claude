## ADDED Requirements

### Requirement: Closing Context Sentences

Generated skills SHALL include closing context sentences in at least 50% of rule files. These sentences provide nuanced guidance about when and why to apply the pattern.

#### Scenario: Rule with closing context

- **WHEN** generating a rule file for a performance pattern
- **THEN** the rule SHALL end with a contextual sentence like: "This optimization is especially valuable when [condition], or when [alternative condition]."

#### Scenario: Validation of closing context coverage

- **WHEN** validating a generated skill
- **THEN** the validation SHALL check that ≥50% of rule files contain closing context sentences

---

### Requirement: Trade-off Documentation

Generated skills SHALL document trade-offs explicitly in at least 20% of rules where competing goals exist.

#### Scenario: Trade-off statement format

- **WHEN** a rule involves competing optimization goals
- **THEN** the rule SHALL include a trade-off statement: "**Trade-off:** [Goal A] vs [Goal B]. Choose based on [decision criteria]."

#### Scenario: Example trade-off patterns

- **WHEN** documenting patterns with trade-offs
- **THEN** examples like "Faster initial paint vs potential layout shift" or "Memory usage vs CPU cycles" SHALL be documented

---

### Requirement: Quantified Code Comments

Code examples in generated skills SHALL include specific, quantified metrics in comments for CRITICAL and HIGH impact rules.

#### Scenario: Quantified incorrect example

- **WHEN** showing an incorrect code pattern for a CRITICAL rule
- **THEN** the comment SHALL include specific metrics like: "// PROBLEM: Creates 1,583 module imports, ~2.8s overhead"

#### Scenario: Quantified correct example

- **WHEN** showing a correct code pattern
- **THEN** the comment SHALL include improvement metrics like: "// SOLUTION: Reduces to 3 modules (~2KB vs ~1MB)"

---

### Requirement: Problem-First Writing Style

Rule explanations SHALL start with the problem or impact, not with a definition or description of the technology.

#### Scenario: Problem-first explanation

- **WHEN** writing a rule explanation
- **THEN** the first sentence SHALL describe the problem or impact: "Move await operations into branches where they're actually used to avoid blocking code paths"
- **THEN** the explanation SHALL NOT start with a definition like: "The await keyword is used to pause execution"

---

### Requirement: Quick Reference Bullet Limit

The Quick Reference section in SKILL.md SHALL contain no more than 25 total bullets across all categories.

#### Scenario: Quick reference validation

- **WHEN** generating a SKILL.md Quick Reference
- **THEN** the total bullet count SHALL be ≤25
- **THEN** each category section SHALL have ≤5 bullets

#### Scenario: Condensing detailed patterns

- **WHEN** a category has more than 5 important rules
- **THEN** the Quick Reference SHALL summarize patterns rather than list all rules individually

---

### Requirement: Imperative Verb Quick Reference

Every bullet in the Quick Reference SHALL start with an imperative verb.

#### Scenario: Imperative verb format

- **WHEN** writing Quick Reference bullets
- **THEN** bullets SHALL start with verbs like: "Use", "Avoid", "Prefer", "Defer", "Cache", "Apply"
- **THEN** bullets SHALL NOT start with nouns or noun phrases like: "Memory management", "Smart pointers"

---

### Requirement: Real Library Examples for Critical Rules

CRITICAL impact rules SHALL reference real-world production libraries, not generic utility patterns.

#### Scenario: Real library in critical rule

- **WHEN** generating a CRITICAL impact rule
- **THEN** code examples SHALL use real library names (e.g., lucide-react, pydantic, Abseil, folly)
- **THEN** code examples SHALL NOT use generic patterns like "utils/helper" or "lib/common"

#### Scenario: Language-specific library guidance

- **WHEN** the template specifies language-specific guidance
- **THEN** it SHALL include real library examples:
  - C++: Abseil, Boost, folly, {fmt}
  - Python: pydantic, httpx, asyncio, attrs
  - TypeScript: zod, ts-pattern, effect-ts
  - Rust: tokio, serde, rayon

---

### Requirement: impactDescription Brevity

The impactDescription frontmatter field SHALL be concise, using 8 words or fewer.

#### Scenario: Brief impact description

- **WHEN** writing impactDescription frontmatter
- **THEN** it SHALL use short, punchy metrics: "O(n) to O(1)", "avoids blocking unused paths", "eliminates memory leaks"
- **THEN** it SHALL NOT use verbose descriptions: "eliminates memory leaks and prevents dangling pointer bugs from occurring"

---

## MODIFIED Requirements

### Requirement: Rule File Length Guidance

Rule files SHALL be 30-100 lines, prioritizing content quality over specific line count. Shorter rules (30-50 lines) are acceptable when content is complete and actionable.

#### Scenario: Flexible length based on complexity

- **WHEN** generating a simple rule with clear Incorrect/Correct examples
- **THEN** 30-50 lines is acceptable if content is complete

#### Scenario: Complex rule length

- **WHEN** generating a complex rule with multiple examples and alternatives
- **THEN** 60-100 lines is appropriate

#### Scenario: Quality over quantity validation

- **WHEN** validating rule files
- **THEN** validation SHALL NOT reject rules solely based on line count
- **THEN** validation SHALL check for completeness: frontmatter, explanation, Incorrect/Correct examples

---

### Requirement: Alternative vs Another Example Terminology

The template SHALL distinguish between "Alternative" (different approach) and "Another example" (variant of same pattern).

#### Scenario: Alternative approach usage

- **WHEN** showing a fundamentally different solution approach
- **THEN** use header: "**Alternative ({approach name}):**"
- **EXAMPLE** "**Alternative (Next.js 13.5+ config):**" showing framework-level solution vs code-level solution

#### Scenario: Another example usage

- **WHEN** showing a variation or additional use case of the same pattern
- **THEN** use header: "**Another example ({variation description}):**"
- **EXAMPLE** "**Another example (early return optimization):**" showing same defer-await pattern in different context

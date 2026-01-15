# Change: Improve skills-template Quality to Match React Golden Standard

## Why

The `skills-template` generates skills that are structurally complete but fall short of the expert-level quality demonstrated by `react-best-practices`. A pedantic analysis reveals 15+ quality gaps that prevent generated skills from achieving the same depth, actionability, and AI-agent optimization as the golden standard. These gaps result in skills that look correct but lack the nuance, specificity, and real-world grounding that make the react skill exceptional.

## What Changes

### Core Quality Gaps Identified

**1. Closing Context Sentences (MISSING)**
- React rules end with contextual wisdom: *"This optimization is especially valuable when the skipped branch is frequently taken, or when the deferred operation is expensive."*
- Generated rules lack this pattern - they end abruptly after code examples
- Impact: AI agents miss the nuanced guidance about when/why to apply patterns

**2. impactDescription Verbosity**
- React: Short, punchy metrics - `"avoids blocking unused code paths"`, `"O(n) to O(1)"`
- Generated: Longer phrases - `"eliminates memory leaks and dangling pointers"`
- Impact: Less scannable, harder for AI agents to compare impacts quickly

**3. Quick Reference Bullet Overflow**
- Template specifies: 20-25 bullets total
- React: ~25 bullets (compliant)
- Generated cpp skill: 39 bullets (56% over target)
- Impact: SKILL.md loses its "quick reference" purpose; becomes another comprehensive document

**4. "Another example" vs "Alternative" Terminology**
- React uses: **"Another example (variation description):"**
- Template requires: **"Alternative ({approach name}):"**
- Template doesn't capture that React shows *variants of the same pattern*, not always *alternative approaches*
- Impact: Confusion about when to use Alternative vs Another example

**5. "When NOT to use" Coverage**
- Template requires: 20% of rules
- React: Has this pattern but uses prose integration, not explicit headers
- Generated skills: Often missing or inconsistent
- Impact: AI agents over-apply patterns without understanding contraindications

**6. Quantified Comments in Code Examples**
- React: `// Loads 1,583 modules, takes ~2.8s extra in dev`, `// Runtime cost: 200-800ms on every cold start`
- Generated: Generic comments like `// Easy to forget, exception-unsafe`
- Impact: Lost opportunity to embed specific, memorable metrics

**7. Trade-off Documentation Pattern**
- React has explicit trade-off statements: *"Trade-off: Faster initial paint vs potential layout shift. Choose based on your UX priorities."*
- Template doesn't require this pattern
- Impact: Missing nuanced guidance for choosing between competing goals

**8. Rule File Length Mismatch**
- Template specifies: 60-100 lines
- React actual average: ~48 lines (range 24-82)
- Generated cpp average: ~96 lines
- Impact: Template over-specifies length; quality matters more than line count

**9. Reference Format Inconsistency**
- React: Mix of inline references and end-of-rule `Reference: [text](url)`
- Template: Only shows end-of-rule reference pattern
- Impact: Generated rules lack contextual inline references

**10. Imperative Verb Consistency in Quick Reference**
- React: Every bullet starts with verb - "Defer await", "Use Promise.all()", "Avoid barrel file"
- Generated: Sometimes noun-first - "Memory Management", "Compile Time"
- Impact: Less actionable quick reference

**11. Problem-First Explanations**
- React rule explanations: Start with problem impact - *"Move await operations into branches where they're actually used to avoid blocking code paths"*
- Generated: Sometimes start with definition - *"Raw pointers require manual memory management"*
- Impact: Less urgency, harder to understand why the rule matters

**12. Real Library Examples Coverage**
- React: Uses real libraries consistently (lucide-react, @mui/material, swr, lru-cache, better-all)
- Generated cpp: Uses standard library but rarely mentions real-world libraries (Abseil, Boost, folly, etc.)
- Impact: Examples feel academic rather than production-ready

**13. Version Header Completeness**
- React guidelines.md: Has "Version 0.1.0", source, date, and explicit "Note:" about AI optimization
- Template requires this but generated skills sometimes omit the AI-optimization note
- Impact: Missing context about intended audience

**14. Category Description Pattern**
- React _sections.md: *"Waterfalls are the #1 performance killer. Each sequential await adds full network latency."*
- Pattern: Problem + Impact + Value proposition
- Generated often follows pattern but not as punchy
- Impact: Less memorable category descriptions

**15. Tag Quality and Coverage**
- React: 4-5 specific tags per rule (e.g., `async, await, conditional, optimization`)
- Generated: Sometimes generic or missing relevant tags
- Impact: Reduced searchability and categorization

### Template Instruction Gaps

The template (SKILL-TEMPLATE.md) lacks explicit guidance on:

1. **Closing context sentences** - When and how to add them
2. **Trade-off documentation** - Required format and frequency
3. **"Another example" vs "Alternative"** - When to use each
4. **Quantified comment format** - Examples of specific metric embedding
5. **Rule file length flexibility** - Quality over quantity principle
6. **Inline reference patterns** - Beyond end-of-rule references
7. **Problem-first writing style** - Explicit guidance for explanations

## Impact

- Affected specs: `skills-template` (primary)
- Affected code:
  - `domain_plugins/skills-template/SKILL-TEMPLATE.md`
  - `domain_plugins/skills-template/starter/` templates
  - `domain_plugins/skills-template/agents/skill-architect.md`
- Generated skills will have higher quality parity with react-best-practices
- AI agents using generated skills will receive better guidance

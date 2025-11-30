# Comprehensive Skills Review & Refactoring Plan

**Plugins Reviewed:** agent, blackbox, commit, debug, dev, doc, shell
**Excluded:** super
**Model Pattern:** amazon-writing (doc plugin)
**Date:** 2025-11-30

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Skill-Creator Best Practices Audit Framework](#skill-creator-best-practices-audit-framework)
3. [Model Skill Analysis: amazon-writing](#model-skill-analysis-amazon-writing)
4. [Detailed Skill-by-Skill Review](#detailed-skill-by-skill-review)
5. [Refactoring Specifications](#refactoring-specifications)
6. [Validation Strategy](#validation-strategy)
7. [Implementation Order](#implementation-order)
8. [Rollback Plan](#rollback-plan)

---

## Executive Summary

### Skills Inventory

| Plugin | Skill | Lines | Status | Priority |
|--------|-------|-------|--------|----------|
| dev | python-testing-patterns | 909 | CRITICAL | P0 |
| dev | python-packaging | 872 | CRITICAL | P0 |
| dev | uv-package-manager | 833 | CRITICAL | P0 |
| dev | python-performance-optimization | 871 | CRITICAL | P0 |
| dev | async-python-patterns | 696 | EXCEEDS | P1 |
| doc | amazon-writing | 121 | MODEL | - |
| shell | man | 196 | GOOD | - |
| shell | google-shell-style | 421 | GOOD | P2 |

### Key Findings

1. **5 of 8 skills exceed the 500-line limit** (skill-creator says "under 500 lines")
2. **All dev plugin skills share identical structural anti-patterns**
3. **amazon-writing is the gold standard** - perfect progressive disclosure
4. **shell skills are well-designed** - concise with appropriate bundled resources

### Root Cause Analysis

The dev plugin skills appear to have been created as comprehensive reference guides rather than AI-optimized skills. They contain:
- Explanations of concepts Claude already knows from training
- Tutorial-style progressive examples that waste context
- Redundant "When to Use" sections in the body (should only be in description)
- No progressive disclosure via reference files

---

## Skill-Creator Best Practices Audit Framework

Each skill will be audited against these 8 criteria from the skill-creator documentation:

### 1. Conciseness (Weight: Critical)
> "The context window is a public good... Only add context Claude doesn't already have."

**Pass Criteria:**
- SKILL.md body < 500 lines
- No explanations of concepts in Claude's training data
- No tutorial-style "hello world" examples
- Every section justifies its token cost

### 2. Description Quality (Weight: Critical)
> "This is the primary triggering mechanism... Include all 'when to use' information here"

**Pass Criteria:**
- Description includes specific trigger phrases
- Description covers all use cases
- No "When to Use This Skill" section in body (redundant)

### 3. Progressive Disclosure (Weight: High)
> "Skills use a three-level loading system... Keep SKILL.md body to the essentials"

**Pass Criteria:**
- Core workflow in SKILL.md
- Detailed/variant-specific content in references/
- Clear guidance on when to load reference files

### 4. Degrees of Freedom (Weight: Medium)
> "Match the level of specificity to the task's fragility and variability"

**Pass Criteria:**
- Imperative instructions for fragile operations
- Flexible guidance for creative decisions
- Not over-constraining routine tasks

### 5. Bundled Resources (Weight: Medium)
> "Scripts for tasks that require deterministic reliability... References for documentation"

**Pass Criteria:**
- Scripts for repeated code generation
- References for large documentation
- Assets for output templates
- No extraneous files (README, CHANGELOG, etc.)

### 6. File Structure (Weight: Medium)
**Pass Criteria:**
- Valid YAML frontmatter (name, description required)
- No extraneous documentation files
- Logical organization of resources

### 7. Information Architecture (Weight: Medium)
**Pass Criteria:**
- Table of contents for files >100 lines
- Logical section ordering
- No deeply nested references

### 8. Actionability (Weight: Low)
**Pass Criteria:**
- Clear instructions Claude can follow
- Examples that demonstrate patterns, not teach basics
- Specific enough to execute

---

## Model Skill Analysis: amazon-writing

The amazon-writing skill exemplifies all best practices. This is the target pattern for refactoring.

### Structure Analysis

```
amazon-writing/
├── SKILL.md (121 lines)
└── references/
    ├── one-pager.md
    ├── press-release.md
    ├── prfaq.md
    └── six-pager.md
```

### Why It Works

#### 1. Perfect Description (Lines 1-4)
```yaml
name: amazon-writing
description: Use when writing narrative memos, 6-pagers, 1-pagers, press releases,
or PRFAQs in Amazon style. Applies Amazon's no-PowerPoint writing standards with
data over adjectives, active voice, and the "so what" test.
```

**Strengths:**
- Lists ALL document types (6-pagers, 1-pagers, press releases, PRFAQs)
- Includes key methodology terms ("data over adjectives", "so what test")
- Provides context ("Amazon style", "no-PowerPoint")
- No wasted words

#### 2. Concise Core Rules (Lines 6-54)
The body contains ONLY:
- 6 core writing principles (data over adjectives, active voice, etc.)
- Tables comparing good/bad examples
- No "what is Amazon writing" explanation (Claude knows)
- No history or background

#### 3. Progressive Disclosure via References (Lines 56-65)
```markdown
| Document Type | When to Use | Reference File |
|---------------|-------------|----------------|
| Press Release | New product/feature | `references/press-release.md` |
| 6-Pager | Complex strategic topics | `references/six-pager.md` |
```

**Key Insight:** Document-specific details live in reference files, loaded ONLY when that document type is needed.

#### 4. Process, Not Tutorial (Lines 67-100)
The "Rewriting Process" section is procedural:
1. Analyze Content
2. Load Document Guidelines
3. Rewrite
4. Verify

No "here's an example of how to write a press release" - just the process.

### Metrics to Emulate

| Metric | amazon-writing | Target for Others |
|--------|----------------|-------------------|
| SKILL.md lines | 121 | < 350 |
| "When to Use" in body | None | None |
| "Core Concepts" section | None | None (or < 10 lines) |
| Reference files | 4 | 1-3 |
| Tutorial examples | 0 | 0 |

---

## Detailed Skill-by-Skill Review

### 1. python-testing-patterns

**Current State:** 909 lines (182% of limit)

#### Audit Results

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Conciseness | FAIL | 909 lines, 82% over limit |
| Description Quality | PARTIAL | Good triggers, but "When to Use" duplicated in body |
| Progressive Disclosure | FAIL | No reference files, all content in single file |
| Degrees of Freedom | PASS | Appropriate flexibility for testing patterns |
| Bundled Resources | FAIL | No scripts despite repeated pytest commands |
| File Structure | PARTIAL | Valid frontmatter, missing references/ |
| Information Architecture | PARTIAL | Good sections but too many |
| Actionability | PASS | Clear patterns with code examples |

#### Specific Issues

**Issue 1: Redundant "When to Use This Skill" (Lines 11-23)**
```markdown
## When to Use This Skill

- Writing unit tests for Python code
- Setting up test suites and test infrastructure
...
```
This duplicates the description. Claude already knows when to trigger the skill.

**Issue 2: Explanatory "Core Concepts" (Lines 24-46)**
```markdown
## Core Concepts

### 1. Test Types
- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interaction between components
...
```
Claude knows what unit tests are. This wastes 22 lines explaining basics.

**Issue 3: Trivial "Quick Start" (Lines 48-64)**
```python
def test_add():
    """Basic test example."""
    result = add(2, 3)
    assert result == 5
```
Claude can write a basic test. This 16-line section adds no value.

**Issue 4: 10 Full Patterns in Main Body**
Patterns 6-10 (Advanced Patterns) should be in references:
- Pattern 6: Testing Async Code
- Pattern 7: Monkeypatch for Testing
- Pattern 8: Temporary Files
- Pattern 9: Custom Fixtures and Conftest
- Pattern 10: Property-Based Testing

**Issue 5: Database Testing Section (Lines 732-801)**
70 lines of database-specific testing should be in `references/database-testing.md`.

**Issue 6: CI/CD Section (Lines 803-840)**
37 lines of CI/CD config should be in `references/ci-cd.md`.

#### Refactoring Specification

**Target Structure:**
```
python-testing-patterns/
├── SKILL.md (~320 lines)
└── references/
    ├── advanced-patterns.md (~300 lines)
    │   ├── async testing
    │   ├── monkeypatch
    │   ├── temporary files
    │   ├── fixtures/conftest
    │   └── property-based testing
    ├── database-testing.md (~80 lines)
    └── ci-cd-integration.md (~60 lines)
```

**SKILL.md Changes:**
1. DELETE "When to Use This Skill" section (lines 11-23)
2. DELETE "Core Concepts" section (lines 24-46)
3. DELETE "Quick Start" section (lines 48-64)
4. KEEP Patterns 1-5 (Fundamental Patterns)
5. MOVE Patterns 6-10 to `references/advanced-patterns.md`
6. MOVE "Testing Database Code" to `references/database-testing.md`
7. MOVE "CI/CD Integration" to `references/ci-cd-integration.md`
8. ADD reference navigation table (like amazon-writing)

**New SKILL.md Outline:**
```markdown
---
name: python-testing-patterns
description: [KEEP CURRENT - already good]
allowed-tools: [KEEP CURRENT]
---

# Python Testing Patterns

## Reference Files

| Topic | When to Load | File |
|-------|--------------|------|
| Async, fixtures, property-based | Advanced testing needs | references/advanced-patterns.md |
| SQLAlchemy, in-memory DBs | Database testing | references/database-testing.md |
| GitHub Actions, coverage | CI/CD setup | references/ci-cd-integration.md |

## Fundamental Patterns

### Pattern 1: Basic pytest Tests
[KEEP - 35 lines]

### Pattern 2: Fixtures for Setup and Teardown
[KEEP - 75 lines]

### Pattern 3: Parameterized Tests
[KEEP - 50 lines]

### Pattern 4: Mocking with unittest.mock
[KEEP - 70 lines]

### Pattern 5: Testing Exceptions
[KEEP - 40 lines]

## Test Organization
[CONDENSE to 30 lines - remove obvious naming examples]

## Configuration Files
[KEEP - 45 lines]

## Best Practices Summary
[KEEP - 15 lines]
```

---

### 2. python-packaging

**Current State:** 872 lines (174% of limit)

#### Audit Results

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Conciseness | FAIL | 872 lines, 74% over limit |
| Description Quality | PARTIAL | "When to Use" duplicated in body |
| Progressive Disclosure | FAIL | 20 patterns in single file |
| Bundled Resources | PARTIAL | Could use template files |
| Information Architecture | FAIL | Pattern 18 is README template (meta) |

#### Specific Issues

**Issue 1: README.md Template (Lines 692-737)**
This is documentation teaching Claude to write documentation. Claude already knows markdown. Delete entirely.

**Issue 2: .gitignore Template (Lines 787-819)**
Claude can generate .gitignore files. Delete or move to optional reference.

**Issue 3: MANIFEST.in Template (Lines 821-833)**
Low-value template. Move to reference.

**Issue 4: 20 Patterns is Too Many**
Patterns should be split:
- Core (1-10): Keep in SKILL.md
- Advanced (11-20): Move to references

#### Refactoring Specification

**Target Structure:**
```
python-packaging/
├── SKILL.md (~350 lines)
└── references/
    ├── advanced-patterns.md (~250 lines)
    │   ├── Data files
    │   ├── Namespace packages
    │   ├── C extensions
    │   ├── Version management
    │   ├── Multi-arch wheels
    │   └── Private package index
    └── templates.md (~60 lines)
        ├── MANIFEST.in example
        └── .gitignore patterns
```

**DELETE entirely:**
- "When to Use This Skill" (lines 13-22)
- "Core Concepts" (lines 24-47) - Claude knows PEP 517/621
- Pattern 18: README.md Template (lines 692-737)

---

### 3. uv-package-manager

**Current State:** 833 lines (167% of limit)

#### Audit Results

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Conciseness | FAIL | 833 lines, 67% over limit |
| Description Quality | PARTIAL | Duplicated "When to Use" |
| Progressive Disclosure | FAIL | 22 patterns, no references |

#### Specific Issues

**Issue 1: "What is uv?" Section (Lines 25-49)**
```markdown
### 1. What is uv?
- **Ultra-fast package installer**: 10-100x faster than pip
- **Written in Rust**: Leverages Rust's performance
```
Claude knows what uv is. This is marketing copy, not skill content. DELETE.

**Issue 2: Installation Section (Lines 52-76)**
Users asking about uv workflows already have it installed. DELETE or reduce to 3 lines.

**Issue 3: Comparison Section (Lines 523-567)**
"uv vs pip", "uv vs poetry" - Claude knows these tools. DELETE.

**Issue 4: Migration Guide (Lines 735-778)**
Only needed when specifically migrating. Move to `references/migration.md`.

#### Refactoring Specification

**Target Structure:**
```
uv-package-manager/
├── SKILL.md (~350 lines)
└── references/
    ├── advanced-workflows.md (~200 lines)
    │   ├── Monorepo support
    │   ├── CI/CD integration
    │   ├── Docker integration
    │   └── Lockfile workflows
    └── migration.md (~50 lines)
        ├── From pip
        ├── From poetry
        └── From pip-tools
```

**DELETE entirely:**
- "When to Use" (lines 11-23)
- "What is uv?" (lines 25-49)
- Installation (lines 52-76) -> reduce to 3 lines
- "UV vs Traditional Tools" (lines 44-49)
- Comparison section (lines 523-567)

---

### 4. async-python-patterns

**Current State:** 696 lines (139% of limit)

#### Audit Results

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Conciseness | EXCEEDS | 696 lines, 39% over limit |
| Description Quality | PARTIAL | "When to Use" in body |
| Progressive Disclosure | FAIL | Real-world apps should be references |

#### Specific Issues

**Issue 1: Core Concepts (Lines 23-55)**
Claude knows what event loops, coroutines, and futures are. DELETE.

**Issue 2: Quick Start (Lines 57-67)**
```python
async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")
```
This is the asyncio equivalent of "Hello World". DELETE.

**Issue 3: Real-World Applications (Lines 399-540)**
These 140+ lines of web scraping, database, and WebSocket examples should be in `references/real-world-examples.md`.

#### Refactoring Specification

**Target Structure:**
```
async-python-patterns/
├── SKILL.md (~400 lines)
└── references/
    └── real-world-examples.md (~180 lines)
        ├── Web scraping with aiohttp
        ├── Async database operations
        └── WebSocket server
```

---

### 5. python-performance-optimization

**Current State:** 871 lines (174% of limit)

#### Audit Results

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Conciseness | FAIL | 871 lines, 74% over limit |
| Progressive Disclosure | FAIL | 20 patterns, no references |
| Bundled Resources | PARTIAL | Could include benchmark script |

#### Specific Issues

**Issue 1: Core Concepts (Lines 24-43)**
Claude knows profiling types and performance metrics. DELETE.

**Issue 2: Quick Start (Lines 45-70)**
Basic timeit example is trivial. DELETE.

**Issue 3: Database Optimization (Lines 606-678)**
72 lines of database-specific optimization should be in `references/database-optimization.md`.

**Issue 4: Memory Optimization (Lines 679-777)**
98 lines of memory-specific content should be in `references/memory-optimization.md`.

#### Refactoring Specification

**Target Structure:**
```
python-performance-optimization/
├── SKILL.md (~400 lines)
└── references/
    ├── database-optimization.md (~80 lines)
    ├── memory-optimization.md (~100 lines)
    └── benchmarking-tools.md (~60 lines)
```

---

### 6. google-shell-style (Minor Improvements)

**Current State:** 421 lines (84% of limit) - PASS

#### Audit Results

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Conciseness | PASS | Under 500 lines |
| Description Quality | PASS | Good trigger phrases |
| Progressive Disclosure | PARTIAL | Has quick-reference.md but could use more |

#### Minor Issues

**Issue 1: Additional Resources Reference (Lines 411-416)**
```markdown
For the complete Google Shell Style Guide:
- **`${CLAUDE_PLUGIN_ROOT}/styleguide.md`** - Full original styleguide (project root)
```
This references a file that may not exist in the skill directory. Verify or remove.

**Recommendation:** No major changes needed. Consider:
- Verify styleguide.md reference
- Potentially move "Security Patterns" to reference (if trimming needed later)

---

### 7. man (No Changes Needed)

**Current State:** 196 lines - PASS

This skill follows best practices:
- Concise (196 lines)
- Good description with trigger phrases
- Includes useful bundled script (mancat.sh)
- No redundant explanations

**Status:** No changes required.

---

## Validation Strategy

### Phase 1: Static Validation

For each refactored skill, verify:

#### 1.1 Line Count Check
```bash
# Must be < 500 lines for SKILL.md
for skill_dir in plugins/*/skills/*/; do
  if [[ -f "${skill_dir}SKILL.md" ]]; then
    lines=$(wc -l < "${skill_dir}SKILL.md")
    if (( lines >= 500 )); then
      echo "FAIL: ${skill_dir}SKILL.md has ${lines} lines (limit: 500)"
    else
      echo "PASS: ${skill_dir}SKILL.md has ${lines} lines"
    fi
  fi
done
```

**Pass Criteria:** All SKILL.md files < 500 lines

#### 1.2 Frontmatter Validation
```bash
# Check YAML validity and required fields
for skill in plugins/*/skills/*/SKILL.md; do
  echo "Checking: $skill"
  # Must have name:
  if ! grep -q "^name:" "$skill"; then
    echo "  FAIL: Missing 'name:' field"
  fi
  # Must have description:
  if ! grep -q "^description:" "$skill"; then
    echo "  FAIL: Missing 'description:' field"
  fi
  # Should NOT have "When to Use" section in body
  if grep -q "## When to Use" "$skill"; then
    echo "  FAIL: Has 'When to Use' section in body (should be in description only)"
  fi
done
```

**Pass Criteria:**
- `name:` present and non-empty
- `description:` present and > 50 characters
- No "When to Use" section in body

#### 1.3 Reference File Check
```bash
# Verify all referenced files exist
for skill in plugins/*/skills/*/SKILL.md; do
  skill_dir=$(dirname "$skill")
  # Find all references/xxx.md mentions
  grep -oE 'references/[a-z0-9-]+\.md' "$skill" | sort -u | while read ref; do
    if [[ ! -f "${skill_dir}/${ref}" ]]; then
      echo "FAIL: $skill references $ref but file does not exist"
    fi
  done
done
```

**Pass Criteria:** All referenced files exist

#### 1.4 No Prohibited Sections
```bash
# Check for sections that should be deleted
for skill in plugins/*/skills/*/SKILL.md; do
  echo "Checking: $skill"

  if grep -q "## When to Use This Skill" "$skill"; then
    echo "  FAIL: Has 'When to Use This Skill' section (must be removed)"
  fi

  if grep -q "## Core Concepts" "$skill"; then
    # Count lines in Core Concepts section
    start=$(grep -n "## Core Concepts" "$skill" | head -1 | cut -d: -f1)
    if [[ -n "$start" ]]; then
      # Find next ## heading
      end=$(tail -n +$((start+1)) "$skill" | grep -n "^## " | head -1 | cut -d: -f1)
      if [[ -n "$end" ]]; then
        section_lines=$((end - 1))
        if (( section_lines > 15 )); then
          echo "  WARN: Core Concepts section is $section_lines lines (should be < 10)"
        fi
      fi
    fi
  fi

  if grep -q "## Quick Start" "$skill"; then
    echo "  WARN: Has 'Quick Start' section (consider removing if trivial)"
  fi
done
```

**Pass Criteria:** No "When to Use" sections; "Core Concepts" < 10 lines if present

### Phase 2: Semantic Validation

#### 2.1 Trigger Phrase Coverage

For each skill, verify the description covers all use cases:

| Skill | Required Trigger Phrases |
|-------|-------------------------|
| python-testing-patterns | pytest, fixtures, mocking, TDD, unit tests |
| python-packaging | pyproject.toml, PyPI, wheel, package, distribute |
| uv-package-manager | uv, dependencies, virtual environment, python version |
| async-python-patterns | async, await, asyncio, concurrent, non-blocking |
| python-performance-optimization | profile, optimize, bottleneck, cProfile, memory |

**Validation Script:**
```bash
# For each skill, check description contains key phrases
check_triggers() {
  local skill="$1"
  shift
  local triggers=("$@")

  desc=$(grep -A5 "^description:" "$skill" | head -6)

  for trigger in "${triggers[@]}"; do
    if ! echo "$desc" | grep -qi "$trigger"; then
      echo "WARN: $skill description missing trigger: $trigger"
    fi
  done
}

check_triggers "plugins/dev/skills/python-testing-patterns/SKILL.md" \
  "pytest" "fixtures" "mocking" "TDD" "test"

check_triggers "plugins/dev/skills/python-packaging/SKILL.md" \
  "pyproject.toml" "PyPI" "package" "distribute"

# etc...
```

#### 2.2 Progressive Disclosure Verification

Each reference file must be:
1. Referenced in SKILL.md with guidance on when to load
2. Self-contained (can be understood without reading SKILL.md first)
3. Has a table of contents if > 100 lines

**Validation Checklist:**

For each skill with references/:
- [ ] SKILL.md has reference navigation table
- [ ] Each reference file is mentioned in the table
- [ ] Table includes "When to Load" column with specific conditions
- [ ] Reference files > 100 lines have table of contents

**Expected Reference Table Format:**
```markdown
## Reference Files

| Topic | When to Load | File |
|-------|--------------|------|
| [topic] | [specific condition] | `references/[file].md` |
```

### Phase 3: Functional Validation (Subagent Testing)

#### 3.1 Skill Triggering Test

Dispatch a subagent with a prompt that should trigger the skill:

**Test Protocol:**
```
1. Create fresh subagent with no prior context
2. Send test prompt
3. Verify subagent announces using the correct skill
4. Verify subagent produces expected output
```

**Test Cases per Skill:**

| Skill | Test Prompt | Expected Behavior |
|-------|-------------|-------------------|
| python-testing-patterns | "How do I mock an API call in pytest?" | Uses skill, shows Pattern 4 (mocking) |
| python-packaging | "Help me publish my library to PyPI" | Uses skill, shows publishing patterns |
| uv-package-manager | "Set up uv for my new project" | Uses skill, shows Pattern 19 workflow |
| async-python-patterns | "Write an async web scraper" | Uses skill, loads real-world reference |
| python-performance-optimization | "My Python code is slow, how do I find bottlenecks?" | Uses skill, shows profiling patterns |

#### 3.2 Reference Loading Test

Verify subagent loads appropriate reference files when needed:

**Test Cases:**

| Test Prompt | Expected Reference Loaded |
|-------------|---------------------------|
| "I need to write property-based tests with hypothesis" | references/advanced-patterns.md |
| "Help me test async database operations" | references/database-testing.md |
| "Set up pytest in GitHub Actions" | references/ci-cd-integration.md |
| "Create a namespace package" | references/advanced-patterns.md |
| "Migrate from poetry to uv" | references/migration.md |

#### 3.3 Conciseness Impact Test

Compare context window usage before/after refactoring:

**Calculation:**
```
Token estimate = lines * ~4 characters per line / 4 characters per token
                = lines * 1 token per line (approximate)
```

**Expected Savings:**

| Skill | Before (lines) | After (lines) | Token Savings |
|-------|----------------|---------------|---------------|
| python-testing-patterns | 909 | ~320 | 65% |
| python-packaging | 872 | ~350 | 60% |
| uv-package-manager | 833 | ~350 | 58% |
| python-performance-optimization | 871 | ~400 | 54% |
| async-python-patterns | 696 | ~400 | 42% |
| **TOTAL** | 4,181 | ~1,820 | **56%** |

### Phase 4: Regression Testing

#### 4.1 Capability Coverage Matrix

Ensure refactored skills still cover all original capabilities:

**python-testing-patterns:**

| Capability | Original Location | New Location | Test |
|------------|------------------|--------------|------|
| Basic pytest | Pattern 1 | SKILL.md Pattern 1 | Prompt: "basic pytest example" |
| Fixtures | Pattern 2 | SKILL.md Pattern 2 | Prompt: "pytest fixture setup" |
| Parameterized | Pattern 3 | SKILL.md Pattern 3 | Prompt: "parameterized tests" |
| Mocking | Pattern 4 | SKILL.md Pattern 4 | Prompt: "mock API call" |
| Exceptions | Pattern 5 | SKILL.md Pattern 5 | Prompt: "test exception" |
| Async testing | Pattern 6 | references/advanced-patterns.md | Prompt: "test async function" |
| Monkeypatch | Pattern 7 | references/advanced-patterns.md | Prompt: "monkeypatch env var" |
| Temp files | Pattern 8 | references/advanced-patterns.md | Prompt: "temporary file test" |
| Conftest | Pattern 9 | references/advanced-patterns.md | Prompt: "conftest fixtures" |
| Property-based | Pattern 10 | references/advanced-patterns.md | Prompt: "hypothesis testing" |
| Database | Section | references/database-testing.md | Prompt: "test SQLAlchemy" |
| CI/CD | Section | references/ci-cd-integration.md | Prompt: "pytest GitHub Actions" |

#### 4.2 No Information Loss Verification

For each deleted section, verify the information is either:
1. In Claude's training data (no skill needed)
2. Moved to a reference file
3. Truly unnecessary

**Deletion Justification Log:**

| Section Deleted | Lines | Justification | Risk |
|-----------------|-------|---------------|------|
| "When to Use This Skill" | ~13 | Duplicates description | None - info retained in description |
| "Core Concepts" | ~22 | In Claude's training data | None - Claude knows test types |
| "Quick Start" | ~16 | Trivially simple | None - Claude can write basic tests |
| "What is uv?" | ~25 | In Claude's training data | None - Claude knows uv |
| Installation | ~24 | Users already have tool installed | Low - add 1-line reference to docs |
| Comparison sections | ~45 | In Claude's training data | None - Claude knows pip vs uv |

---

## Implementation Order

Execute refactoring in this order to minimize risk:

### Batch 1: Highest Impact (P0) - Day 1

1. **python-testing-patterns** - Most over limit, clearest refactoring path
2. **python-packaging** - Similar structure, can reuse patterns

**Validation Gate 1:**
- Run Phase 1 static validation
- Run Phase 2 semantic validation
- Commit changes
- Run Phase 3 functional tests (2 skills)

### Batch 2: Medium Impact (P0) - Day 2

3. **uv-package-manager** - Has unique installation/comparison bloat
4. **python-performance-optimization** - Database/memory sections clear split

**Validation Gate 2:**
- Run Phase 1 static validation
- Run Phase 2 semantic validation
- Commit changes
- Run Phase 3 functional tests (2 skills)

### Batch 3: Lower Priority (P1) - Day 3

5. **async-python-patterns** - Least over limit, simplest refactor

**Validation Gate 3:**
- Run all Phase 1-4 validations
- Full regression test across all 5 refactored skills

### Batch 4: Minor (P2) - Optional

6. **google-shell-style** - Verify external reference only

---

## Rollback Plan

### Git-Based Rollback

Before starting, create backup branch:
```bash
git checkout -b backup/skills-pre-refactor
git checkout -b feat/skills-refactor
```

### Per-Skill Rollback

If a refactored skill fails validation:
```bash
git checkout backup/skills-pre-refactor -- plugins/dev/skills/[skill-name]/
```

### Full Rollback

If systemic issues discovered:
```bash
git checkout backup/skills-pre-refactor
git branch -D feat/skills-refactor
```

---

## Success Metrics

### Quantitative

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Total lines (5 dev skills) | 4,181 | ~1,820 | < 2,000 |
| Avg lines per skill | 836 | ~364 | < 400 |
| Skills exceeding 500 lines | 5 | 0 | 0 |
| Skills with references/ | 1 | 6 | 6 |

### Qualitative Checklist

- [ ] All skills follow amazon-writing pattern
- [ ] No redundant "When to Use" sections
- [ ] No trivial "Core Concepts" explanations
- [ ] Progressive disclosure implemented
- [ ] All reference files properly linked
- [ ] Functional tests pass
- [ ] No capability regression
- [ ] All static validations pass
- [ ] All semantic validations pass

---

## Appendix: Templates

### Reference Navigation Table Template

```markdown
## Reference Files

| Topic | When to Load | File |
|-------|--------------|------|
| Advanced patterns | When needing async, fixtures, property-based testing | `references/advanced-patterns.md` |
| Database testing | When testing SQLAlchemy, in-memory DBs | `references/database-testing.md` |
| CI/CD setup | When configuring GitHub Actions, coverage | `references/ci-cd-integration.md` |

Load reference files only when the specific topic is needed.
```

### Reference File Header Template

```markdown
# [Topic Name]

Reference file for [skill-name]. Load when [specific condition].

## Contents

1. [Section 1](#section-1)
2. [Section 2](#section-2)
...

---

## Section 1
...
```

### Validation Script (Complete)

```bash
#!/bin/bash
# validate-skills.sh - Run all Phase 1 and Phase 2 validations

set -e

echo "=== Phase 1: Static Validation ==="

echo -e "\n--- 1.1 Line Count Check ---"
for skill_dir in plugins/*/skills/*/; do
  if [[ -f "${skill_dir}SKILL.md" ]]; then
    lines=$(wc -l < "${skill_dir}SKILL.md")
    skill_name=$(basename "$skill_dir")
    if (( lines >= 500 )); then
      echo "FAIL: $skill_name has $lines lines (limit: 500)"
      exit 1
    else
      echo "PASS: $skill_name has $lines lines"
    fi
  fi
done

echo -e "\n--- 1.2 Frontmatter Validation ---"
for skill in plugins/*/skills/*/SKILL.md; do
  skill_name=$(basename "$(dirname "$skill")")

  if ! grep -q "^name:" "$skill"; then
    echo "FAIL: $skill_name missing 'name:' field"
    exit 1
  fi

  if ! grep -q "^description:" "$skill"; then
    echo "FAIL: $skill_name missing 'description:' field"
    exit 1
  fi

  echo "PASS: $skill_name has valid frontmatter"
done

echo -e "\n--- 1.3 Reference File Check ---"
for skill in plugins/*/skills/*/SKILL.md; do
  skill_dir=$(dirname "$skill")
  skill_name=$(basename "$skill_dir")

  refs=$(grep -oE 'references/[a-z0-9-]+\.md' "$skill" 2>/dev/null | sort -u || true)

  for ref in $refs; do
    if [[ ! -f "${skill_dir}/${ref}" ]]; then
      echo "FAIL: $skill_name references $ref but file does not exist"
      exit 1
    fi
  done

  [[ -n "$refs" ]] && echo "PASS: $skill_name references verified"
done

echo -e "\n--- 1.4 No Prohibited Sections ---"
for skill in plugins/*/skills/*/SKILL.md; do
  skill_name=$(basename "$(dirname "$skill")")

  if grep -q "## When to Use This Skill" "$skill"; then
    echo "FAIL: $skill_name has prohibited 'When to Use This Skill' section"
    exit 1
  fi

  echo "PASS: $skill_name has no prohibited sections"
done

echo -e "\n=== Phase 2: Semantic Validation ==="

echo -e "\n--- 2.1 Trigger Phrase Coverage ---"
# Add specific checks per skill...

echo -e "\n=== All Validations Passed ==="
```

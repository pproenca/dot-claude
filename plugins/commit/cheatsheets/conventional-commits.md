# Conventional Commits Quick Reference

Based on [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) for release-please compatibility.

## The "Git Log Test"

Your subject must pass this test: **A developer skimming `git log --oneline` should understand what this commit does without clicking into it.**

Self-test: "If applied, this commit will _[your description]_"

## Commit Message Structure

```
<type>[!]: <description>

[optional body]

[optional footer(s)]
```

The body explains WHY, not WHAT. Write naturally without rigid labels.

### Type Prefix (REQUIRED)

| Type | Purpose | Triggers Release |
|------|---------|------------------|
| `feat` | New feature | Yes (MINOR) |
| `fix` | Bug fix | Yes (PATCH) |
| `docs` | Documentation only | No |
| `chore` | Maintenance, cleanup | No |
| `refactor` | Code restructuring (no behavior change) | No |
| `perf` | Performance improvement | No |
| `test` | Adding/updating tests | No |
| `build` | Build system, dependencies | No |
| `ci` | CI configuration | No |

### Breaking Changes

Mark breaking changes with ! before the colon:
```
feat!: remove deprecated API endpoint
```

Or use the `BREAKING CHANGE:` footer:
```
feat: restructure authentication

BREAKING CHANGE: JWT tokens now use RS256 instead of HS256
```

### Description Rules

- **Imperative mood**: "add" not "adding" or "added"
- **Lowercase first letter**: "add feature" not "Add feature"
- **No period at end**
- **50-72 characters** ideal, max 100
- **Specific and searchable**: Include component/function names

### Body: Permanent Historical Context

The body becomes **permanent version control history**. Code shows WHAT; body explains WHY.

**Write naturally, covering these as relevant:**
- What issue or need prompted this change
- Why this approach over alternatives
- Implementation details worth noting
- Known limitations or trade-offs
- Context that survives dead links

**Context Survival Rule**: Write as if every linked document will be deleted.

---

## Type Detection Guide

Use this to determine the correct type:

| If your changes... | Type |
|--------------------|------|
| Add new functionality, endpoints, features | `feat` |
| Fix a bug, error, or incorrect behavior | `fix` |
| Only modify documentation (*.md, comments) | `docs` |
| Restructure code without changing behavior | `refactor` |
| Improve performance without changing behavior | `perf` |
| Add or update tests only | `test` |
| Change build system, configs, dependencies | `build` |
| Change CI/CD configuration | `ci` |
| Everything else (cleanup, formatting, etc.) | `chore` |

### Auto-Detection Hints

The plugin auto-detects type based on:
- **test**: Only test files changed (`*_test.*`, `test_*.*`, `tests/`)
- **docs**: Only markdown or docs/ files changed
- **ci**: Only `.github/` files changed
- **build**: Only build configs (`Makefile`, `*config.*`, `package.json`)
- **fix**: Diff contains error-handling patterns
- **feat**: New files added to source directories
- **refactor**: Files renamed/moved, no new exports

When ambiguous, you'll be asked to select the type.

---

## Examples by Type

### feat: New Feature

```
feat: add rate limiting to auth endpoint

Credential stuffing attacks were hitting 10K+ req/sec and overwhelming
downstream services. Token bucket algorithm chosen over sliding window
for O(1) memory footprint. Uses Redis for distributed enforcement.

IPv6 address sharing may cause false positives for shared networks.
```

**Why it works:**
- Subject: Specific component + specific feature
- Context: Concrete numbers (10K requests)
- Rationale: Why token bucket, why Redis
- Acknowledges limitation

### fix: Bug Fix

```
fix: resolve null pointer in UserCache.get() on cache miss

Race condition where async refill returned before initialization
complete. Window was ~50ms during cold-start, causing intermittent
crashes in production.

Added sync barrier between refill task and get() return path.

Fixes #789
```

**Why it works:**
- Subject: Exact location + condition
- Explains the mechanism and impact
- Shows root cause analysis
- Links to issue

### refactor: Code Restructuring

```
refactor: extract validation into ValidationService

Moves duplicated validation logic from OrderController and
PaymentController into a shared service. Reduces 3 copies to 1
and prepares for per-tenant validation rules.

No functional changes - existing tests pass unchanged.
```

**Why it works:**
- Clear "refactor" signal in type
- Explains the WHY (preparation + deduplication)
- Explicitly states "no functional changes"

### feat!: Breaking Change

```
feat!: remove deprecated v1 API endpoints

The v1 API has been deprecated since 2023-01. This removes all
/api/v1/* endpoints. Clients must migrate to /api/v2/*.

BREAKING CHANGE: All /api/v1/* endpoints removed. Use /api/v2/*.
```

**Why it works:**
- Breaking change marked with ! in type
- BREAKING CHANGE footer provides details
- Clearly states migration path

### chore: Maintenance

```
chore: update API rate limits from 100 to 500 req/min

Traffic analysis showed P99 users hitting the 100 req/min limit
during normal usage patterns. Increasing to 500 accommodates
legitimate traffic while still providing abuse protection.

To rollback: revert this commit and restart pods.
```

**Why it works:**
- Specific values in subject (100 to 500)
- Data-driven rationale (P99 users)
- Includes rollback instructions

### test: Adding Tests

```
test: add payment timeout integration tests

Covers edge cases for payment processor timeouts that were
causing silent failures in production. Tests verify retry
behavior and proper error propagation.
```

**Why it works:**
- Specific about what's being tested
- Explains the WHY (silent failures in production)
- Describes what tests verify

---

## Bad Subjects (BLOCKED)

| Bad | Problem | Better |
|-----|---------|--------|
| "Fix bug" | Which bug? No type | `fix: resolve null pointer in UserCache` |
| "fix: fix build" | Vague description | `fix: add missing import in auth_handler` |
| "Update code" | No type, meaningless | `chore: update rate limits to 500 req/min` |
| "Refactoring" | No type, vague | `refactor: extract auth into AuthService` |
| "feat: stuff" | Vague description | `feat: add user preferences endpoint` |
| "WIP" | Incomplete, no type | `feat: add rate limiting (pending Redis)` |
| "chore: misc" | Vague description | `chore: remove unused imports` |
| "Adding tests" | Wrong mood, no type | `test: add payment timeout tests` |
| "feat: Done" | Meaningless description | Describe what's done |

---

## Small Commits Rules

### Size Guidelines

| Lines | Action |
|-------|--------|
| ~100 | Ideal size |
| 100-200 | OK, verify single concern |
| 200-400 | Review if splittable |
| 400+ | Must justify or split |
| 1000+ | Too large - must split |

**File spread matters**: 200 lines in 1 file differs from 200 lines across 50 files.

### Mandatory Separation

| Separate These | Never Mix |
|----------------|-----------|
| Refactoring | with features |
| Features | with bug fixes |
| Bug fixes | with each other (unless related) |

**Exception**: Tests go WITH their feature/fix (same commit).

---

## Commit Splitting Strategies

### When to Split

- 400+ lines -> MUST split
- 200-400 lines -> Consider splitting
- Refactoring + feature -> MUST split
- Multiple independent fixes -> SHOULD split

### Strategies

**1. Stacking (Sequential Dependencies)**
```
Commit 1: refactor: add interface/types for new feature
Commit 2: feat: implement core logic
Commit 3: feat: migrate consumers to new implementation
```

**2. Horizontal (By Layer)**
```
Commit 1: feat: add shared types/interfaces
Commit 2: feat: implement backend logic
Commit 3: feat: add frontend integration
```

**3. Vertical (By Feature)**
```
Commit 1: feat: add multiplication operator
Commit 2: feat: add division operator
(NOT: "feat: add arithmetic operators")
```

**4. By Reviewer Expertise**
```
Commit 1: feat: add database schema (DBA review)
Commit 2: feat: implement backend logic (engineers)
Commit 3: feat: add API contracts (API team)
```

### What Stays Together

- Feature + its tests
- Bug fix + its test
- Small related cleanup (e.g., rename used by new feature)

---

## ENFORCEMENT RULES

These rules are MANDATORY and hooks will BLOCK violations:

| Violation | Result |
|-----------|--------|
| Missing type prefix | BLOCKED |
| Invalid type | BLOCKED |
| Empty description | BLOCKED |
| Non-imperative mood ("adding X", "fixed Y") | BLOCKED |
| Subject > 100 chars | BLOCKED |
| Subject ends with period | BLOCKED |

**Warnings (flagged but not blocked):**
- Subject 72-100 chars
- Commit > 200 lines
- Commit > 400 lines (strongly recommended to split)
- Missing body on non-trivial commit
- Potential breaking change without ! marker

---

## Red Flags Checklist

Before committing, verify:

- [ ] Type prefix matches the change (feat/fix/refactor/etc.)
- [ ] Description is specific and searchable
- [ ] Breaking changes marked with ! or BREAKING CHANGE: footer
- [ ] Commit > 200 lines? Consider splitting
- [ ] Commit > 400 lines? Must split unless single-file change
- [ ] Refactoring mixed with features? Separate them
- [ ] Tests in separate commit? Combine with code
- [ ] Missing body? Add WHY unless truly trivial
- [ ] Would a new developer understand this in 6 months?

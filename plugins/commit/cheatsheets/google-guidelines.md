# Google Commit Guidelines Quick Reference

Based on [CL Descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html) and [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html).

## The "Git Log Test"

Your subject must pass this test: **A developer skimming `git log --oneline` should understand what this commit does without clicking into it.**

Self-test: "If applied, this commit will _[your subject line]_"

## Commit Message Structure

```
[SUBJECT: Imperative, 50-72 chars, searchable, specific]

[Body: Context and rationale in natural prose]

[Footer: Fixes #N, Related: #M]
```

The body explains WHY, not WHAT. Write naturally without rigid labels.

### Subject Line Rules

- **Imperative mood**: "Add" not "Adding" or "Added"
- **Complete sentence**: Standalone thought, not a fragment
- **Searchable**: Include component/file/function names
- **Specific**: Name what changed, not just that something changed
- **50-72 characters** ideal, max 100, no period at end

### Body: Permanent Historical Context

The body becomes **permanent version control history**. Code shows WHAT; body explains WHY.

**Write naturally, covering these as relevant:**
- What issue or need prompted this change
- Why this approach over alternatives
- Implementation details worth noting
- Known limitations or trade-offs
- Context that survives dead links

**Context Survival Rule**: Write as if every linked document will be deleted.

**NO rigid labels required** - explain naturally in prose, not with `Problem:` / `Solution:` headers.

---

## Examples by Commit Type

### Feature Addition

```
Add rate limiting to auth endpoint

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

### Bug Fix

```
Fix null pointer in UserCache.get() on cache miss

Race condition where async refill returned before initialization
complete. Window was ~50ms during cold-start, causing intermittent
crashes in production.

Added sync barrier between refill task and get() return path to
ensure cache population completes before returning results.

Fixes #789
```

**Why it works:**
- Subject: Exact location + condition
- Explains the mechanism and impact
- Shows root cause analysis
- Links to issue

### Refactoring

```
Refactor validation into ValidationService

Extracts duplicated validation logic from OrderController and
PaymentController into a shared service. Reduces 3 copies to 1
and prepares for per-tenant validation rules in the next commit.

No functional changes - existing tests pass unchanged.
```

**Why it works:**
- Clear "refactoring" signal in subject
- Explains the WHY (preparation + deduplication)
- Explicitly states "no functional changes"

### Configuration

```
Update API rate limits from 100 to 500 req/min

Traffic analysis showed P99 users hitting the 100 req/min limit during
normal usage patterns. Increasing to 500 accommodates legitimate traffic
while still providing protection against abuse.

To rollback: revert this commit and restart pods.
```

**Why it works:**
- Specific values in subject
- Data-driven rationale
- Includes rollback instructions

---

## Bad Subjects (BLOCKED)

| Bad | Problem | Better |
|-----|---------|--------|
| "Fix bug" | Which bug? | "Fix null pointer in UserCache.get()" |
| "Fix build" | What broke? | "Fix missing import in auth_handler" |
| "Update code" | Meaningless | "Update rate limits to 500 req/min" |
| "Refactoring" | What? | "Refactor auth into AuthService class" |
| "Cleanup" | What? | "Remove deprecated v1 API endpoints" |
| "WIP" | Incomplete | "Add rate limiting (pending Redis)" |
| "Phase 1" | Not searchable | "Add rate limiting data models" |
| "CR feedback" | Which? | "Extract helper per review feedback" |
| "Address comments" | Which? | "Fix race condition (per review)" |
| "Misc" / "Stuff" | No info | Be specific |
| "Adding tests" | Which? | "Add payment timeout tests" |
| "Done" / "Ready" | Meaningless | Describe what's done |
| "Final" / "Initial" | Vague | Be specific about what |

---

## Small CLs Rules

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

## CL Splitting Strategies

### When to Split

- 400+ lines -> MUST split
- 200-400 lines -> Consider splitting
- Refactoring + feature -> MUST split
- Multiple independent fixes -> SHOULD split

### Strategies

**1. Stacking (Sequential Dependencies)**
```
Commit 1: Add interface/types
Commit 2: Implement core logic
Commit 3: Migrate consumers
```

**2. Horizontal (By Layer)**
```
Commit 1: Shared types/interfaces
Commit 2: Backend implementation
Commit 3: Frontend/consumer updates
```

**3. Vertical (By Feature)**
```
Commit 1: Add multiplication operator
Commit 2: Add division operator
(NOT: "Add arithmetic operators")
```

**4. By Reviewer Expertise**
```
Commit 1: Database schema (DBA)
Commit 2: Backend logic (engineers)
Commit 3: API contracts (API team)
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
| Vague subject (see table above) | BLOCKED |
| Non-imperative mood ("Adding X", "Fixed Y") | BLOCKED |
| Subject > 100 chars | BLOCKED |
| Missing body on non-trivial commit | BLOCKED |
| Subject ends with period | BLOCKED |
| Refactoring mixed with features | BLOCKED |
| Tests separated from their feature/fix | BLOCKED |

**Warnings (flagged but not blocked):**
- Subject 72-100 chars
- Commit > 200 lines
- Commit > 400 lines (strongly recommended to split)

---

## Red Flags Checklist

Before committing, verify:

- [ ] Commit > 200 lines? Consider splitting
- [ ] Commit > 400 lines? Must split unless single-file change
- [ ] Refactoring mixed with features? Separate them
- [ ] Tests in separate commit? Combine with code
- [ ] Subject vague like "Fix bug"? Be specific
- [ ] Missing body? Add WHY unless truly trivial
- [ ] Would a new developer understand this in 6 months?

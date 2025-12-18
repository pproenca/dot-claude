# Planning Philosophy

## The Golden Rule

**Write plans assuming the executor has zero context and questionable taste.**

This is not insulting the executor - it's acknowledging reality:

- **Zero context:** They haven't read other files, don't know conventions, don't understand the problem domain
- **Questionable taste:** They will take shortcuts if the plan allows it, over-engineer if not constrained, and guess if requirements are vague

**They are skilled developers** who know almost nothing about:

- This codebase's conventions
- The problem domain
- Good test design (see dev-workflow:testing-anti-patterns)
- When to abstract vs duplicate

**They WILL:**
- Take shortcuts if the plan allows it
- Add features if not explicitly forbidden
- Skip steps if they seem optional
- Guess at unclear requirements (wrong 50%+ of the time)

**Your plan must prevent all of this.**

## What to Document

Every task must include:

- Exact file paths (not "update the config")
- Complete code snippets (not "add validation")
- Test commands to run
- Expected output
- Commit message

## Task Granularity

Each task = one TDD cycle (10-30 minutes):

1. Write failing test
2. Run to verify failure
3. Implement minimal code
4. Run to verify pass
5. Commit

## File Organization Rules

**Apply dev-workflow:pragmatic-architecture principles:**

| Rule | Guidance |
|------|----------|
| Rule of Three | Don't create shared utilities until 3rd use |
| Colocation | Keep related code in same file/folder |
| YAGNI | No "for future use" abstractions |
| File Count | ≤3 new files per feature |

**Plan should specify:**
- Why each new file exists (can't be merged elsewhere)
- Where types/utils live (inline preferred over separate files)
- Expected file sizes (flag if <50 lines)

## Quick Reference

| Good                            | Bad              |
| ------------------------------- | ---------------- |
| `src/auth/login.ts:42`          | "the auth file"  |
| `expect(result).toBe(42)`       | "add assertions" |
| `npm test -- --grep "login"`    | "run the tests"  |
| "Returns 401 for invalid token" | "should fail"    |
| Types inline in component       | Separate `types.ts` for 3 types |
| 2 files for feature             | 8 files for feature |

## Anti-Patterns in Plans

Plans should NOT include:

- Abstract base classes without 2+ concrete implementations
- Utility files for single-use functions
- Type-only files (inline types where used)
- "Extensibility" or "plugin" patterns without concrete extensions
- Folders like `types/`, `utils/`, `constants/` that scatter related code

## How to Write for Zero Context

| Vague (Bad) | Specific (Good) |
|-------------|-----------------|
| "Update the auth file" | "Modify `src/auth/login.ts:42-58`" |
| "Add validation" | "Add `if (!email) return { error: 'Email required' }`" |
| "Run the tests" | "Run `pytest tests/auth/test_login.py::test_empty_email -v`" |
| "Should fail" | "Expected: FAIL with `AssertionError: expected 'required' got None`" |
| "Commit your changes" | "Run `git commit -m 'feat(auth): validate empty email'`" |

## Step Timing (2-5 minutes each)

Each step should take 2-5 minutes. If longer, break it down:

**Too big:**
```
Step 1: Implement user authentication
```

**Right size:**
```
Step 1: Write failing test for login with valid credentials (2-5 min)
Step 2: Run test to verify it fails (30 sec)
Step 3: Add login function skeleton (2 min)
Step 4: Run test to verify still fails with correct error (30 sec)
Step 5: Implement password verification (3 min)
Step 6: Run test to verify it passes (30 sec)
Step 7: Commit (30 sec)
```

## Why This Matters

| Plan Quality | Executor Outcome |
|--------------|------------------|
| Vague requirements | 50%+ wrong implementations |
| Missing test commands | Tests skipped or wrong tests run |
| No expected output | Can't tell if test is correct |
| Big steps | Scope creep, lost progress on interrupt |
| "Add validation" | Implementer guesses (wrong) |

**Detailed plans take longer to write but execute faster and more correctly.**

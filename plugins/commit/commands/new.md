---
description: Create a new commit from staged changes following Conventional Commits
argument-hint: ""
allowed-tools: [Bash, Read, Task, AskUserQuestion]
---

# Create New Commit

Create a well-structured commit from currently staged changes using Conventional Commits format.

## Workflow

1. Check staged changes exist
2. Analyze staged diff and detect commit type
3. Check for breaking changes
4. Propose commit message
5. Execute commit

---

## Step 1: Check Staged Changes

```bash
git diff --cached --stat
```

**If nothing staged**: STOP - tell user to stage changes first with `git add`.

---

## Step 2: Analyze Staged Diff and Detect Type

Get the staged changes:

```bash
git diff --cached
```

Get list of changed files:

```bash
git diff --cached --name-only
```

### Type Auto-Detection

Analyze the diff and determine the commit type using this priority order:

| If changes are... | Type | Confidence |
|-------------------|------|------------|
| Only test files (`*_test.*`, `test_*.*`, `tests/`, `__tests__/`) | `test` | HIGH |
| Only documentation (`*.md`, `docs/`, `README*`) | `docs` | HIGH |
| Only CI files (`.github/`, `.gitlab-ci*`, `Jenkinsfile`) | `ci` | HIGH |
| Only build configs (`Makefile`, `*config.*`, `package.json` deps) | `build` | HIGH |
| Contains bug fix patterns (error handling, null checks, edge cases) | `fix` | MODERATE |
| Files renamed/moved, no new exports | `refactor` | MODERATE |
| New files in source directories, new exports/functions | `feat` | MODERATE |
| Everything else | Ask user | LOW |

### Confidence Handling

- **HIGH confidence**: Use detected type, proceed without asking
- **MODERATE confidence**: Show detected type, allow user to change
- **LOW confidence**: Ask user to select type

When confidence is MODERATE or LOW, use AskUserQuestion:

### Type Selection (When Ambiguous)
- Header: "Type"
- Question: "What type of change is this?"
- Options:
  - feat: New feature or capability
  - fix: Bug fix or error correction
  - refactor: Code restructuring (no behavior change)
  - chore: Maintenance or cleanup

---

## Step 3: Check for Breaking Changes

Scan the diff for potential breaking change patterns:

- Removed function/method definitions
- Changed function signatures (added required parameters)
- Removed exports or public APIs
- Removed environment variables or config keys
- Changed return types

If any patterns detected, use AskUserQuestion:

### Breaking Change Confirmation
- Header: "Breaking?"
- Question: "This change appears to [describe detected pattern]. Is this a breaking change?"
- Options:
  - Yes, breaking: Mark with `!` and add BREAKING CHANGE footer
  - No, compatible: Proceed without breaking change marker

---

## Step 4: Propose Commit Message

Based on the analysis, draft a commit message following Conventional Commits:

**Format:**
```
<type>[!]: <description>

[optional body]

[optional BREAKING CHANGE: footer]
```

**Subject rules:**
- Type prefix is REQUIRED (`feat`, `fix`, `docs`, etc.)
- Use `!` before colon for breaking changes
- Description in imperative mood ("add", not "adding")
- Description starts lowercase
- 50-72 chars ideal, max 100
- No period at end

**Body (Context and Rationale):**

The body explains WHY, not WHAT. Write naturally - no rigid labels required.

Include as needed:
- What issue or need prompted this change
- Why this approach was chosen over alternatives
- Any implementation details worth noting
- Known limitations or trade-offs

**Example:**
```
feat: add rate limiting to auth endpoint

Traffic analysis showed credential stuffing attacks hitting 10K+ req/sec.
Token bucket algorithm chosen over sliding window for O(1) memory.
Uses Redis for distributed enforcement across pods.

IPv6 address sharing may cause false positives for shared networks.
```

**Breaking change example:**
```
feat!: remove deprecated v1 API endpoints

The v1 API has been deprecated since 2023-01. This removes all
/api/v1/* endpoints. Clients must migrate to /api/v2/*.

BREAKING CHANGE: All /api/v1/* endpoints removed. Use /api/v2/*.
```

Present the proposed message and validate with AskUserQuestion:

### Message Validation
- Header: "Commit"
- Question: "Does this commit message accurately describe your changes?"
- Options:
  - Looks good: Proceed with this message as-is
  - Change type: I want to use a different type prefix
  - Needs edits: I'll provide corrections to the message
  - Add context: I want to add more details to the body

---

## Step 5: Execute Commit

```bash
git commit -m "$(cat <<'EOF'
[Approved subject]

[Approved body]
EOF
)"
```

Verify with:
```bash
git log -1 --format='%B'
```

---

## Notes

- Validation hooks will automatically check the commit message format
- If the commit is rejected by hooks, review the error and adjust the message
- For complex changes that should be split, suggest using `/commit:reset` instead
- Type prefix is mandatory - commits without valid type will be blocked

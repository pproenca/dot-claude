---
description: Create a new commit from staged changes following Conventional Commits
argument-hint: ""
allowed-tools: [Bash, Read, Task, AskUserQuestion, TodoWrite]
---

# Create New Commit

**Announce at start:** "Creating a commit from staged changes."

## Progress Tracking

Create TodoWrite todos for each step:
- Check staged changes exist
- Analyze diff and detect type
- Check for breaking changes
- Draft and validate commit message
- Execute commit

Mark each step as `in_progress` when starting, `completed` when done.

---

## FIRST ACTION (Mandatory)

Run this command NOW before doing anything else:

```bash
git diff --cached --stat
```

**If no output:** STOP immediately. Tell user: "No staged changes. Run `git add <files>` first."

**If output exists:** Continue to Step 2.

---

## Step 2: Analyze Diff

Run these commands NOW:

```bash
git diff --cached
git diff --cached --name-only
```

Determine commit type using this priority:

| Pattern | Type | Confidence |
|---------|------|------------|
| Only test files (`*_test.*`, `test_*.*`, `tests/`, `__tests__/`) | `test` | HIGH → proceed |
| Only docs (`*.md`, `docs/`, `README*`) | `docs` | HIGH → proceed |
| Only CI files (`.github/`, `.gitlab-ci*`, `Jenkinsfile`) | `ci` | HIGH → proceed |
| Only build configs (`Makefile`, `*config.*`, `package.json` deps) | `build` | HIGH → proceed |
| Bug fix patterns (error handling, null checks, edge cases) | `fix` | MODERATE → ask |
| Files renamed/moved, no new exports | `refactor` | MODERATE → ask |
| New files in source directories, new exports/functions | `feat` | MODERATE → ask |
| Everything else | Ask | LOW → ask |

**For MODERATE confidence:** Show detected type, allow user to confirm or change.

**For LOW confidence:** Ask user to select type.

Use AskUserQuestion with these parameters:

- Header: "Type"
- Question: "I detected this as '[detected_type]'. What type of change is this?"
- Options:
  - Auto-detect: Use Claude's analysis (currently: [detected_type])
  - feat: New feature or capability
  - fix: Bug fix or error correction
  - refactor: Code restructuring (no behavior change)
  - chore: Maintenance or cleanup
- multiSelect: false

---

## Step 3: Check Breaking Changes

Scan diff for these patterns:
- Removed function/method definitions
- Changed function signatures (added required parameters)
- Removed exports or public APIs
- Removed environment variables or config keys
- Changed return types

**If patterns detected,** use AskUserQuestion with these parameters:

- Header: "Breaking?"
- Question: "This appears to [describe pattern]. Is this a breaking change?"
- Options:
  - Yes, breaking: Mark with ! and BREAKING CHANGE footer
  - No, compatible: Proceed without breaking marker
- multiSelect: false

---

## Step 4: Draft Message

Draft commit message following Conventional Commits:

**Format:** type[!]: description

**Rules:**
- Type prefix is REQUIRED (feat, fix, docs, etc.)
- Use exclamation mark (!) before colon for breaking changes
- Description in imperative mood ("add", not "adding")
- Description starts lowercase
- 50-72 chars ideal, max 100
- No period at end

**Body (for non-trivial changes):**
- Explains WHY, not WHAT
- What issue prompted this change
- Why this approach was chosen
- Known limitations or trade-offs

Present the message and validate with AskUserQuestion:

- Header: "Commit"
- Question: "Does this message accurately describe your changes?"
- Options:
  - Looks good: Proceed as-is
  - Change type: Use different type prefix
  - Needs edits: I'll provide corrections
  - Add context: Add more details to body
- multiSelect: false

---

## Step 5: Execute Commit

**Single-line commits (no body):**
```bash
git commit -m 'type: description'
```

**Multi-line commits (with body):**
```bash
printf '%b' 'type: subject line\n\nBody text explaining why.' | git commit -F -
```

**Breaking changes:**
```bash
printf '%b' 'feat!: remove deprecated API\n\nMigration required for all v1 clients.\n\nBREAKING CHANGE: /api/v1/* endpoints removed.' | git commit -F -
```

**Critical:** Use single-quoted strings with `\n` escape sequences. The `printf '%b'` interprets escapes at runtime.

Verify with:
```bash
git log -1 --format='%B'
```

---

## Notes

- Use single quotes for commit messages to prevent shell expansion of exclamation marks
- Validation hooks will automatically check the commit message format
- For complex changes that should be split, suggest using /commit:reset instead

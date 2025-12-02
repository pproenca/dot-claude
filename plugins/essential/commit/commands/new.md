---
description: Create a new commit from staged changes following Conventional Commits
argument-hint: ""
allowed-tools: [Bash, Read, AskUserQuestion]
---

# Create New Commit

**Announce at start:** "Creating a commit from staged changes."

---

## Step 1: Check Staged Changes

Run this command NOW:

```bash
git diff --cached --stat
```

**If no output:** STOP. Tell user: "No staged changes. Run `git add <files>` first."

**If output exists:** Continue.

---

## Step 2: Analyze and Draft

Run these commands:

```bash
git diff --cached
git diff --cached --name-only
```

### Determine Type

| Pattern | Type |
|---------|------|
| Only test files (`*_test.*`, `test_*.*`, `tests/`, `__tests__/`) | `test` |
| Only docs (`*.md`, `docs/`, `README*`) | `docs` |
| Only CI files (`.github/`, `.gitlab-ci*`, `Jenkinsfile`) | `ci` |
| Only build configs (`Makefile`, `*config.*`, `package.json` deps) | `build` |
| Bug fix patterns (error handling, null checks, edge cases) | `fix` |
| Files renamed/moved, no new exports | `refactor` |
| New files in source directories, new exports/functions | `feat` |

Pick the best-fit type. Only ask the user if two types are **genuinely equally valid** (e.g., changes both add a feature AND fix a bug).

### Check Breaking Changes

Scan for these patterns:
- Removed function/method definitions
- Changed function signatures (added required parameters)
- Removed exports or public APIs
- Changed return types

If detected, mark as breaking change (add ! and footer). Do not ask—show in the message.

### Draft Message

**Format:** `type[!]: description`

**Rules:**
- Type prefix required (feat, fix, docs, etc.)
- ! before colon for breaking changes
- Imperative mood ("add", not "adding")
- Lowercase description
- 50-72 chars ideal, max 100
- No period at end

**Body (for non-trivial changes):**
- Explains WHY, not WHAT
- What issue prompted this
- Why this approach

---

## Step 3: Confirm and Execute

Present the complete commit message and ask:

- Header: "Commit"
- Question: "Ready to commit with this message?"
- Options:
  - Commit: Execute this commit now
  - Edit: I'll provide corrections
  - Split: Break into multiple commits
  - Cancel: Abort without committing
- multiSelect: false

### If "Commit"

**Single-line:**
```bash
git commit -F - <<'EOF'
type: description
EOF
```

**Multi-line:**
```bash
git commit -F - <<'EOF'
type: subject

Body text.
EOF
```

**Breaking changes:**
```bash
git commit -F - <<'EOF'
feat!: remove deprecated API

BREAKING CHANGE: description.
EOF
```

Verify with:
```bash
git log -1 --format='%B'
```

### If "Edit"

Apply user's corrections and re-present.

### If "Split"

Tell user:
- To split: `git reset HEAD <files>` to unstage some files, then run `/commit:new` for each logical commit
- For complex reorganization: use `/commit:reset`

### If "Cancel"

Stop without committing.

---

## Notes

- Use heredoc with quoted delimiter (`<<'EOF'`) for commit messages (prevents all shell expansion including !)
- Validation hooks will check the format

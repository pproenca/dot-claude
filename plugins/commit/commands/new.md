---
description: Create a new commit from staged changes following Google's practices
argument-hint: ""
allowed-tools: [Bash, Read, Task, AskUserQuestion]
---

# Create New Commit

Create a well-structured commit from currently staged changes.

## Workflow

1. Check staged changes exist
2. Analyze staged diff
3. Propose commit message
4. Execute commit

---

## Step 1: Check Staged Changes

```bash
git diff --cached --stat
```

**If nothing staged**: STOP - tell user to stage changes first with `git add`.

---

## Step 2: Analyze Staged Diff

Get the staged changes:

```bash
git diff --cached
```

Analyze the diff and classify the change:
- **Type**: Feature / Bug Fix / Refactoring / Config
- **Scope**: Single concern? Multiple concerns that should be split?
- **Size**: ~100 lines ideal, 400+ consider splitting

If changes should be split, suggest user unstage some files and commit separately.

---

## Step 3: Propose Commit Message

Based on the diff analysis, draft a commit message following Google's practices:

**Subject (Git Log Test):**
- Imperative mood ("Add", not "Adding")
- 50-72 chars, max 100
- Specific and searchable
- Must stand alone in `git log --oneline`

**Body (Context and Rationale):**

The body explains WHY, not WHAT. Write naturally - no rigid labels required.

Include as needed:
- What issue or need prompted this change
- Why this approach was chosen over alternatives
- Any implementation details worth noting
- Known limitations or trade-offs

Example:
```
Add rate limiting to auth endpoint

Traffic analysis showed credential stuffing attacks hitting 10K+ req/sec.
Token bucket algorithm chosen over sliding window for O(1) memory.
Uses Redis for distributed enforcement across pods.

IPv6 address sharing may cause false positives for shared networks.
```

Present the proposed message and validate with AskUserQuestion:

### Message Validation
- Header: "Commit"
- Question: "Does this commit message accurately describe your changes?"
- Options:
  - Looks good: Proceed with this message as-is
  - Needs edits: I'll provide corrections to the message
  - Add context: I want to add more details to the body

---

## Step 4: Execute Commit

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
- For complex changes that should be split, suggest using `/commits:reset` instead

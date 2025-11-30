---
description: Reset and reorganize commits following Conventional Commits
argument-hint: ""
allowed-tools: [Bash, Read, Task, AskUserQuestion, TodoWrite]
---

# Commit History Reset and Organization

Reorganize git commits following Conventional Commits specification.

Commit message validation runs automatically via hooks.

## Workflow

1. Safety check and backup
2. Dispatch commit-organizer agent for analysis
3. Review and approve proposed organization
4. Execute commits
5. Verify

---

## Step 1: Safety Check and Backup

```bash
git rev-parse --git-dir && git branch --show-current && git status --porcelain
```

**If uncommitted changes**: STOP - user must commit or stash first.

**Create backup**:

```bash
BACKUP_BRANCH="backup/$(git branch --show-current)-$(date +%Y%m%d-%H%M%S)"
git branch $BACKUP_BRANCH
echo "Backup: $BACKUP_BRANCH"
```

---

## Step 2: Dispatch Commit-Organizer Agent

Use the Task tool with `subagent_type="commits:commit-organizer"` to analyze the branch.

The agent will:
- Run `${CLAUDE_PLUGIN_ROOT}/scripts/analyze-branch.sh` to get full diffs
- Read ALL diffs holistically (cumulative change, not individual commits)
- Classify changes (refactoring/fix/feature/config)
- Apply Conventional Commits rules (separation, size limits, self-containment)
- Propose commit organization with draft messages

**Prompt for the agent:**
```
Analyze this branch and propose a commit organization following Conventional Commits specification.

For each proposed commit, provide:
- Files and line count
- Proposed subject (passes "Git Log Test")
- Proposed body (Problem/Solution format)
- Reasoning for this grouping
```

The agent will return a detailed commit organization plan.

---

## Step 3: Review Agent's Proposal

Present the agent's proposed commit organization to the user.

Use AskUserQuestion to confirm the proposed organization:

### Organization Approval
- Header: "Plan"
- Question: "Do you approve this commit organization?"
- Options:
  - Approve: Proceed with this organization
  - Adjust groupings: I want to change how files are grouped into commits
  - Edit messages: The groupings are fine but I want to adjust commit messages
  - Rethink: Start over with different organization criteria

**DO NOT proceed until user approves the plan.**

---

## Step 4: Execute Commits

1. Create TodoWrite list with each commit as an item

2. Soft reset to branch point:

```bash
git reset --soft $BRANCH_POINT
```

3. For EACH commit in the approved plan:

```bash
# Stage ONLY the files for this commit
git add [specific files]
git status  # Verify only intended files staged

# Create commit with agent's proposed message
git commit -m "$(cat <<'EOF'
[Agent's proposed subject]

[Agent's proposed body]
EOF
)"
```

4. Mark todo complete ONLY after commit succeeds and passes validation hooks

---

## Step 5: Verify

```bash
git log --oneline $BRANCH_POINT..HEAD
git log --stat $BRANCH_POINT..HEAD
git status
```

Check that:
- Each commit is self-contained
- Commit order makes sense (dependencies first)
- Messages explain WHY, not just WHAT

---

## Recovery

If anything goes wrong:

```bash
git reset --hard $BACKUP_BRANCH
```

---

## Notes

- **Do not push automatically** - let user review first
- **Safety hooks** block dangerous operations without backup
- **Commit validation** happens automatically via PostToolUse hooks
- **Guidelines** - refer to cheatsheet for Conventional Commits details

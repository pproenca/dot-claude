# Phase: SYNTHESIZE

## Purpose
Merge all work, finalize state, and complete the orchestration.

## Activities

### 1. Collect All Artifacts

Read artifacts from each completed task:
```bash
ls .claude/artifacts/
cat .claude/artifacts/task-*.md
```

### 2. Verify Interface Compatibility

Check that:
- Consumer inputs match provider outputs
- No type mismatches between modules
- All dependencies satisfied

### 3. Merge Worktree Branches

From the main repository:
```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"

# Merge each task branch
git checkout main
git merge task-a-component --no-edit
git merge task-b-service --no-edit
git merge task-c-api --no-edit
```

### 4. Clean Up Worktrees

```bash
worktree_remove "task-a-component" --delete-branch
worktree_remove "task-b-service" --delete-branch
worktree_remove "task-c-api" --delete-branch
```

### 5. Final Verification

Run full verification in main repo:
```bash
uv run pytest -v
ty check
uv run ruff check .
```

### 6. Update External State

```bash
# Mark all tasks complete in todo.md
sed -i '' 's/PENDING/DONE/g' todo.md
# Or for checkbox format:
sed -i '' 's/\[ \]/[x]/g' todo.md

# Update progress.txt
cat > progress.txt << 'EOF'
=== Session State ===
Status: COMPLETE
All tasks: Done
Verification: Passed

=== Summary ===
[Brief summary of what was implemented]

=== Files Modified ===
[List from artifacts]
EOF
```

And sync TodoWrite:
```
TodoWrite([
  {content: "Task A", status: "completed", ...},
  {content: "Task B", status: "completed", ...},
  ...
])
```

### 7. Set Phase to COMPLETE

```bash
echo "COMPLETE" > "${STATE_DIR}/workflow-phase"
```

### 8. Report to User

Provide completion summary:
- What was implemented
- Files modified
- Test coverage
- Any notes for follow-up

## If Issues During Merge

If merge conflicts occur:
1. Resolve conflicts in main repo
2. Re-run tests
3. If issues persist, create remediation task and return to DELEGATE

## Constraints
- All merges must be non-destructive
- Final tests must pass
- State files must be updated
- Worktrees must be cleaned up

## Completion Checklist

Before claiming done:
- [ ] All worktree branches merged to main
- [ ] All worktrees removed
- [ ] todo.md shows all DONE
- [ ] progress.txt updated
- [ ] .claude/workflow-phase shows COMPLETE
- [ ] Final tests pass in main repo
- [ ] User notified of completion

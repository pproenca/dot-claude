---
description: Manage git worktrees for isolated agent work - create, remove, list, or cleanup worktrees
argument-hint: [create|remove|list|cleanup|status] [branch-name]
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# /worktree - Git Worktree Management

Manage git worktrees for isolating subagent work. Worktrees are stored at `~/.dot-claude-worktrees/<project>--<branch>`.

## Input

Action: $ARGUMENTS
- `create <branch>` - Create a new worktree for a task
- `remove [branch]` - Remove a worktree (current or specified)
- `list` - List all worktrees for this project
- `cleanup` - Remove stale/old worktrees
- `status` (default) - Show current worktree context

## Setup

First, source the worktree utilities:
```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
```

## Actions

### status (default)

Show current worktree context:

```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"

if worktree_is_worktree; then
    echo "## Current Worktree"
    echo "Name: $(worktree_current)"
    echo "Branch: $(worktree_current_branch)"
    echo "Path: $(pwd)"
    echo "Main repo: $(worktree_main_repo)"
else
    echo "## Main Repository"
    echo "Project: $(worktree_project_name)"
    echo "Path: $(pwd)"
fi

echo ""
echo "## State Directory"
echo "$(worktree_state_dir)"

echo ""
echo "## All Worktrees"
worktree_list
```

### create <branch>

Create a new worktree:

1. **Parse branch name** from arguments
2. **Validate** branch name (no spaces, valid git ref)
3. **Create worktree**:
   ```bash
   source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
   wt_path=$(worktree_create "<branch-name>")
   ```
4. **Report**:
   ```
   Created worktree: ~/.dot-claude-worktrees/<project>--<branch>

   To switch to this worktree:
   cd <wt_path>

   State files will be stored at:
   <wt_path>/.claude/
   ```

### remove [branch]

Remove a worktree:

1. **Determine target**:
   - If branch specified: use that
   - If in worktree: use current worktree's branch
   - If in main repo with no arg: error

2. **Confirm removal** using AskUserQuestion:
   ```
   AskUserQuestion({
     questions: [{
       question: "Remove worktree '<project>--<branch>'? This will delete the worktree directory but preserve the branch.",
       header: "Remove",
       multiSelect: false,
       options: [
         {
           label: "Remove worktree only (Recommended)",
           description: "Delete worktree directory, keep the git branch"
         },
         {
           label: "Remove worktree and branch",
           description: "Delete both worktree and the git branch"
         },
         {
           label: "Cancel",
           description: "Don't remove anything"
         }
       ]
     }]
   })
   ```

Handle responses:
- "Remove worktree only" → Delete worktree directory, keep branch
- "Remove worktree and branch" → Delete both worktree and git branch
- "Cancel" → Exit without action
- "Other" (custom input) → Process user's custom request

**Error Handling**: If AskUserQuestion fails or returns empty/invalid response:
- Report: "Unable to process response. Cancelling removal for safety."
- Fallback: Do not remove anything, ask user to confirm manually

3. **Execute**:
   ```bash
   source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
   # Based on user choice:
   worktree_remove "<branch>"              # worktree only
   worktree_remove "<branch>" --delete-branch  # both
   ```

4. **If in removed worktree**: cd back to main repo

### list

List all worktrees:

```bash
source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
worktree_list
```

Display format:
```
## Worktrees for project: myapp
Location: ~/.dot-claude-worktrees

/Users/pedro/Projects/myapp                    abc1234 [main]
~/.dot-claude-worktrees/myapp--feature-auth    def5678 [feature-auth]
~/.dot-claude-worktrees/myapp--fix-bug         ghi9012 [fix-bug]

Total: 3 worktrees (1 main + 2 task worktrees)
```

### cleanup

Clean up stale worktrees:

1. **List candidates**:
   ```bash
   source "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/worktree-utils.sh"
   worktree_list
   ```

2. **Ask what to clean** using AskUserQuestion:
   ```
   AskUserQuestion({
     questions: [{
       question: "Which worktrees should be cleaned up?",
       header: "Cleanup",
       multiSelect: false,
       options: [
         {
           label: "Prune stale only (Recommended)",
           description: "Remove worktrees with missing directories (git worktree prune)"
         },
         {
           label: "Remove all task worktrees",
           description: "Remove all worktrees in ~/.dot-claude-worktrees for this project"
         },
         {
           label: "Select specific worktrees",
           description: "Choose which worktrees to remove"
         },
         {
           label: "Cancel",
           description: "Don't clean up anything"
         }
       ]
     }]
   })
   ```

Handle responses:
- "Prune stale only" → `worktree_cleanup`
- "Remove all task worktrees" → Remove each worktree in WORKTREE_BASE for this project
- "Select specific worktrees" → Follow up with list of worktrees to select
- "Cancel" → Exit without changes
- "Other" (custom input) → Process user's custom request

**Error Handling**: If AskUserQuestion fails or returns empty/invalid response:
- Report: "Unable to process response. Cancelling cleanup for safety."
- Fallback: Do not clean up anything, ask user to confirm manually

## Examples

### Create worktree for a task
```
/worktree create auth-service

Created worktree: ~/.dot-claude-worktrees/myapp--auth-service
Branch: auth-service (from HEAD)

To switch:
cd ~/.dot-claude-worktrees/myapp--auth-service

State files at:
~/.dot-claude-worktrees/myapp--auth-service/.claude/
```

### Check current context
```
/worktree status

## Current Worktree
Name: myapp--auth-service
Branch: auth-service
Path: ~/.dot-claude-worktrees/myapp--auth-service
Main repo: /Users/pedro/Projects/myapp

## State Directory
~/.dot-claude-worktrees/myapp--auth-service/.claude

## All Worktrees
/Users/pedro/Projects/myapp                     abc1234 [main]
~/.dot-claude-worktrees/myapp--auth-service     def5678 [auth-service]
```

### List all worktrees
```
/worktree list

## Worktrees for project: myapp
Location: ~/.dot-claude-worktrees

/Users/pedro/Projects/myapp                    abc1234 [main]
~/.dot-claude-worktrees/myapp--auth-service    def5678 [auth-service]
~/.dot-claude-worktrees/myapp--fix-validation  ghi9012 [fix-validation]

Total: 3 worktrees
```

### Remove a worktree
```
/worktree remove auth-service

[AskUserQuestion: Remove worktree 'myapp--auth-service'?]
User selects: "Remove worktree and branch"

Removing worktree: ~/.dot-claude-worktrees/myapp--auth-service
Deleting branch: auth-service

Worktree removed.
```

## Environment Variables

- `DOT_CLAUDE_WORKTREES`: Override default worktree location (default: `~/.dot-claude-worktrees`)

## Notes

- Worktrees share the same git history but have isolated working directories
- Each worktree can have its own `.claude/` state directory
- Changes in a worktree can be merged back to main using `git merge` from main repo
- Use `/orchestrate` to automatically create worktrees for subagents

---
description: Show current project context for resuming work
allowed-tools: Read, Bash(git:*)
---

Read CLAUDE.md if it exists and summarize:
1. Project overview
2. Current focus / active tasks
3. Recent context notes

Also run these git commands to show current state:
- `git log --oneline -5` - Last 5 commits
- `git status --short` - Current changes

Present as a quick status update for resuming work on this project.

---
name: standup
description: Generate standup update from recent work and priorities
allowed-tools:
  - Read
  - Bash
  - Glob
argument-hint: "[optional: 'async' for written format, 'verbal' for talking points]"
---

# Standup Generator

Generate a standup update based on recent commits and priorities.

## Process

### 1. Gather Data

Collect information from multiple sources:

**Recent commits (yesterday/today):**
```bash
git log --oneline --since="yesterday" --author="$(git config user.name)" 2>/dev/null | head -10
```

**Today's priorities:**
Read `.pm/me/today.md` for current focus.

**Recent PR activity:**
```bash
gh pr list --author="@me" --state=all --limit=5 2>/dev/null || echo "gh not available"
```

### 2. Determine Format

If argument is "async" → Written format for Slack/email
If argument is "verbal" → Bullet points for speaking
Default → Concise written format

### 3. Generate Update

Structure the standup:

**Yesterday (What I did)**
- Summarize commits into meaningful work items
- Group related commits
- Mention PRs merged or reviewed

**Today (What I'm doing)**
- Pull from today.md Must Do items
- Mention any meetings or reviews
- Focus on deliverables

**Blockers (What's in my way)**
- From today.md Notes section
- Any dependencies on others
- Escalations needed

### 4. Output Format

**Async (Slack/written):**
```markdown
**Yesterday:**
- Shipped [feature] (PR #123)
- Reviewed [teammate]'s auth PR

**Today:**
- Finishing [current task]
- Starting [next task]

**Blockers:**
- Waiting on [thing] from [person]
```

**Verbal (talking points):**
```
Yesterday:
• Shipped the auth changes
• Did code reviews

Today:
• Wrapping up the API migration
• Starting on tests

Blockers:
• Need API key from infra
```

### 5. Quick Summary

Provide a one-liner version for quick updates:
> "Yesterday: shipped auth. Today: API migration. Blocked on infra API key."

## Tips

- Keep it under 30 seconds to read
- Focus on outcomes, not tasks
- Be specific about blockers
- No fluff - busy people will read this

---
name: today
description: Morning ritual - review and set daily priorities
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
argument-hint: "[optional: specific focus or context]"
---

# Daily Priority Setting

Guide the user through their morning priority-setting ritual.

## Process

### 1. Check Current State

First, check if `.pm/` structure exists:

```bash
ls -la .pm/me/ 2>/dev/null || echo "PM structure not found"
```

If not found, offer to initialize:

```bash
mkdir -p .pm/me .pm/team/epics .pm/archive
```

### 2. Read Yesterday's Priorities

Read `.pm/me/today.md` if it exists. Note:
- What was completed (checked items)
- What's still open (unchecked items)
- Any notes or blockers

### 3. Gather Context

Check recent activity:
- `git log --oneline -5` for recent commits
- Any open PRs or reviews needed
- Calendar context if user mentions meetings

### 4. Set Today's Priorities

Help the user define 3-5 priorities:

**Must Do** (1-2 items)
- Critical path items
- Deadlines today
- Blocking others

**Should Do** (2-3 items)
- Important but not urgent
- Progress on current epic
- Reviews and feedback

Ask clarifying questions:
- "What's the most important thing to ship today?"
- "Is anyone blocked on you?"
- "Any meetings that need prep?"

### 5. Write today.md

Update `.pm/me/today.md` with the format:

```markdown
# Today - [DATE]

## Must Do
- [ ] [Priority 1]
- [ ] [Priority 2]

## Should Do
- [ ] [Priority 3]
- [ ] [Priority 4]

## Notes
[Any blockers, context, or reminders]
```

### 6. Quick Check

After writing, summarize:
- "You have X priorities for today"
- "Top focus: [Must Do #1]"
- Any blockers to escalate

## Tips

- Keep it short - 5 minutes max
- Don't over-plan - 3-5 items is ideal
- Carry over unfinished items thoughtfully
- Note blockers explicitly

---
name: week
description: Weekly planning - reflect on the week and plan ahead
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
argument-hint: "[optional: 'review' for end-of-week, 'plan' for start-of-week]"
---

# Weekly Planning Session

Guide the user through weekly planning - either reviewing the past week or planning the next.

## Determine Mode

If argument is "review" → End-of-week reflection
If argument is "plan" → Start-of-week planning
If no argument → Ask which mode or do both

## Process

### 1. Check Current State

Read `.pm/me/week.md` if it exists. Note current focus areas and progress.

### 2. Gather Week's Activity

```bash
# Commits this week
git log --oneline --since="1 week ago" --author="$(git config user.name)" | head -20

# Files changed
git diff --stat HEAD~20 --name-only 2>/dev/null | head -10
```

### 3. End-of-Week Review (Friday)

Help the user reflect:

**What got done?**
- Review completed items
- Celebrate wins explicitly
- Note what shipped

**What didn't happen?**
- Uncompleted items - why?
- Should they carry over?
- Any patterns?

**Blockers encountered?**
- What slowed progress?
- Still blocked or resolved?
- Need escalation?

### 4. Start-of-Week Planning (Monday)

Help set the week's focus:

**Focus Areas (max 3)**
- What are the big rocks?
- What must ship this week?
- What would make this week successful?

**Key Deliverables**
- Concrete, measurable items
- Tied to focus areas
- Realistically achievable

**Dependencies**
- What do you need from others?
- Who needs things from you?

### 5. Write week.md

Update `.pm/me/week.md`:

```markdown
# Week [NUMBER] - [DATE RANGE]

## Focus Areas
1. [Focus 1]
2. [Focus 2]
3. [Focus 3]

## Key Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

## Wins
- [Win from this week]

## Blockers
- [Current blocker and status]

## Notes
[Any context, upcoming PTO, important meetings]
```

### 6. Update Roadmap Connection

Check if weekly focus aligns with `.pm/team/roadmap.md`:
- Are focus areas connected to current epics?
- Any roadmap updates needed?

## Tips

- 15 minutes max
- Be honest about capacity
- 3 focus areas, not 10
- Wins matter - write them down

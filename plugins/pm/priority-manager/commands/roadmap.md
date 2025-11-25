---
name: roadmap
description: Review and update team roadmap and epics
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
argument-hint: "[optional: epic name to focus on, or 'status' for overview]"
---

# Roadmap Management

Help the user review and update the team roadmap.

## Process

### 1. Load Current State

Read roadmap and epics:

```bash
# Check structure
ls -la .pm/team/ 2>/dev/null
ls -la .pm/team/epics/ 2>/dev/null
```

Read `.pm/team/roadmap.md` for high-level view.
Read epic files in `.pm/team/epics/` for details.

### 2. Determine Focus

If argument is an epic name → Focus on that epic
If argument is "status" → Give overview only
If no argument → Interactive review

### 3. Status Overview

Summarize current state:

**Now (In Progress)**
- List active epics with % complete
- Highlight any at risk

**Next (Planned)**
- What's coming up
- Dependencies or blockers

**Key Dates**
- Upcoming milestones
- Deadlines this month

### 4. Epic Deep Dive (if focused)

For a specific epic, review:

**Status**
- Current progress %
- On track or at risk?

**Recent Updates**
- What changed since last review?
- Any new decisions?

**Blockers**
- What's slowing progress?
- Who can unblock?

**Next Steps**
- What's the next milestone?
- Who owns it?

### 5. Update Files

Based on discussion, update:

**roadmap.md** - High-level changes:
- Move items between Now/Next/Later
- Update key dates
- Add new initiatives

**Epic files** - Detailed changes:
- Update status and %
- Add decisions with dates
- Update milestones

### 6. Write Updates

Use consistent format for roadmap.md:

```markdown
# Team Roadmap

## Q[N] [YEAR]

### Now (In Progress)
- **[Epic Name]** - [One-line description] [[file].md]

### Next (Planned)
- [Initiative name]

### Later (Backlog)
- [Future item]

## Key Dates
- [Date]: [Milestone]
```

Use consistent format for epics:

```markdown
# [Epic Name]

## Status: [In Progress/Planned/Complete] ([X]%)

## Overview
[2-3 sentences]

## Goals
- [Goal 1]
- [Goal 2]

## Milestones
- [x] [Completed milestone]
- [ ] [Upcoming milestone]

## Decisions
- [DATE]: [Decision made and rationale]

## Open Questions
- [Question needing resolution]
```

### 7. Archive Completed

If epic is 100% complete:
- Move to `.pm/archive/`
- Update roadmap.md to remove from Now
- Celebrate the win!

## Tips

- Review weekly, update as needed
- Keep roadmap.md scannable (one screen)
- Epic files have the details
- Date your decisions
- Archive, don't delete

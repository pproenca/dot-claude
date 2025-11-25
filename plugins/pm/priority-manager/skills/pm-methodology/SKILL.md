---
name: PM Methodology
description: This skill should be used when the user asks about "priority management", "roadmap structure", "pm file format", "how to organize priorities", or needs to understand the .pm/ directory structure and methodology for managing personal and team priorities.
---

# PM Methodology

A git-based system for managing personal priorities and team roadmaps using markdown files. Inspired by Unix philosophy: simple, composable, human-readable.

## Core Philosophy

- **Markdown everything** - Human-readable, git-friendly, portable
- **Minimal structure** - Only what's needed, nothing more
- **Daily ritual** - Small, consistent habits over complex systems
- **Team visibility** - Roadmaps live alongside code

## File Structure

All PM data lives in `.pm/` at the project root:

```
.pm/
├── me/                   # Personal priorities
│   ├── today.md          # Today's 3-5 priorities
│   ├── week.md           # This week's focus
│   └── goals.md          # Quarterly goals
├── team/                 # Team roadmap
│   ├── roadmap.md        # High-level overview
│   └── epics/            # One file per epic
│       └── [epic-name].md
└── archive/              # Completed work (optional)
```

## File Formats

### today.md

Daily priorities. Keep to 3-5 items maximum. Update every morning.

```markdown
# Today - 2025-01-15

## Must Do
- [ ] Ship auth PR
- [ ] Review team PRs

## Should Do
- [ ] Update roadmap with Q1 dates
- [ ] 1:1 prep for Sarah

## Notes
Blocked on API key from infra team.
```

### week.md

Weekly focus areas. Review on Monday, update Friday.

```markdown
# Week 3 - Jan 13-17

## Focus Areas
1. Auth v2 launch
2. Q1 planning finalization
3. Team hiring (2 interviews)

## Key Deliverables
- [ ] Auth v2 in production
- [ ] Q1 roadmap signed off
- [ ] Interview feedback submitted

## Wins
- Shipped performance fix (2x faster)

## Blockers
- Waiting on security review
```

### goals.md

Quarterly or longer-term personal goals.

```markdown
# Q1 2025 Goals

## Professional
1. Ship 3 major features
2. Mentor 2 junior engineers
3. Reduce on-call incidents by 50%

## Growth
1. Present at team all-hands
2. Complete system design course

## Progress
- Auth v2: 80% complete
- Mentoring: Started with Alex and Jordan
```

### roadmap.md

High-level team roadmap. Single source of truth.

```markdown
# Team Roadmap

## Q1 2025

### Now (In Progress)
- **Auth v2** - New authentication system [auth-v2.md]
- **Performance** - 2x latency reduction [performance.md]

### Next (Planned)
- API v3 migration
- Dashboard redesign

### Later (Backlog)
- Mobile app
- Enterprise SSO

## Key Dates
- Jan 31: Auth v2 launch
- Feb 15: Q1 midpoint review
- Mar 31: Q1 end
```

### Epic Files (epics/*.md)

One file per epic. Contains details, status, and decisions.

```markdown
# Auth v2

## Status: In Progress (80%)

## Overview
Replace legacy auth with OAuth 2.0 + JWT tokens.

## Goals
- Improve security posture
- Enable SSO integration
- Reduce auth-related incidents

## Milestones
- [x] Design review
- [x] Core implementation
- [ ] Security audit
- [ ] Production rollout

## Decisions
- 2025-01-10: Using Auth0 over custom solution
- 2025-01-05: JWT with 1hr expiry, refresh tokens

## Open Questions
- Migration path for existing sessions?
```

## Workflows

### Morning Ritual (5 min)

1. Open `.pm/me/today.md`
2. Archive yesterday's completed items
3. Set 3-5 priorities for today
4. Check `.pm/team/roadmap.md` for blockers

### Weekly Planning (15 min)

1. Review `.pm/me/week.md` - what got done?
2. Update wins and blockers
3. Set next week's focus areas
4. Update `.pm/team/roadmap.md` status

### Standup Prep (2 min)

Generate from recent commits and today.md:
- What did you do yesterday?
- What are you doing today?
- Any blockers?

### Roadmap Review

1. Open `.pm/team/roadmap.md`
2. Update Now/Next/Later sections
3. Update epic files with current status
4. Archive completed epics

## Best Practices

### Keep It Small
- today.md: 3-5 items
- week.md: 3 focus areas
- roadmap.md: Fits on one screen

### Update Frequently
- today.md: Every morning
- week.md: Monday and Friday
- roadmap.md: Weekly

### Use Git
- Commit PM changes with code
- History shows priority evolution
- Team can see roadmap changes

### Archive, Don't Delete
- Move completed epics to archive/
- Keep history for retrospectives
- Git blame shows decisions

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/pm:today` | Morning ritual - set daily priorities |
| `/pm:week` | Weekly planning session |
| `/pm:roadmap` | Review and update team roadmap |
| `/pm:standup` | Generate standup from recent work |

## Getting Started

Initialize the structure:

```bash
mkdir -p .pm/me .pm/team/epics .pm/archive
touch .pm/me/today.md .pm/me/week.md .pm/me/goals.md
touch .pm/team/roadmap.md
```

Start with today.md. Add other files as needed.

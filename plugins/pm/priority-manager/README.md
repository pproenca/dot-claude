# pm

Personal and team priority management with git-based markdown files.

## Philosophy

- **Markdown everything** - Human-readable, git-friendly, portable
- **Minimal structure** - Only what's needed
- **Daily ritual** - Small, consistent habits
- **Unix-style** - Simple, composable commands

## Quick Start

```bash
# Initialize structure in your project
mkdir -p .pm/me .pm/team/epics .pm/archive

# Start your day
/pm:today

# Weekly planning
/pm:week

# Review roadmap
/pm:roadmap

# Generate standup
/pm:standup
```

## File Structure

```
.pm/
├── me/
│   ├── today.md      # Daily priorities (3-5 items)
│   ├── week.md       # Weekly focus areas
│   └── goals.md      # Quarterly goals
├── team/
│   ├── roadmap.md    # High-level roadmap
│   └── epics/        # One file per epic
└── archive/          # Completed work
```

## Commands

| Command | Purpose |
|---------|---------|
| `/pm:today` | Morning ritual - set daily priorities |
| `/pm:week` | Weekly planning session |
| `/pm:roadmap` | Review and update team roadmap |
| `/pm:standup` | Generate standup from recent work |

## Usage

### Morning Ritual (5 min)

```
/pm:today
```

Sets 3-5 priorities. Reviews yesterday. Gets you focused.

### Weekly Planning (15 min)

```
/pm:week review    # Friday - reflect on the week
/pm:week plan      # Monday - set the week's focus
/pm:week           # Interactive - both
```

### Roadmap Updates

```
/pm:roadmap                # Full review
/pm:roadmap auth-v2        # Focus on specific epic
/pm:roadmap status         # Quick overview
```

### Standup

```
/pm:standup          # Written format
/pm:standup async    # Slack/email format
/pm:standup verbal   # Talking points
```

## Example Files

### today.md

```markdown
# Today - 2025-01-15

## Must Do
- [ ] Ship auth PR
- [ ] Review team PRs

## Should Do
- [ ] Update roadmap
- [ ] 1:1 prep

## Notes
Blocked on API key from infra.
```

### roadmap.md

```markdown
# Team Roadmap

## Q1 2025

### Now (In Progress)
- **Auth v2** - New auth system [auth-v2.md]

### Next (Planned)
- API v3 migration

### Later (Backlog)
- Mobile app

## Key Dates
- Jan 31: Auth v2 launch
```

## Best Practices

1. **Keep it small** - 3-5 daily items, 3 weekly focus areas
2. **Update frequently** - today.md every morning
3. **Commit with code** - PM changes go in git
4. **Archive, don't delete** - History matters

## License

MIT

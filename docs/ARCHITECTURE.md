# Architecture

This document describes the architecture of dot-claude, a modular plugin system for Claude Code.

## System Overview

```mermaid
graph TB
    subgraph "Claude Code Runtime"
        CC[Claude Code CLI]
        PM[Plugin Manager]
        HE[Hook Engine]
        SE[Skill Engine]
    end

    subgraph "dot-claude Repository"
        subgraph "Core Plugin"
            SUPER[super]
            SUPER_SKILLS[Skills<br/>TDD, Debugging, Review]
            SUPER_HOOKS[Hooks<br/>TDD Guard, Verification]
            SUPER_AGENTS[Agents<br/>Code Reviewer, Security]
        end

        subgraph "Domain Plugins"
            COMMIT[commit]
            DEV[dev]
            DOC[doc]
            SHELL[shell]
            DEBUG[debug]
            AGENT[agent]
        end
    end

    CC --> PM
    PM --> HE
    PM --> SE
    HE --> SUPER_HOOKS
    SE --> SUPER_SKILLS
    PM --> SUPER
    PM --> COMMIT
    PM --> DEV
    PM --> DOC
    PM --> SHELL
    PM --> DEBUG
    PM --> AGENT

    SUPER --> SUPER_SKILLS
    SUPER --> SUPER_HOOKS
    SUPER --> SUPER_AGENTS
```

## Plugin Architecture

Each plugin follows a standardized structure that Claude Code recognizes:

```mermaid
graph LR
    subgraph "Plugin Structure"
        ROOT[plugins/name/]
        META[.claude-plugin/plugin.json]
        SKILLS[skills/]
        AGENTS[agents/]
        COMMANDS[commands/]
        HOOKS[hooks/]
        LIB[lib/]
        CHEAT[cheatsheets/]
    end

    ROOT --> META
    ROOT --> SKILLS
    ROOT --> AGENTS
    ROOT --> COMMANDS
    ROOT --> HOOKS
    ROOT --> LIB
    ROOT --> CHEAT

    SKILLS --> S1[skill-name/SKILL.md]
    AGENTS --> A1[agent-name.md]
    COMMANDS --> C1[command-name.md]
    HOOKS --> H1[hooks.json]
    HOOKS --> H2[*.sh scripts]
```

### Component Types

| Component | Location | Format | Purpose |
|-----------|----------|--------|---------|
| **Skills** | `skills/<name>/SKILL.md` | Markdown + YAML frontmatter | Reusable techniques and workflows |
| **Agents** | `agents/<name>.md` | Markdown + YAML frontmatter | Subagent definitions with prompts |
| **Commands** | `commands/<name>.md` | Markdown + YAML frontmatter | Slash commands that expand to prompts |
| **Hooks** | `hooks/hooks.json` + `*.sh` | JSON config + shell scripts | Intercept tool usage events |
| **Cheatsheets** | `cheatsheets/*.md` | Markdown | Reference documentation |
| **Libraries** | `lib/*.js` | JavaScript/ESM | Shared utilities |

## Hook System

Hooks intercept Claude Code events at four lifecycle points:

```mermaid
sequenceDiagram
    participant U as User
    participant CC as Claude Code
    participant HE as Hook Engine
    participant H as Hook Script
    participant T as Tool

    U->>CC: Start session
    CC->>HE: SessionStart event
    HE->>H: Execute session-start.sh
    H-->>HE: Context injection
    HE-->>CC: Modified context

    U->>CC: Request action
    CC->>HE: PreToolUse (Write/Edit)
    HE->>H: Execute tdd-guard.sh
    alt Approved
        H-->>HE: approve
        HE->>T: Execute tool
        T-->>CC: Result
    else Blocked
        H-->>HE: block + reason
        HE-->>CC: Blocked message
    end

    CC->>HE: Stop event
    HE->>H: Verification check
    H-->>HE: approve/block
```

### Hook Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| `SessionStart` | Session begins, resumes, or clears | Inject context, load skills |
| `PreToolUse` | Before tool execution | Validate, block, or modify tool calls |
| `PostToolUse` | After tool execution | Audit, log, or react to results |
| `Stop` | Conversation ends | Verify work completion |

## Skill Resolution

Skills support namespacing and shadowing:

```mermaid
flowchart TD
    REQ[Skill Request: 'brainstorming']

    REQ --> CHECK{super: prefix?}
    CHECK -->|Yes| SUPER_ONLY[Search super plugin only]
    CHECK -->|No| PERSONAL[Search personal skills first]

    PERSONAL --> FOUND1{Found?}
    FOUND1 -->|Yes| USE_PERSONAL[Use personal skill]
    FOUND1 -->|No| SUPER_FALLBACK[Search super plugin]

    SUPER_FALLBACK --> FOUND2{Found?}
    FOUND2 -->|Yes| USE_SUPER[Use super skill]
    FOUND2 -->|No| NOT_FOUND[Skill not found]

    SUPER_ONLY --> FOUND3{Found?}
    FOUND3 -->|Yes| USE_SUPER
    FOUND3 -->|No| NOT_FOUND
```

### Skill File Format

```yaml
---
name: skill-name
description: Use when [condition] - [what it does]
---

# Skill Content

Instructions, checklists, and patterns...
```

## Plugin Relationships

```mermaid
graph TD
    subgraph "Foundation Layer"
        SUPER[super<br/>Core workflows]
    end

    subgraph "Development Layer"
        DEV[dev<br/>Python tools]
        SHELL[shell<br/>Shell scripts]
        DEBUG[debug<br/>Troubleshooting]
    end

    subgraph "Collaboration Layer"
        COMMIT[commit<br/>Git workflows]
        DOC[doc<br/>Documentation]
    end

    subgraph "Orchestration Layer"
        AGENT[agent<br/>Multi-agent]
    end

    SUPER -.->|TDD, verification| DEV
    SUPER -.->|TDD, verification| SHELL
    SUPER -.->|systematic-debugging| DEBUG
    SUPER -.->|brainstorming, review| COMMIT
    SUPER -.->|brainstorming| DOC
    SUPER -.->|skill patterns| AGENT

    DEV -.->|code context| DOC
    DEBUG -.->|error analysis| DEV
    COMMIT -.->|branch workflows| DEV
```

## Data Flow

### Session Initialization

```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant SUPER as super plugin
    participant SKILLS as Skill Engine

    CC->>SUPER: Load plugin
    SUPER->>CC: Register hooks
    CC->>SUPER: SessionStart
    SUPER->>SKILLS: Discover available skills
    SKILLS-->>SUPER: Skill catalog
    SUPER-->>CC: Inject skill context
    Note over CC: Skills available via<br/>Skill tool
```

### TDD Enforcement

```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant TDD as tdd-guard.sh
    participant FILE as Target File

    CC->>TDD: PreToolUse(Write, path)
    TDD->>TDD: Check file extension
    alt Test file (*_test.*, *.test.*, test_*)
        TDD-->>CC: approve
        CC->>FILE: Write test
    else Production code
        TDD->>TDD: Check recent test runs
        alt Tests run recently
            TDD-->>CC: approve
        else No recent tests
            TDD-->>CC: block: "Write test first"
        end
    end
```

## Plugin Catalog

| Plugin | Version | Skills | Agents | Commands | Hooks |
|--------|---------|--------|--------|----------|-------|
| **super** | 3.5.1 | 20 | 3 | 3 | 3 |
| **commit** | 1.0.0 | 0 | 1 | 3 | 3 |
| **dev** | 0.1.0 | 5 | 3 | 1 | 0 |
| **doc** | 0.3.0 | 1 | 5 | 3 | 0 |
| **shell** | 1.2.0 | 1 | 1 | 1 | 1 |
| **debug** | 0.1.0 | 0 | 2 | 1 | 0 |
| **agent** | 0.1.0 | 0 | 1 | 2 | 0 |

## Extension Points

### Creating a New Plugin

1. Create directory: `plugins/<name>/`
2. Add metadata: `.claude-plugin/plugin.json`
3. Add components as needed (skills, agents, commands, hooks)
4. Install: Add to Claude Code settings or symlink to `~/.claude/plugins/`

### Skill Development Workflow

```mermaid
flowchart LR
    IDEA[Identify pattern] --> BASELINE[Test without skill]
    BASELINE --> WRITE[Write SKILL.md]
    WRITE --> TEST[Test with subagent]
    TEST --> ITERATE{Passes?}
    ITERATE -->|No| REFINE[Close loopholes]
    REFINE --> TEST
    ITERATE -->|Yes| DEPLOY[Deploy skill]
```

## Security Considerations

- **Hook scripts** run with user privileges; review before installing
- **PreToolUse hooks** can block dangerous operations
- **Skill content** is injected into LLM context; avoid sensitive data
- **Personal skills** shadow plugin skills; verify source on conflicts

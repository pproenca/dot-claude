# Plugin Reference

Complete reference for all plugins in dot-claude.

## super

**Core skills library for Claude Code: TDD, debugging, collaboration patterns, and proven techniques**

Version: 3.5.1

The foundation plugin that provides workflow enforcement and reusable patterns.

### Skills (20)

| Skill | Description |
|-------|-------------|
| `brainstorming` | Collaborative design refinement before coding |
| `condition-based-waiting` | Replace timeouts with condition polling |
| `defense-in-depth` | Multi-layer validation patterns |
| `dispatching-parallel-agents` | Run multiple independent investigations |
| `executing-plans` | Execute implementation plans in batches |
| `finishing-a-development-branch` | Merge/PR/keep/discard workflow |
| `receiving-code-review` | Handle review feedback rigorously |
| `requesting-code-review` | Dispatch code reviewer agent |
| `root-cause-tracing` | Trace bugs backward through call stack |
| `sharing-skills` | Contribute skills upstream |
| `subagent-driven-development` | Fresh agents per task with review gates |
| `systematic-debugging` | Four-phase investigation framework |
| `test-driven-development` | RED-GREEN-REFACTOR cycle enforcement |
| `testing-anti-patterns` | Avoid common testing mistakes |
| `testing-skills-with-subagents` | TDD for skill documentation |
| `using-git-worktrees` | Isolated feature development |
| `using-superpowers` | Mandatory skill discovery protocol for every conversation |
| `verification-before-completion` | Requires evidence before claiming "done" |
| `writing-plans` | Create detailed implementation plans |
| `writing-skills` | Create bulletproof skills |

### Agents

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Review implementation against requirements |
| `diagram-generator` | Create Mermaid/PlantUML diagrams |
| `security-reviewer` | OWASP vulnerabilities and production readiness |

### Commands

| Command | Description |
|---------|-------------|
| `/super:plan` | Create detailed implementation plan |
| `/super:exec` | Execute plan in batches with checkpoints |
| `/super:brainstorm` | Interactive design refinement |

### Hooks

- **SessionStart**: Injects skill context via `session-start.sh`
- **PreToolUse**: TDD enforcement via `tdd-guard.sh`
- **Stop**: Verification check before completion

---

## commit

**Git workflows: worktrees, branches, and commit organization**

Version: 1.0.0

Implements Google-style commit practices and branch management.

### Agents

| Agent | Purpose |
|-------|---------|
| `commit-organizer` | Reorganize commits for clean history |

### Commands

| Command | Description |
|---------|-------------|
| `/commit:new` | Create commit following Google practices |
| `/commit:pr [base]` | Generate PR title and description |
| `/commit:reset` | Reset and reorganize commits |

### Hooks

- **SessionStart**: Git context initialization
- **PreToolUse**: Safety checks for git operations
- **PostToolUse**: Commit validation

### Cheatsheets

- `google-guidelines.md` - Commit message standards

---

## dev

**Modern Python 3.12+ development with uv, ruff, pydantic, FastAPI and production-ready practices**

Version: 0.1.0

Python development toolkit with modern tooling expertise.

### Skills

| Skill | Description |
|-------|-------------|
| `uv-package-manager` | Fast dependency management with uv |
| `async-python-patterns` | asyncio and concurrent programming |
| `python-testing-patterns` | pytest, fixtures, mocking, TDD |
| `python-packaging` | Create distributable packages |
| `python-performance-optimization` | Profiling and optimization |

### Agents

| Agent | Purpose |
|-------|---------|
| `python-pro` | Python 3.12+ expert |
| `fastapi-pro` | FastAPI, SQLAlchemy 2.0, async APIs |
| `django-pro` | Django 5.x, DRF, Celery, Channels |

### Commands

| Command | Description |
|---------|-------------|
| `/dev:scaffold` | Scaffold Python project structure |

---

## doc

**Documentation: API docs, tutorials, memos, architecture guides, Mermaid diagrams**

Version: 0.3.0

Documentation generation and writing expertise.

### Skills

| Skill | Description |
|-------|-------------|
| `amazon-writing` | Narrative memos, 6-pagers, PRFAQs |

### Agents

| Agent | Purpose |
|-------|---------|
| `api-documenter` | OpenAPI specs and API docs |
| `docs-architect` | Documentation structure and organization |
| `tutorial-engineer` | Step-by-step tutorials |
| `reference-builder` | Comprehensive reference docs |
| `mermaid-expert` | Diagrams and visualizations |

### Commands

| Command | Description |
|---------|-------------|
| `/doc:gen` | Generate documentation from code |
| `/doc:explain` | Explain code or concepts |
| `/doc:rewrite [type]` | Rewrite document in Amazon style |

---

## shell

**Shell scripting toolkit with Google Style Guide refactoring**

Version: 1.2.0

Shell script analysis and improvement.

### Skills

| Skill | Description |
|-------|-------------|
| `google-shell-style` | Google Shell Style Guide rules |

### Agents

| Agent | Purpose |
|-------|---------|
| `shell-expert` | Shell scripting expertise |

### Commands

| Command | Description |
|---------|-------------|
| `/shell:refactor path` | Refactor script to Google style |

### Hooks

- **PreCompact**: Preserves shell plugin context during compaction

---

## debug

**Distributed systems debugging: log analysis, error correlation, stack trace detection, and root cause investigation**

Version: 0.1.0

Production troubleshooting and incident response.

### Agents

| Agent | Purpose |
|-------|---------|
| `error-detective` | Search logs for error patterns |
| `devops-troubleshooter` | Incident response and debugging |

### Commands

| Command | Description |
|---------|-------------|
| `/debug:trace` | Trace error through system |

---

## agent

**Context engineering and multi-agent workflow orchestration with vector databases and knowledge graphs**

Version: 0.1.0

Advanced agent orchestration patterns.

### Agents

| Agent | Purpose |
|-------|---------|
| `context-manager` | Dynamic context management |

### Commands

| Command | Description |
|---------|-------------|
| `/agent:improve` | Improve agent configuration |
| `/agent:optimize` | Optimize context usage |

---

## Plugin Comparison Matrix

| Feature | super | commit | dev | doc | shell | debug | agent |
|---------|-------|--------|-----|-----|-------|-------|-------|
| Skills | 20 | 0 | 5 | 1 | 1 | 0 | 0 |
| Agents | 3 | 1 | 3 | 5 | 1 | 2 | 1 |
| Commands | 3 | 3 | 1 | 3 | 1 | 1 | 2 |
| Hooks | 3 | 3 | 0 | 0 | 1 | 0 | 0 |
| Cheatsheets | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

## Skill Quick Reference

### Workflow Skills (super)

```
super:brainstorming          - Design before coding
super:test-driven-development - RED-GREEN-REFACTOR
super:verification-before-completion - Evidence before "done"
super:systematic-debugging   - Four-phase investigation
```

### Development Skills (super + dev)

```
super:root-cause-tracing     - Trace bugs to source
super:defense-in-depth       - Multi-layer validation
dev:python-testing-patterns  - pytest and mocking
dev:async-python-patterns    - asyncio mastery
```

### Collaboration Skills (super)

```
super:requesting-code-review - Get code reviewed
super:receiving-code-review  - Handle feedback well
super:writing-plans          - Detailed implementation plans
super:executing-plans        - Execute in batches
```

### Git Skills (super + commit)

```
super:using-git-worktrees    - Isolated branches
super:finishing-a-development-branch - Merge/PR workflow
commit:new                   - Google-style commits
commit:pr                    - PR descriptions
```

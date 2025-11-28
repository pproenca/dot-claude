# Getting Started

This guide walks you through installing and using dot-claude with Claude Code.

## Prerequisites

- [Claude Code CLI](https://claude.ai/code) installed
- Git for cloning the repository
- Shell access (bash/zsh)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/pedroproenca/dot-claude.git
cd dot-claude
```

### Step 2: Install Plugins

**Option A: Symlink all plugins (recommended)**

```bash
# Create plugins directory if needed
mkdir -p ~/.claude/plugins

# Symlink each plugin
for plugin in plugins/*/; do
  plugin_name=$(basename "$plugin")
  ln -sf "$(pwd)/$plugin" ~/.claude/plugins/"$plugin_name"
done
```

**Option B: Install specific plugins**

```bash
# Install only the plugins you need
ln -sf "$(pwd)/plugins/super" ~/.claude/plugins/super
ln -sf "$(pwd)/plugins/commit" ~/.claude/plugins/commit
```

**Option C: Project-specific installation**

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": [
    "/absolute/path/to/dot-claude/plugins/super",
    "/absolute/path/to/dot-claude/plugins/commit"
  ]
}
```

### Step 3: Verify Installation

Start Claude Code and check for skill availability:

```
What skills are available?
```

You should see skills from the installed plugins listed.

## Your First Workflow

### Example 1: Brainstorming a Feature

Before writing code, use brainstorming to refine your design:

```
I want to add user authentication to my app. Let's brainstorm.
```

Claude will use `super:brainstorming` to:
1. Ask clarifying questions
2. Explore alternatives
3. Validate assumptions
4. Produce a design document

### Example 2: Test-Driven Development

When implementing, TDD is enforced:

```
Implement the login function we designed.
```

Claude will:
1. Write tests first (RED)
2. Implement minimal code (GREEN)
3. Refactor for quality (REFACTOR)

The `tdd-guard.sh` hook blocks writing production code without tests.

### Example 3: Creating a Commit

Use Google-style commit practices:

```
/commit:new
```

Claude will:
1. Analyze staged changes
2. Generate a structured commit message
3. Follow Google commit guidelines

### Example 4: Debugging

When troubleshooting, use systematic debugging:

```
The API is returning 500 errors. Help me debug.
```

Claude will use `super:systematic-debugging`:
1. **Root cause investigation** - Gather evidence
2. **Pattern analysis** - Identify correlations
3. **Hypothesis testing** - Test theories
4. **Implementation** - Fix with verification

## Understanding Components

### Skills

Skills are reusable techniques stored in `SKILL.md` files. They provide:
- Structured workflows
- Checklists to follow
- Best practices

**How to use:**
```
I'm using the test-driven-development skill to implement this.
```

**Key skills to know:**
| Skill | When to use |
|-------|-------------|
| `super:brainstorming` | Before coding, when designing |
| `super:test-driven-development` | When writing any code |
| `super:systematic-debugging` | When troubleshooting issues |
| `super:verification-before-completion` | Before claiming "done" |

### Commands

Commands are slash-prefixed shortcuts that expand to prompts:

| Command | Purpose |
|---------|---------|
| `/super:plan` | Create detailed implementation plan |
| `/super:exec` | Execute plan with checkpoints |
| `/commit:new` | Create structured commit |
| `/commit:pr` | Generate PR description |
| `/doc:gen` | Generate documentation |

### Agents

Agents are specialized subagents with focused expertise:

| Agent | Expertise |
|-------|-----------|
| `code-reviewer` | Code review against requirements |
| `fastapi-pro` | FastAPI development |
| `django-pro` | Django development |
| `python-pro` | Python best practices |

**How to invoke:**
```
Use the code-reviewer agent to review my changes.
```

### Hooks

Hooks intercept Claude Code events to enforce workflows:

| Hook | Event | Purpose |
|------|-------|---------|
| SessionStart | Session begins | Load context, inject skills |
| PreToolUse | Before Write/Edit | Enforce TDD |
| Stop | Conversation ends | Verify completion |

Hooks run automatically - you don't invoke them directly.

## Common Workflows

### Starting a New Feature

1. **Brainstorm the design**
   ```
   I want to add [feature]. Let's brainstorm.
   ```

2. **Create implementation plan**
   ```
   /super:plan
   ```

3. **Execute with TDD**
   ```
   /super:exec
   ```

4. **Review before merge**
   ```
   Use the code-reviewer agent to review.
   ```

5. **Create PR**
   ```
   /commit:pr
   ```

### Debugging an Issue

1. **Start systematic investigation**
   ```
   I'm seeing [error]. Help me debug using systematic debugging.
   ```

2. **Follow the four phases**
   - Root cause investigation
   - Pattern analysis
   - Hypothesis testing
   - Implementation

3. **Verify the fix**
   ```
   Run the tests to verify the fix.
   ```

### Writing Documentation

1. **Generate from code**
   ```
   /doc:gen
   ```

2. **Create architecture diagrams**
   ```
   Use the mermaid-expert agent to create diagrams.
   ```

3. **Write tutorials**
   ```
   Use the tutorial-engineer agent to write a guide.
   ```

## Customization

### Adding Personal Skills

Create skills in `~/.claude/skills/<name>/SKILL.md`:

```yaml
---
name: my-custom-skill
description: Use when [condition] - [what it does]
---

# My Custom Skill

Instructions here...
```

Personal skills override plugin skills with the same name.

### Overriding Plugin Skills

To customize a plugin skill:

1. Copy to personal skills directory
2. Modify as needed
3. Personal version takes precedence

### Disabling Hooks

To disable TDD enforcement for a project, add to `.claude/settings.json`:

```json
{
  "hooks": {
    "super": {
      "PreToolUse": {
        "enabled": false
      }
    }
  }
}
```

## Troubleshooting

### Skills Not Loading

1. Check symlinks exist: `ls -la ~/.claude/plugins/`
2. Verify plugin structure: `ls plugins/super/.claude-plugin/`
3. Check for YAML frontmatter in SKILL.md files

### Hooks Not Firing

1. Verify hooks.json syntax: `cat plugins/super/hooks/hooks.json | jq .`
2. Check script permissions: `chmod +x plugins/super/hooks/*.sh`
3. Test hook manually: `./plugins/super/hooks/session-start.sh`

### TDD Guard Blocking Incorrectly

The TDD guard checks for recent test runs. If blocked:

1. Run tests first: `pytest` or equivalent
2. Write test file before production code
3. Check that test file matches naming convention (`*_test.py`, `test_*.py`)

## Next Steps

- Read [Architecture](ARCHITECTURE.md) for system design details
- Browse [Plugin Reference](PLUGINS.md) for complete documentation
- Explore skills in `plugins/super/skills/` for workflow patterns
- Contribute improvements via `super:sharing-skills`

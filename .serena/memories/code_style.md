# Code Style and Conventions

## Bash/Shell Scripts

### Follow Google Shell Style Guide
Reference: `domain_plugins/shell/skills/google-shell-style/SKILL.md`

### Key Rules
1. **Shebang**: `#!/bin/bash`
2. **Strict mode**: `set -euo pipefail`
3. **Indentation**: 2 spaces (never tabs)
4. **Line length**: Max 80 characters

### Variable Handling
```bash
# Always quote and use braces
echo "${var}"
rm "${file}"

# Arrays for commands with spaces
local -a args=(--flag "value with spaces")
command "${args[@]}"
```

### Conditionals
```bash
# Use [[ ]] not [ ]
if [[ condition ]]; then
  command
fi

# Use $(command) not backticks
result=$(command)
```

### Functions
```bash
# lowercase_with_underscores
# Use local variables
# Return status codes 0-255
process_file() {
  local input_file="$1"
  local result=""

  if ! some_command; then
    return 1
  fi

  echo "$result"
}
```

### Error Handling
```bash
# Standard error function
err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

# Cleanup with traps
cleanup() {
  rm -f "${tmp_file:-}"
}
trap cleanup EXIT
```

### Avoid
- `eval` - security risk
- Aliases in scripts - use functions
- Piping to `while` - creates subshell
- `mapfile`/`readarray` - not on macOS

## Markdown Files

### Plugin Frontmatter
```yaml
---
name: Skill Name
description: When to trigger this skill
allowed-tools: Tool1, Tool2
---
```

### Command Frontmatter
```yaml
---
description: What the command does
allowed-tools: Tool1, Tool2
args:
  - name: arg_name
    description: What it does
---
```

### Agent Frontmatter
```yaml
---
name: agent-name
description: When to dispatch via Task tool
model: sonnet | haiku
tools: Glob, Grep, Read
---
```

## Pre-commit Hooks
- `trailing-whitespace`
- `end-of-file-fixer`
- `check-yaml`
- `check-json`
- `shellcheck` with `-x` flag

---
name: git-commit
description: Use when making git commits directly (not via /commit:new). Ensures safe shell quoting with heredoc format. Triggers on creating commits, staging and committing, any git commit operation.
allowed-tools: Bash
---

# Git Commit

Always use the commit script or heredoc format. Never use `-m "..."` with newlines.

## Single-line commit

```bash
$CLAUDE_PLUGIN_ROOT/scripts/commit.sh "type: description"
```

## Multi-line commit

```bash
$CLAUDE_PLUGIN_ROOT/scripts/commit.sh "type: description" "Body explaining WHY.

Additional context if needed."
```

## Alternative: Direct heredoc

```bash
git commit -F - <<'EOF'
type: description

Body explaining WHY.
EOF
```

## Never do this

```bash
# WRONG - causes shell parsing issues with multiline messages
git commit -m "type: description
body text"
```

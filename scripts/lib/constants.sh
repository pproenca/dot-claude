#!/usr/bin/env bash
# Constants for marketplace validation
# Sourced by common.sh - do not source directly

# Disable shellcheck warnings for:
# SC2034: Variables appear unused but are used by sourcing scripts
# shellcheck disable=SC2034

# ============================================================================
# Valid Tools Whitelist
# ============================================================================

# Built-in Claude Code tools
VALID_BUILTIN_TOOLS=(
  "AskUserQuestion"
  "Bash"
  "BashOutput"
  "Edit"
  "ExitPlanMode"
  "Glob"
  "Grep"
  "KillShell"
  "NotebookEdit"
  "Read"
  "Skill"
  "SlashCommand"
  "Task"
  "TodoWrite"
  "WebFetch"
  "WebSearch"
  "Write"
)

# Valid model values for agents
VALID_MODELS=(
  "sonnet"
  "opus"
)

# Valid color values for agents (Claude Code UI colors)
VALID_COLORS=(
  "blue"
  "green"
  "red"
  "yellow"
  "purple"
  "orange"
  "cyan"
  "pink"
)

# ============================================================================
# Required Fields by Component Type
# ============================================================================

# Skills (SKILL.md files)
SKILL_REQUIRED_FIELDS=(
  "name"
  "description"
  "allowed-tools"
)

# Commands (commands/*.md files)
COMMAND_REQUIRED_FIELDS=(
  "description"
  "allowed-tools"
)

# Agents (agents/*.md files)
AGENT_REQUIRED_FIELDS=(
  "name"
  "description"
)

# At least one of these must be present in agents
AGENT_TOOLS_FIELDS=(
  "tools"
  "allowed-tools"
)

# Plugin manifest (plugin.json)
PLUGIN_JSON_REQUIRED=(
  "name"
  "description"
)

# Marketplace manifest (marketplace.json)
MARKETPLACE_JSON_REQUIRED=(
  "name"
  "description"
  "plugins"
)

# ============================================================================
# File Patterns
# ============================================================================

# Skill file pattern
SKILL_FILE_PATTERN="SKILL.md"

# Command file extension
COMMAND_FILE_EXT=".md"

# Agent file extension
AGENT_FILE_EXT=".md"

# Plugin manifest path (relative to plugin directory)
PLUGIN_MANIFEST_PATH=".claude-plugin/plugin.json"

# Hooks config path (relative to plugin directory)
HOOKS_CONFIG_PATH="hooks/hooks.json"

# ============================================================================
# Semver Pattern
# ============================================================================

# Regex for semantic versioning (X.Y.Z with optional pre-release)
SEMVER_PATTERN='^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$'

# ============================================================================
# Validation Thresholds
# ============================================================================

# Maximum recommended description length for commands
MAX_COMMAND_DESC_LENGTH=60

# Maximum recommended skill description length (for discovery)
MAX_SKILL_DESC_LENGTH=200

#!/usr/bin/env bash
# Constants for marketplace validation
# Sourced by common.sh - do not source directly

# Disable shellcheck warnings for:
# SC2034: Variables appear unused but are used by sourcing scripts
# shellcheck disable=SC2034

# ============================================================================
# Valid Tools Whitelist
# ============================================================================

# Built-in Claude Code tools.
# Synced to the official Tools reference
# (https://code.claude.com/docs/en/tools-reference.md, v2.1.145+, 2026-05).
# Note: the subagent-dispatch tool is "Agent"; bare "Task" is the legacy
# pre-rename name still used by older command frontmatter, kept for backward
# compatibility. The Task* tools (TaskCreate/Get/List/Output/Stop/Update) are
# the separate background-task tools.
VALID_BUILTIN_TOOLS=(
  "Agent"
  "AskUserQuestion"
  "Bash"
  "CronCreate"
  "CronDelete"
  "CronList"
  "Edit"
  "EnterPlanMode"
  "EnterWorktree"
  "ExitPlanMode"
  "ExitWorktree"
  "Glob"
  "Grep"
  "ListMcpResourcesTool"
  "LSP"
  "Monitor"
  "NotebookEdit"
  "PowerShell"
  "PushNotification"
  "Read"
  "ReadMcpResourceTool"
  "RemoteTrigger"
  "ScheduleWakeup"
  "SendMessage"
  "ShareOnboardingGuide"
  "Skill"
  "Task"
  "TaskCreate"
  "TaskGet"
  "TaskList"
  "TaskOutput"
  "TaskStop"
  "TaskUpdate"
  "TeamCreate"
  "TeamDelete"
  "TodoWrite"
  "ToolSearch"
  "WaitForMcpServers"
  "WebFetch"
  "WebSearch"
  "Write"
)

# Valid model values for agents
VALID_MODELS=(
  "haiku"
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
)

# Commands (commands/*.md files)
# Note: allowed-tools is OPTIONAL for commands (omitting it grants all tools),
# matching Claude Code's command frontmatter spec.
COMMAND_REQUIRED_FIELDS=(
  "description"
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

# Maximum skill description length (Anthropic hard limit: 1024 chars)
MAX_SKILL_DESC_LENGTH=1024

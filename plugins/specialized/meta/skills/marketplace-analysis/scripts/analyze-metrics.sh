#!/usr/bin/env bash
# Analyze plugin metrics for marketplace quality assessment
# Usage: ./analyze-metrics.sh [plugins_dir]

set -euo pipefail

PLUGINS_DIR="${1:-plugins}"

echo "## Plugin Metrics Analysis"
echo ""

# Count plugins
plugin_count=$(find "$PLUGINS_DIR" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
echo "### Overview"
echo "- Plugins: $plugin_count"

# Count components
skill_count=$(find "$PLUGINS_DIR" -path "*/skills/*/SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
agent_count=$(find "$PLUGINS_DIR" -path "*/agents/*.md" 2>/dev/null | wc -l | tr -d ' ')
command_count=$(find "$PLUGINS_DIR" -path "*/commands/*.md" 2>/dev/null | wc -l | tr -d ' ')
hook_count=$(find "$PLUGINS_DIR" -path "*/hooks/hooks.json" 2>/dev/null | wc -l | tr -d ' ')

echo "- Skills: $skill_count"
echo "- Agents: $agent_count"
echo "- Commands: $command_count"
echo "- Hooks: $hook_count"
echo ""

# Line counts for skills
echo "### SKILL.md Line Counts"
if [ "$skill_count" -gt 0 ]; then
    find "$PLUGINS_DIR" -path "*/skills/*/SKILL.md" -exec wc -l {} \; 2>/dev/null | sort -rn | head -10
    echo ""
    total_skill_lines=$(find "$PLUGINS_DIR" -path "*/skills/*/SKILL.md" -exec cat {} \; 2>/dev/null | wc -l | tr -d ' ')
    echo "Total skill lines: $total_skill_lines"
    avg_lines=$((total_skill_lines / skill_count))
    echo "Average per skill: $avg_lines"
else
    echo "No skills found"
fi
echo ""

# Large files (>500 lines)
echo "### Files Over 500 Lines (Red Flags)"
find "$PLUGINS_DIR" -name "*.md" -exec sh -c 'lines=$(wc -l < "$1"); if [ "$lines" -gt 500 ]; then echo "$lines $1"; fi' _ {} \; 2>/dev/null | sort -rn || echo "None found"
echo ""

# Trigger phrase analysis
echo "### Trigger Phrase Metrics"
if [ "$skill_count" -gt 0 ]; then
    trigger_count=$(grep -roh '"[^"]\{1,50\}"' "$PLUGINS_DIR"/*/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    echo "- Quoted trigger phrases in skills: $trigger_count"
    if [ "$skill_count" -gt 0 ]; then
        avg_triggers=$((trigger_count / skill_count))
        echo "- Average triggers per skill: $avg_triggers"
    fi
fi
echo ""

echo "### Analysis Complete"

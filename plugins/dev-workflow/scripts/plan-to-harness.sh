#!/usr/bin/env bash
# plan-to-harness.sh - Convert markdown plan to harness JSON format
# Usage: plan-to-harness.sh <plan-file.md>

set -euo pipefail

plan_to_harness() {
  local plan_file="$1"

  if [[ ! -f "$plan_file" ]]; then
    echo "ERROR: Plan file not found: $plan_file" >&2
    return 1
  fi

  local content
  content=$(cat "$plan_file")

  # Extract goal from **Goal:** line
  local goal
  goal=$(echo "$content" | grep -E '^\*\*Goal:\*\*' | sed 's/\*\*Goal:\*\* *//' | head -1)

  # Initialize JSON structure
  local json='{"goal":"'"$goal"'","tasks":{}}'

  # Extract tasks using awk
  local task_num=0
  local current_task=""
  local current_desc=""
  local current_deps=""
  local current_instructions=""
  local in_task=false

  while IFS= read -r line; do
    # Check for task header: ### Task N: Description
    if [[ "$line" =~ ^###[[:space:]]+Task[[:space:]]+([0-9]+):[[:space:]]*(.*) ]]; then
      # Save previous task if exists
      if [[ -n "$current_task" ]]; then
        local deps_array="[]"
        if [[ -n "$current_deps" ]]; then
          deps_array=$(echo "$current_deps" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | \
            sed 's/Task /task-/g' | jq -R . | jq -s .)
        fi
        # Escape instructions for JSON
        local escaped_instructions
        escaped_instructions=$(echo "$current_instructions" | jq -Rs .)
        json=$(echo "$json" | jq --arg id "$current_task" --arg desc "$current_desc" \
          --argjson deps "$deps_array" --argjson instr "$escaped_instructions" \
          '.tasks[$id] = {description: $desc, dependencies: $deps, timeout_seconds: 600, instructions: $instr, role: "backend"}')
      fi

      task_num="${BASH_REMATCH[1]}"
      current_task="task-$task_num"
      current_desc="${BASH_REMATCH[2]}"
      current_deps=""
      current_instructions=""
      in_task=true
    # Check for dependencies line
    elif [[ "$in_task" == true && "$line" =~ ^\*\*Dependencies:\*\*[[:space:]]*(.*) ]]; then
      current_deps="${BASH_REMATCH[1]}"
    # Collect instructions (everything after **Step lines)
    elif [[ "$in_task" == true && "$line" =~ ^\*\*Step ]]; then
      current_instructions+="$line"$'\n'
    elif [[ "$in_task" == true && -n "$current_instructions" ]]; then
      current_instructions+="$line"$'\n'
    fi
  done <<< "$content"

  # Save last task
  if [[ -n "$current_task" ]]; then
    local deps_array="[]"
    if [[ -n "$current_deps" ]]; then
      deps_array=$(echo "$current_deps" | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | \
        sed 's/Task /task-/g' | jq -R . | jq -s .)
    fi
    local escaped_instructions
    escaped_instructions=$(echo "$current_instructions" | jq -Rs .)
    json=$(echo "$json" | jq --arg id "$current_task" --arg desc "$current_desc" \
      --argjson deps "$deps_array" --argjson instr "$escaped_instructions" \
      '.tasks[$id] = {description: $desc, dependencies: $deps, timeout_seconds: 600, instructions: $instr, role: "backend"}')
  fi

  echo "$json"
}

# Allow sourcing or direct execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <plan-file.md>" >&2
    exit 1
  fi
  plan_to_harness "$1"
fi

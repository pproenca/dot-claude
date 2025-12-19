#!/bin/bash
# Helper functions for dev-workflow hooks and scripts
# All state management is via harness daemon

# =============================================================================
# Plan Parsing Functions (for parallel task grouping)
# =============================================================================

# Extract all task numbers from a plan file
# Usage: get_task_numbers <plan_file>
# Returns: Space-separated list of task numbers (e.g., "1 1.1 1.2 2 3")
get_task_numbers() {
  local plan_file="$1"
  grep -oE "^### Task [0-9]+(\.[0-9]+)?:" "$plan_file" | \
    sed 's/^### Task //' | sed 's/:$//' | tr '\n' ' ' | sed 's/ $//'
}

# Get the next task number in sequence (for awk range extraction)
# Usage: get_next_task_number <plan_file> <current_task_num>
# Returns: Next task number or empty string if last task
get_next_task_number() {
  local plan_file="$1"
  local current="$2"
  local found_current=false

  for num in $(get_task_numbers "$plan_file"); do
    if [[ "$found_current" == "true" ]]; then
      echo "$num"
      return
    fi
    if [[ "$num" == "$current" ]]; then
      found_current=true
    fi
  done
  echo ""
}

# Extract file paths from a task section
# Usage: get_task_files <plan_file> <task_num>
# Returns: List of file paths (one per line)
get_task_files() {
  local plan_file="$1"
  local task_num="$2"
  local next_task
  next_task=$(get_next_task_number "$plan_file" "$task_num")

  # Build awk pattern - if no next task, match until next section
  local end_pattern
  if [[ -n "$next_task" ]]; then
    end_pattern="/^### Task ${next_task}:|^## /"
  else
    end_pattern="/^## /"
  fi

  # Extract task section and find file paths in backticks after Create/Modify/Test:
  # shellcheck disable=SC2016 # Backtick regex is intentional - matching literal backticks
  awk "/^### Task ${task_num}:/,${end_pattern}" "$plan_file" | \
    grep -E '(Create|Modify|Test):' | \
    grep -oE '`[^`]+`' | tr -d '`' | sort -u
}

# Group tasks by file dependencies for parallel execution
# Usage: group_tasks_by_dependency <plan_file> [max_group_size]
# Output: group1:1,1.1,1.2|group2:2,3|group3:4,4.1
# Tasks within a group have NO file overlap (can run in parallel)
# Groups execute serially (group 1 completes before group 2)
group_tasks_by_dependency() {
  local plan_file="$1"
  local max_group="${2:-5}"  # Default max 5 per group (Anthropic pattern)

  local groups=""
  local current_group=""
  local current_group_files=""
  local group_count=0
  local group_num=1

  # Iterate through actual task numbers from plan
  for task_num in $(get_task_numbers "$plan_file"); do
    local task_files
    task_files=$(get_task_files "$plan_file" "$task_num")

    # Check if task overlaps with current group
    local has_overlap=false
    if [[ -n "$current_group_files" ]] && [[ -n "$task_files" ]]; then
      local common
      common=$(comm -12 <(echo "$current_group_files" | sort) <(echo "$task_files" | sort) 2>/dev/null)
      [[ -n "$common" ]] && has_overlap=true
    fi

    # Start new group if: overlap, or group full
    if [[ "$has_overlap" == "true" ]] || [[ "$group_count" -ge "$max_group" ]]; then
      # Save current group
      if [[ -n "$current_group" ]]; then
        [[ -n "$groups" ]] && groups="${groups}|"
        groups="${groups}group${group_num}:${current_group}"
        group_num=$((group_num + 1))
      fi
      # Start new group with this task
      current_group="$task_num"
      current_group_files="$task_files"
      group_count=1
    else
      # Add to current group
      [[ -n "$current_group" ]] && current_group="${current_group},$task_num" || current_group="$task_num"
      current_group_files="${current_group_files}"$'\n'"${task_files}"
      group_count=$((group_count + 1))
    fi
  done

  # Save last group
  if [[ -n "$current_group" ]]; then
    [[ -n "$groups" ]] && groups="${groups}|"
    groups="${groups}group${group_num}:${current_group}"
  fi

  echo "$groups"
}

# Get maximum parallelism from task groups
# Usage: get_max_parallel_from_groups <groups_string>
# Input: "group1:1,2,3|group2:4,5|group3:6"
# Output: 3 (largest group has 3 tasks)
get_max_parallel_from_groups() {
  local groups="$1"
  local max_parallel=1

  # Split by | and find largest group
  IFS='|' read -ra GROUP_ARRAY <<< "$groups"
  for group in "${GROUP_ARRAY[@]}"; do
    # Extract task list after colon
    local task_list="${group#*:}"
    # Count tasks (comma-separated)
    local task_count
    task_count=$(echo "$task_list" | tr ',' '\n' | wc -l | tr -d ' ')
    if [[ "$task_count" -gt "$max_parallel" ]]; then
      max_parallel="$task_count"
    fi
  done

  echo "$max_parallel"
}

# =============================================================================
# Harness Integration Functions
# =============================================================================

# Get workflow progress as JSON: {total, completed, pending, running}
harness_get_progress() {
  local state
  state=$(harness get-state 2>/dev/null || echo '{"tasks":{}}')

  echo "$state" | jq '{
    total: .tasks | length,
    completed: [.tasks[] | select(.status == "completed")] | length,
    pending: [.tasks[] | select(.status == "pending")] | length,
    running: [.tasks[] | select(.status == "running")] | length
  }'
}

# Import a plan file into harness
harness_import_plan() {
  local plan_file="$1"
  local json
  local temp_file

  # Resolve script directory relative to this file
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  # Convert markdown plan to harness JSON
  json=$("$script_dir/plan-to-harness.sh" "$plan_file")

  # Write JSON to temp file wrapped in markdown code fence (harness expects this)
  temp_file=$(mktemp)
  cat > "$temp_file" << EOF
\`\`\`json
$json
\`\`\`
EOF

  # Import into harness using --file
  harness plan import --file "$temp_file"
  local result=$?

  rm -f "$temp_file"
  return $result
}

# Claim next available task for current worker
harness_claim_task() {
  harness task claim
}

# Complete a task
harness_complete_task() {
  local task_id="$1"
  harness task complete --id "$task_id"
}

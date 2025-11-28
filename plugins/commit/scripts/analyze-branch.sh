#!/usr/bin/env bash
# Minimal branch analysis for commit-organizer
# Outputs JSON with branch point, file list, and line counts

set -euo pipefail

# Check if in git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo '{"error": "Not a git repository"}'
  exit 1
fi

# Get current branch
current_branch="$(git branch --show-current 2>/dev/null)" || current_branch="HEAD"

# Detect main branch
main_branch=""
for candidate in main master; do
  if git show-ref --verify --quiet "refs/remotes/origin/${candidate}" 2>/dev/null; then
    main_branch="${candidate}"
    break
  fi
done

if [[ -z "${main_branch}" ]]; then
  # Try symbolic ref
  main_branch="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
    | sed 's@^refs/remotes/origin/@@')" || main_branch="main"
fi

# Find branch point
branch_point="$(git merge-base HEAD "origin/${main_branch}" 2>/dev/null)" \
  || branch_point=""

if [[ -z "${branch_point}" ]]; then
  escaped_main="$(printf '%s' "${main_branch}" \
    | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"
  echo '{"error": "Could not find branch point. Ensure origin/'"${escaped_main}"' exists."}'
  exit 1
fi

branch_point_short="$(git rev-parse --short "${branch_point}")"
branch_point_msg="$(git log -1 --format=%s "${branch_point}" 2>/dev/null)" \
  || branch_point_msg=""

# Get changed files
files=()
while IFS= read -r file; do
    [[ -n "${file}" ]] && files+=("${file}")
done < <(git diff --name-only "${branch_point}" HEAD 2>/dev/null)

# Build file stats JSON
stats_json="["
total_add=0
total_del=0
first=true

for file in "${files[@]}"; do
    [[ -z "${file}" ]] && continue

    # Get additions/deletions for this file
    stat_line="$(git diff --numstat "${branch_point}" HEAD -- "${file}" 2>/dev/null \
      | head -1)"
    add="$(awk '{print $1}' <<< "${stat_line}")"
    del="$(awk '{print $2}' <<< "${stat_line}")"

    # Handle binary files (shown as -)
    [[ "${add}" == "-" ]] && add=0
    [[ "${del}" == "-" ]] && del=0

    total_add="$((total_add + add))"
    total_del="$((total_del + del))"

    # Escape filename for JSON
    escaped_file="$(printf '%s' "${file}" \
      | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"

    if [[ "${first}" == "true" ]]; then
        first=false
    else
        stats_json+=","
    fi
    stats_json+="{\"file\":\"${escaped_file}\",\"additions\":${add},"
    stats_json+="\"deletions\":${del}}"
done
stats_json+="]"

# Build cumulative diff content
diff_json="["
first_diff=true

for file in "${files[@]}"; do
  [[ -z "${file}" ]] && continue

  file_diff="$(git diff "${branch_point}" HEAD -- "${file}" 2>/dev/null)" \
    || file_diff=""

  escaped_diff="$(printf '%s' "${file_diff}" \
    | sed 's/\\/\\\\/g' \
    | sed 's/"/\\"/g' \
    | sed 's/\t/\\t/g' \
    | awk '{printf "%s\\n", $0}')"

  escaped_file="$(printf '%s' "${file}" \
    | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"

  if [[ "${first_diff}" == "true" ]]; then
    first_diff=false
  else
    diff_json+=","
  fi
  diff_json+="{\"file\":\"${escaped_file}\",\"diff\":\"${escaped_diff}\"}"
done
diff_json+="]"

# Build files array JSON
files_json="["
first=true
for file in "${files[@]}"; do
  [[ -z "${file}" ]] && continue
  escaped_file="$(printf '%s' "${file}" \
    | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"
  if [[ "${first}" == "true" ]]; then
    first=false
  else
    files_json+=","
  fi
  files_json+="\"${escaped_file}\""
done
files_json+="]"

# Escape branch point message
escaped_msg="$(printf '%s' "${branch_point_msg}" \
  | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"

# Output JSON
cat <<EOF
{
  "branch": {
    "current": "${current_branch}",
    "main": "${main_branch}",
    "branch_point": "${branch_point_short}",
    "branch_point_full": "${branch_point}",
    "branch_point_message": "${escaped_msg}"
  },
  "files": ${files_json},
  "stats": ${stats_json},
  "diffs": ${diff_json},
  "total": {
    "files": ${#files[@]},
    "additions": ${total_add},
    "deletions": ${total_del}
  }
}
EOF

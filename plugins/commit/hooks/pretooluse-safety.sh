#!/usr/bin/env bash
# PreToolUse hook for commit-organizer
# 1. Validates commit messages follow Google CL standards BEFORE execution
# 2. Validates destructive git commands have proper safety measures

set -euo pipefail

# Read input JSON from stdin
input="$(cat)"

# Fast-path: exit immediately if input doesn't contain git (avoid jq parsing overhead)
if ! echo "${input}" | grep -q '"git '; then
    echo '{}'
    exit 0
fi

# Skip validation on WIP/temp branches (subagents need flexible commits)
current_branch=$(git branch --show-current 2>/dev/null || echo "")
if [[ "$current_branch" =~ ^(wip|temp|backup)/ ]]; then
    echo '{}'
    exit 0
fi

# Extract command from tool_input
command="$(echo "${input}" | jq -r '.tool_input.command // empty')"

# Quick exit if not a git command
if [[ ! "${command}" =~ ^git ]]; then
    echo '{}'
    exit 0
fi

# === COMMIT MESSAGE VALIDATION (PreToolUse - before commit is created) ===
if [[ "${command}" =~ git[[:space:]]+commit ]]; then
    commit_issues=""

    # Extract commit message from -m flag
    # Handles: git commit -m "message", git commit -m 'message', git commit -m message
    commit_msg=""
    if [[ "${command}" =~ -m[[:space:]]+[\"\']([^\"\']+)[\"\'] ]]; then
        commit_msg="${BASH_REMATCH[1]}"
    elif [[ "${command}" =~ -m[[:space:]]+\"([^\"]+)\" ]]; then
        commit_msg="${BASH_REMATCH[1]}"
    elif [[ "${command}" =~ -m[[:space:]]+\'([^\']+)\' ]]; then
        commit_msg="${BASH_REMATCH[1]}"
    elif [[ "${command}" =~ -m[[:space:]]+([^[:space:]]+) ]]; then
        commit_msg="${BASH_REMATCH[1]}"
    fi

    if [[ -n "${commit_msg}" ]]; then
        # Get subject (first line)
        subject="$(echo "${commit_msg}" | head -1)"

        # Check for vague subjects
        vague_patterns=(
            "^[Ff]ix bug$" "^[Ff]ix build$" "^[Ff]ix$"
            "^[Aa]dd patch$" "^[Uu]pdate$" "^[Uu]pdates$"
            "^[Ww]ip$" "^[Ww]ork in progress$" "^[Cc]hanges$"
            "^[Pp]hase [0-9]" "^[Mm]oving code" "^[Mm]iscellaneous"
            "^[Mm]isc$" "^[Ff]ixes$" "^[Ss]tuff$"
            "^[Rr]efactoring$" "^[Rr]efactor$" "^[Cc]leanup$" "^[Cc]lean up$"
        )

        for pattern in "${vague_patterns[@]}"; do
            if echo "${subject}" | grep -qE "${pattern}"; then
                commit_issues="Vague subject '${subject}' - be specific about WHAT changed"
                break
            fi
        done

        # Check subject length
        subject_len="${#subject}"
        if (( subject_len > 100 )); then
            commit_issues="${commit_issues:+${commit_issues}; }Subject too long (${subject_len} chars) - max 100"
        fi

        # Check imperative mood
        if echo "${subject}" | grep -qE "^[A-Z][a-z]+ing "; then
            commit_issues="${commit_issues:+${commit_issues}; }Use imperative mood: 'Add' not 'Adding'"
        elif echo "${subject}" | grep -qE "^[A-Z][a-z]+ed "; then
            commit_issues="${commit_issues:+${commit_issues}; }Use imperative mood: 'Add' not 'Added'"
        elif echo "${subject}" | grep -qE "^[A-Z][a-z]+s "; then
            commit_issues="${commit_issues:+${commit_issues}; }Use imperative mood: 'Add' not 'Adds'"
        fi

        # Check for period at end
        if [[ "${subject}" =~ \.$ ]]; then
            commit_issues="${commit_issues:+${commit_issues}; }Subject must not end with period"
        fi

        # If issues found, BLOCK the commit (not just warn)
        if [[ -n "${commit_issues}" ]]; then
            escaped_msg="$(printf '%s' "${commit_issues}" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"
            cat <<EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "BLOCKED: ${escaped_msg}\\n\\nGood format: Imperative verb + specific change (50-72 chars)\\nExample: 'Add rate limiting to auth endpoint'"
}
EOF
            exit 0
        fi
    fi
fi

# === DESTRUCTIVE COMMAND CHECKS ===
destructive_blocked=""

# git reset --hard (dangerous without backup)
if [[ "${command}" =~ git[[:space:]]+reset[[:space:]]+--hard ]]; then
    # Check if backup branch exists
    backup_exists="$(git branch --list 'backup/*' 2>/dev/null | head -1 || echo "")"
    if [[ -z "${backup_exists}" ]]; then
        destructive_blocked="git reset --hard without backup branch"
    fi
fi

# git push --force or -f (always warn)
if [[ "${command}" =~ git[[:space:]]+push[[:space:]]+(--force|-f) ]]; then
    destructive_blocked="git push --force is dangerous"
fi

# git branch -D (delete branch permanently)
if [[ "${command}" =~ git[[:space:]]+branch[[:space:]]+-D ]]; then
    # Allow if it's not the current branch
    current="$(git branch --show-current 2>/dev/null || echo "")"
    if [[ "${command}" =~ ${current} ]]; then
        destructive_blocked="Cannot delete current branch"
    fi
fi

# git clean -fd (remove untracked files)
if [[ "${command}" =~ git[[:space:]]+clean[[:space:]]+-[[:alnum:]]*f ]]; then
    destructive_blocked="git clean removes untracked files permanently"
fi

# Output result
if [[ -n "${destructive_blocked}" ]]; then
    # Escape message for JSON
    escaped_msg="$(printf '%s' "${destructive_blocked}" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')"

    cat <<EOF
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "BLOCKED: ${escaped_msg}. Create a backup branch first: git branch backup/\$(git branch --show-current)-\$(date +%Y%m%d-%H%M%S)"
}
EOF
else
    echo '{}'
fi

exit 0

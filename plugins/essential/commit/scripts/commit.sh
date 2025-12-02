#!/usr/bin/env bash
# Safe git commit wrapper that handles shell quoting
# Usage: commit.sh "subject" ["body"]
#
# Examples:
#   commit.sh "feat: add user authentication"
#   commit.sh "fix: resolve race condition" "The mutex was not being released..."

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: commit.sh \"subject\" [\"body\"]" >&2
    exit 1
fi

subject="$1"
body="${2:-}"

if [[ -z "$body" ]]; then
    git commit -F - <<EOF
$subject
EOF
else
    git commit -F - <<EOF
$subject

$body
EOF
fi

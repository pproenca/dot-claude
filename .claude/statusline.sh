#!/bin/bash
set -euo pipefail

json=$(cat) || { echo "[unknown] . | \$0.00"; exit 0; }
[[ -z "$json" ]] && { echo "[unknown] . | \$0.00"; exit 0; }

if ! echo "$json" | jq empty 2>/dev/null; then
    echo "[unknown] . | \$0.00"
    exit 0
fi

model=$(echo "$json" | jq -r '.model.display_name // .model.id // "unknown"')
cost=$(echo "$json" | jq -r '.cost.total_cost_usd // 0')
cwd=$(echo "$json" | jq -r '.cwd // "."' | xargs basename)
printf "[%s] %s | \$%.2f\n" "$model" "$cwd" "$cost"

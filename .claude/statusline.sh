#!/usr/bin/env bash
set -euo pipefail

main() {
  local json
  local model
  local cost
  local cwd

  json="$(cat)" || { echo "[unknown] . | 0s | +0 -0 | \$0.00"; exit 0; }
  [[ -z "${json}" ]] && { echo "[unknown] . | 0s | +0 -0 | \$0.00"; exit 0; }

  if ! jq empty 2>/dev/null <<< "${json}"; then
    echo "[unknown] . | 0s | +0 -0 | \$0.00"
    exit 0
  fi

  model="$(jq -r '.model.display_name // .model.id // "unknown"' <<< "${json}")"
  cost="$(jq -r '.cost.total_cost_usd // 0' <<< "${json}")"
  cwd="$(basename "$(jq -r '.cwd // "."' <<< "${json}")")"

  # Duration formatting
  local duration_ms duration_s minutes seconds duration_str
  duration_ms="$(jq -r '.cost.total_duration_ms // 0' <<< "${json}")"
  duration_s=$((duration_ms / 1000))
  if (( duration_s >= 60 )); then
    minutes=$((duration_s / 60))
    seconds=$((duration_s % 60))
    duration_str="${minutes}m ${seconds}s"
  else
    duration_str="${duration_s}s"
  fi

  # Lines changed
  local lines_added lines_removed
  lines_added="$(jq -r '.cost.total_lines_added // 0' <<< "${json}")"
  lines_removed="$(jq -r '.cost.total_lines_removed // 0' <<< "${json}")"

  printf "[%s] %s | %s | +%d -%d | \$%.2f\n" "${model}" "${cwd}" "${duration_str}" "${lines_added}" "${lines_removed}" "${cost}"
}

main "$@"

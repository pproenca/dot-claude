#!/usr/bin/env bash
# mancat - Non-interactive man page viewer for Claude Code
# Usage: mancat <command> [section]
#        mancat -s <section> <command>  # Extract specific section (OPTIONS, SYNOPSIS, etc.)
#        mancat -k <keyword>            # Search man pages (apropos)

set -euo pipefail

err() {
  echo "mancat: $*" >&2
}

usage() {
  cat <<'EOF'
Usage: mancat [OPTIONS] <command> [man-section]

Options:
  -s SECTION   Extract specific section (OPTIONS, SYNOPSIS, DESCRIPTION, etc.)
  -k KEYWORD   Search man page descriptions (like apropos)
  -h           Show this help

Examples:
  mancat ls              # Full man page, clean output
  mancat 5 passwd        # Section 5 (file formats)
  mancat -s OPTIONS tar  # Just the OPTIONS section
  mancat -k compress     # Search for compression tools
EOF
}

extract_section() {
  local section="$1"
  awk -v sec="${section}" '
    $0 ~ "^" sec { found=1 }
    found && /^[A-Z][A-Z]/ && $0 !~ "^" sec { exit }
    found { print }
  '
}

main() {
  local section=""
  local search=""
  local cmd
  local man_section
  local -a man_cmd

  while getopts "s:k:h" opt; do
    case "${opt}" in
      s) section="${OPTARG}" ;;
      k) search="${OPTARG}" ;;
      h) usage; exit 0 ;;
      *) usage; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))

  if [[ -n "${search}" ]]; then
    man -k "${search}" 2>/dev/null \
      || echo "No matches for: ${search}"
    exit 0
  fi

  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  cmd="$1"
  man_section="${2:-}"

  if [[ -n "${man_section}" ]]; then
    man_cmd=(man "${man_section}" "${cmd}")
    if ! man -w "${man_section}" "${cmd}" &>/dev/null; then
      err "No man page for '${cmd}' in section ${man_section}. Try: mancat -k ${cmd}"
      exit 1
    fi
  else
    man_cmd=(man "${cmd}")
    if ! man -w "${cmd}" &>/dev/null; then
      err "No man page for '${cmd}'. Try: mancat -k ${cmd}"
      exit 1
    fi
  fi

  if [[ -n "${section}" ]]; then
    "${man_cmd[@]}" 2>/dev/null | col -b | extract_section "${section}"
  else
    "${man_cmd[@]}" 2>/dev/null | col -b
  fi
}

main "$@"

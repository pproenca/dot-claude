#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

failed=0

echo "Validating marketplace..."
if ! claude plugin validate "${REPO_ROOT}"; then
  failed=1
fi

echo ""
echo "Validating plugins..."
for plugin_dir in "${REPO_ROOT}"/plugins/*/; do
  if ! claude plugin validate "${plugin_dir}"; then
    failed=1
  fi
done

echo ""
if [[ ${failed} -eq 0 ]]; then
  echo "All validations passed"
else
  echo "Some validations failed"
  exit 1
fi

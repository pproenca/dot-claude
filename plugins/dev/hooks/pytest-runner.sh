#!/usr/bin/env bash
# Pytest Runner - PostToolUse hook for automatic test execution
# Runs pytest after test file edits to provide immediate feedback

set -euo pipefail

main() {
  local input
  local file_path
  local tool_name

  input="$(cat)"
  file_path="$(jq -r '.tool_input.file_path // .tool_input.path // ""' <<< "${input}")"
  tool_name="$(jq -r '.tool_name // ""' <<< "${input}")"

  # Only run for Write/Edit operations
  if [[ "${tool_name}" != "Write" && "${tool_name}" != "Edit" ]]; then
    exit 0
  fi

  # If no file path found, skip
  if [[ -z "${file_path}" ]]; then
    exit 0
  fi

  # Only run for Python test files
  if [[ ! "${file_path}" =~ \.py$ ]]; then
    exit 0
  fi

  # Check if this is a test file
  if [[ ! "${file_path}" =~ (test_|_test\.py$|tests/|/test[^/]*\.py$) ]]; then
    exit 0
  fi

  # Check if file exists
  if [[ ! -f "${file_path}" ]]; then
    exit 0
  fi

  # Find project root (look for pyproject.toml, setup.py, or pytest.ini)
  local project_root
  project_root="$(dirname "${file_path}")"
  while [[ "${project_root}" != "/" ]]; do
    if [[ -f "${project_root}/pyproject.toml" ]] || \
       [[ -f "${project_root}/setup.py" ]] || \
       [[ -f "${project_root}/pytest.ini" ]] || \
       [[ -f "${project_root}/setup.cfg" ]]; then
      break
    fi
    project_root="$(dirname "${project_root}")"
  done

  # If no project root found, use file directory
  if [[ "${project_root}" == "/" ]]; then
    project_root="$(dirname "${file_path}")"
  fi

  # Check for pytest availability
  local pytest_cmd=""
  if [[ -f "${project_root}/uv.lock" ]] || [[ -f "${project_root}/.venv/bin/uv" ]]; then
    pytest_cmd="uv run pytest"
  elif [[ -f "${project_root}/.venv/bin/pytest" ]]; then
    pytest_cmd="${project_root}/.venv/bin/pytest"
  elif command -v pytest &> /dev/null; then
    pytest_cmd="pytest"
  else
    echo "ℹ️  pytest not found - install with: uv add --dev pytest"
    exit 0
  fi

  # Run pytest on the specific test file
  echo ""
  echo "🧪 Running tests: ${file_path##*/}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  cd "${project_root}"

  # Run pytest with verbose output, capture exit code
  local exit_code=0
  ${pytest_cmd} "${file_path}" -v --tb=short 2>&1 || exit_code=$?

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [[ ${exit_code} -eq 0 ]]; then
    echo "✅ Tests passed"
  else
    echo "❌ Tests failed (exit code: ${exit_code})"
  fi

  exit 0
}

main "$@"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "${SCRIPT_DIR}")"
HOOK_SCRIPT="${PLUGIN_ROOT}/hooks/blackbox.py"
DATA_DIR="${PLUGIN_ROOT}/data"

echo "=== Blackbox Integration Test ==="

# Clean up
rm -rf "${DATA_DIR}"

# Test 1: PreToolUse event
echo "Test 1: PreToolUse Write event..."
export CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT}"

echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"'"${SCRIPT_DIR}/fixtures/sample.txt"'"}}' | python3 -S "${HOOK_SCRIPT}"

if [[ -f "${DATA_DIR}/buffer.jsonl" ]]; then
    echo "  PASS: buffer.jsonl created"
else
    echo "  FAIL: buffer.jsonl not created"
    exit 1
fi

if [[ -d "${DATA_DIR}/objects" ]]; then
    echo "  PASS: objects directory created"
else
    echo "  FAIL: objects directory not created"
    exit 1
fi

# Test 2: SessionStart event
echo "Test 2: SessionStart event..."
echo '{"hook_event_name":"SessionStart"}' | python3 -S "${HOOK_SCRIPT}"

LINE_COUNT=$(wc -l < "${DATA_DIR}/buffer.jsonl" | tr -d ' ')
if [[ "${LINE_COUNT}" -eq 2 ]]; then
    echo "  PASS: Two events logged"
else
    echo "  FAIL: Expected 2 lines, got ${LINE_COUNT}"
    exit 1
fi

# Test 3: Binary file skipped
echo "Test 3: Binary file skipped..."
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"'"${SCRIPT_DIR}/fixtures/binary.png"'"}}' | python3 -S "${HOOK_SCRIPT}"

if grep -q '"skipped".*"binary_or_oversize"' "${DATA_DIR}/buffer.jsonl"; then
    echo "  PASS: Binary file marked as skipped"
else
    echo "  FAIL: Binary file not marked as skipped"
    exit 1
fi

echo "=== All integration tests passed ==="

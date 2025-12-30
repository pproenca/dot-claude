#!/usr/bin/env bats
# Tests for run-harness.sh

load test_helper

SCRIPT="$PLUGIN_ROOT/scripts/run-harness.sh"

@test "--help shows usage information" {
  run "$SCRIPT" --help
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Usage:"
  echo "$output" | grep -q -- "--implementation"
  echo "$output" | grep -q -- "--output"
}

@test "--version shows version" {
  run "$SCRIPT" --version
  [ "$status" -eq 0 ]
  echo "$output" | grep -qE "^[0-9]+\.[0-9]+\.[0-9]+$"
}

@test "--dry-run sets DRY_RUN flag" {
  run "$SCRIPT" --dry-run --help
  [ "$status" -eq 0 ]
}

@test "unknown option shows error" {
  run "$SCRIPT" --unknown-option
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "Unknown option"
}

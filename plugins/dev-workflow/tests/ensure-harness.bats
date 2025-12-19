#!/usr/bin/env bats

setup() {
  load '../scripts/ensure-harness.sh'
  # Mock harness command
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"
}

@test "ensure_harness returns 0 when daemon responds to ping" {
  # Mock harness ping succeeds
  echo '#!/bin/bash
echo "pong"
exit 0' > "$BATS_TEST_DIRNAME/mocks/harness"
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"

  run ensure_harness
  [ "$status" -eq 0 ]
}

@test "ensure_harness spawns daemon when ping fails then succeeds" {
  # First ping fails, second succeeds (daemon started)
  echo '#!/bin/bash
if [[ "$1" == "ping" ]]; then
  if [[ ! -f /tmp/harness-started ]]; then
    touch /tmp/harness-started
    exit 1
  fi
  echo "pong"
  exit 0
fi
exit 0' > "$BATS_TEST_DIRNAME/mocks/harness"
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"

  run ensure_harness
  [ "$status" -eq 0 ]
  rm -f /tmp/harness-started
}

@test "ensure_harness fails after timeout when daemon never starts" {
  echo '#!/bin/bash
exit 1' > "$BATS_TEST_DIRNAME/mocks/harness"
  chmod +x "$BATS_TEST_DIRNAME/mocks/harness"

  HARNESS_TIMEOUT=1 run ensure_harness
  [ "$status" -eq 1 ]
}

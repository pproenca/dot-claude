#!/usr/bin/env bats

setup() {
  load '../scripts/ensure-hyh.sh'
  # Mock uvx command (hyh is accessed via 'uvx hyh')
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"
}

@test "ensure_hyh returns 0 when daemon responds to ping" {
  # Mock uvx hyh ping succeeds
  echo '#!/bin/bash
# uvx receives: hyh <command>
if [[ "$1" == "hyh" && "$2" == "ping" ]]; then
  echo "pong"
  exit 0
fi
exit 0' > "$BATS_TEST_DIRNAME/mocks/uvx"
  chmod +x "$BATS_TEST_DIRNAME/mocks/uvx"

  run ensure_hyh
  [ "$status" -eq 0 ]
}

@test "ensure_hyh spawns daemon when ping fails then succeeds" {
  # First ping fails, second succeeds (daemon started)
  echo '#!/bin/bash
# uvx receives: hyh <command>
if [[ "$1" == "hyh" && "$2" == "ping" ]]; then
  if [[ ! -f /tmp/hyh-started ]]; then
    touch /tmp/hyh-started
    exit 1
  fi
  echo "pong"
  exit 0
fi
exit 0' > "$BATS_TEST_DIRNAME/mocks/uvx"
  chmod +x "$BATS_TEST_DIRNAME/mocks/uvx"

  run ensure_hyh
  [ "$status" -eq 0 ]
  rm -f /tmp/hyh-started
}

@test "ensure_hyh fails after timeout when daemon never starts" {
  echo '#!/bin/bash
exit 1' > "$BATS_TEST_DIRNAME/mocks/uvx"
  chmod +x "$BATS_TEST_DIRNAME/mocks/uvx"

  HYH_TIMEOUT=1 run ensure_hyh
  [ "$status" -eq 1 ]
}

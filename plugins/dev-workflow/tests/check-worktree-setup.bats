#!/usr/bin/env bats
# Tests for check-worktree-setup.sh

load test_helper

SCRIPT="$PLUGIN_ROOT/hooks/check-worktree-setup.sh"

setup() {
  setup_test_dir
  export CLAUDE_PROJECT_DIR="$TEST_DIR"
}

teardown() {
  teardown_test_dir
}

@test "is_configured returns false when settings file missing" {
  run "$SCRIPT"
  [ "$status" -eq 0 ]
  # Should output JSON warning
  echo "$output" | grep -q "hookSpecificOutput"
}

@test "is_configured returns false when settings has no additionalDirectories" {
  mkdir -p "$TEST_DIR/.claude"
  echo '{"permissions": {}}' > "$TEST_DIR/.claude/settings.json"

  run "$SCRIPT"
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "Worktree support not configured"
}

@test "is_configured returns true with tilde path" {
  mkdir -p "$TEST_DIR/.claude"
  cat > "$TEST_DIR/.claude/settings.json" << 'EOF'
{"permissions":{"additionalDirectories":["~/.dot-claude-worktrees"]}}
EOF

  run "$SCRIPT"
  [ "$status" -eq 0 ]
  # Should NOT output warning when configured
  [[ -z "$output" ]]
}

@test "is_configured returns true with expanded path" {
  mkdir -p "$TEST_DIR/.claude"
  cat > "$TEST_DIR/.claude/settings.json" << EOF
{"permissions":{"additionalDirectories":["$HOME/.dot-claude-worktrees"]}}
EOF

  run "$SCRIPT"
  [ "$status" -eq 0 ]
  [[ -z "$output" ]]
}

@test "outputs valid JSON when not configured" {
  run "$SCRIPT"
  [ "$status" -eq 0 ]
  assert_valid_json
}

@test "always exits with 0" {
  # Missing file
  run "$SCRIPT"
  [ "$status" -eq 0 ]

  # Invalid JSON in settings
  mkdir -p "$TEST_DIR/.claude"
  echo 'not json' > "$TEST_DIR/.claude/settings.json"
  run "$SCRIPT"
  [ "$status" -eq 0 ]
}

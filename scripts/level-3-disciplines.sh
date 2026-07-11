#!/usr/bin/env bash
# Level 3: Discipline Consistency
# Validates that the dev-skill plugin's discipline architecture is internally consistent:
# - Every discipline has required files (RECIPE.md, RUBRIC.md)
# - Anatomy layer is complete
# - Commands reference agents that exist

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)
DEV_SKILL="$MARKETPLACE_ROOT/plugins/dev-skill"

echo "=== Level 3: Discipline Consistency ==="

# Skip if dev-skill plugin doesn't exist
if [[ ! -d "$DEV_SKILL" ]]; then
  info "dev-skill plugin not found, skipping"
  exit 0
fi

# ============================================================================
# Discipline Directories
# ============================================================================

section "Discipline Structure"

DISCIPLINES_DIR="$DEV_SKILL/templates/disciplines"
EXPECTED_DISCIPLINES=(distillation composition investigation extraction)

for discipline in "${EXPECTED_DISCIPLINES[@]}"; do
  disc_dir="$DISCIPLINES_DIR/$discipline"

  if [[ ! -d "$disc_dir" ]]; then
    err "Missing discipline directory: templates/disciplines/$discipline"
    continue
  fi

  # RECIPE.md required
  if [[ -f "$disc_dir/RECIPE.md" ]]; then
    ok "$discipline: RECIPE.md present"
  else
    err "$discipline: missing RECIPE.md"
  fi

  # RUBRIC.md required
  if [[ -f "$disc_dir/RUBRIC.md" ]]; then
    ok "$discipline: RUBRIC.md present"
  else
    err "$discipline: missing RUBRIC.md"
  fi

  # At least one template
  template_count=$(find "$disc_dir" -name "*.template" -o -name "SKILL.md.template" 2>/dev/null | wc -l | xargs)
  if [[ "$template_count" -gt 0 ]]; then
    ok "$discipline: $template_count template(s) present"
  else
    warn "$discipline: no template files found"
  fi
done

# ============================================================================
# Anatomy Layer
# ============================================================================

section "Anatomy Layer"

ANATOMY_DIR="$DEV_SKILL/templates/anatomy"

for required_file in ANATOMY.md SKILL.md.template metadata.json.template; do
  if [[ -f "$ANATOMY_DIR/$required_file" ]]; then
    ok "anatomy/$required_file present"
  else
    err "anatomy/$required_file missing"
  fi
done

# ============================================================================
# Agent References from Commands
# ============================================================================

section "Command → Agent References"

AGENTS_DIR="$DEV_SKILL/agents"

# Check that agents referenced in commands actually exist
for cmd_file in "$DEV_SKILL"/commands/*.md; do
  [[ -f "$cmd_file" ]] || continue
  cmd_name=$(basename "$cmd_file" .md)

  # Extract agent references: agents/X.md patterns (the last component)
  while IFS= read -r agent_ref; do
    # agent_ref is like "agents/analyzer.md" — extract just the filename
    agent_basename=$(basename "$agent_ref")
    agent_file="$AGENTS_DIR/$agent_basename"
    if [[ -f "$agent_file" ]]; then
      : # ok
    else
      err "commands/$cmd_name references $agent_ref which doesn't exist"
    fi
  done < <(grep -oE 'agents/[a-z_-]+\.md' "$cmd_file" 2>/dev/null | sort -u || true)
done

ok "Command → Agent references validated"

# ============================================================================
# validate-skill.js self-test
# ============================================================================

section "Validator Self-Test"

VALIDATOR="$DEV_SKILL/scripts/validate-skill.js"

if [[ -f "$VALIDATOR" ]] && command -v node &>/dev/null; then
  # Check that the validator's modules resolve (it exits 1 with no args, so check the import chain)
  if (cd "$DEV_SKILL" && node -e "import('./scripts/validation/validator.js').then(() => process.exit(0)).catch(e => { console.error(e.message); process.exit(1); })" 2>/dev/null); then
    ok "validate-skill.js module chain loads"
  else
    err "validate-skill.js module chain fails to load (run: cd plugins/dev-skill && npm install)"
  fi
else
  warn "validate-skill.js or node not available"
fi

exit_with_summary

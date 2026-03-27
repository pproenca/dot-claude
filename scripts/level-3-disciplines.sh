#!/usr/bin/env bash
# Level 3: Discipline Consistency
# Validates that the dev-skill plugin's discipline architecture is internally consistent:
# - Every discipline has required files (RECIPE.md, RUBRIC.md)
# - Anatomy layer is complete
# - Python eval scripts compile and import
# - Commands reference agents that exist

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/common.sh"

MARKETPLACE_ROOT=$(get_marketplace_root)
DEV_SKILL="$MARKETPLACE_ROOT/plugins/dev-skill"

echo "=== Level 3: Discipline & Eval Consistency ==="

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

# EVAL_GUIDE.md (required for eval flow)
if [[ -f "$ANATOMY_DIR/EVAL_GUIDE.md" ]]; then
  ok "anatomy/EVAL_GUIDE.md present"
else
  warn "anatomy/EVAL_GUIDE.md missing (eval flow won't have discipline-specific guidance)"
fi

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
# Python Eval Scripts
# ============================================================================

section "Python Eval Scripts"

EVAL_DIR="$DEV_SKILL/scripts/eval"

if [[ ! -d "$EVAL_DIR" ]]; then
  warn "scripts/eval/ directory not found (eval flow not installed)"
else
  # Syntax check all .py files
  py_errors=0
  py_count=0

  for pyfile in "$EVAL_DIR"/*.py; do
    [[ -f "$pyfile" ]] || continue
    py_name=$(basename "$pyfile")
    py_count=$((py_count + 1))

    if python3 -m py_compile "$pyfile" 2>/dev/null; then
      : # ok
    else
      err "scripts/eval/$py_name: Python syntax error"
      py_errors=$((py_errors + 1))
    fi
  done

  if [[ $py_errors -eq 0 && $py_count -gt 0 ]]; then
    ok "All $py_count eval scripts pass syntax check"
  fi

  # Import check for critical modules (run from plugin root for correct module path)
  if (cd "$DEV_SKILL" && python3 -c "from scripts.eval.utils import parse_skill_md" 2>/dev/null); then
    ok "scripts.eval.utils imports successfully"
  else
    err "scripts.eval.utils failed to import (run: cd plugins/dev-skill && python3 -c 'from scripts.eval.utils import parse_skill_md')"
  fi

  if (cd "$DEV_SKILL" && python3 -c "from scripts.eval.run_eval import run_eval" 2>/dev/null); then
    ok "scripts.eval.run_eval imports successfully"
  else
    err "scripts.eval.run_eval failed to import"
  fi

  if (cd "$DEV_SKILL" && python3 -c "from scripts.eval.aggregate_benchmark import generate_benchmark" 2>/dev/null); then
    ok "scripts.eval.aggregate_benchmark imports successfully"
  else
    err "scripts.eval.aggregate_benchmark failed to import"
  fi
fi

# ============================================================================
# Eval Viewer
# ============================================================================

section "Eval Viewer"

VIEWER_DIR="$DEV_SKILL/eval-viewer"

if [[ -d "$VIEWER_DIR" ]]; then
  for required in generate_review.py viewer.html; do
    if [[ -f "$VIEWER_DIR/$required" ]]; then
      ok "eval-viewer/$required present"
    else
      err "eval-viewer/$required missing"
    fi
  done
else
  warn "eval-viewer/ directory not found (eval flow not installed)"
fi

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

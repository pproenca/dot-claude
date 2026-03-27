#!/usr/bin/env bash
# Golden Set Regression Runner
#
# Generates a minimal skill for each of the 9 types and validates structurally.
# This is the cheap, fast tier — run on every change to commands/templates.
#
# Usage:
#   bash tests/golden-set/run.sh                  # Run from plugin root
#   bash tests/golden-set/run.sh --type=runbook   # Run one type only
#   bash tests/golden-set/run.sh --verbose        # Show validator output
#
# Requires: node, jq

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SPECS_FILE="$SCRIPT_DIR/specs.json"
OUTPUT_DIR="/tmp/golden-set-$(date +%Y%m%d-%H%M%S)"
VALIDATOR="$PLUGIN_ROOT/scripts/validate-skill.js"

# Options
FILTER_TYPE=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type=*) FILTER_TYPE="${1#*=}"; shift ;;
    --verbose) VERBOSE=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Check dependencies
if ! command -v node &>/dev/null; then
  echo "Error: node is required" >&2
  exit 1
fi
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "Golden Set Regression Runner"
echo "========================================"
echo "Output: $OUTPUT_DIR"
echo ""

TOTAL=0
PASSED=0
FAILED=0
RESULTS=()

# Read specs
SPEC_COUNT=$(jq '.specs | length' "$SPECS_FILE")

for i in $(seq 0 $((SPEC_COUNT - 1))); do
  TYPE=$(jq -r ".specs[$i].type" "$SPECS_FILE")
  DISCIPLINE=$(jq -r ".specs[$i].discipline" "$SPECS_FILE")
  TECHNOLOGY=$(jq -r ".specs[$i].spec.technology" "$SPECS_FILE")

  # Filter if specified
  if [[ -n "$FILTER_TYPE" && "$TYPE" != "$FILTER_TYPE" ]]; then
    continue
  fi

  TOTAL=$((TOTAL + 1))
  SKILL_NAME="golden-test-${TYPE}"
  SKILL_DIR="$OUTPUT_DIR/$SKILL_NAME"

  echo "--- [$TYPE] $TECHNOLOGY ($DISCIPLINE) ---"

  # Generate minimal skill based on discipline
  mkdir -p "$SKILL_DIR"

  # === SKILL.md ===
  case "$DISCIPLINE" in
    distillation)
      DESCRIPTION="Use this skill whenever writing, reviewing, or refactoring ${TECHNOLOGY} code for quality and performance. Trigger even if the user doesn't explicitly mention best practices."
      cat > "$SKILL_DIR/SKILL.md" << SKILL_EOF
---
name: $SKILL_NAME
description: $DESCRIPTION
---

# Golden Test ${TECHNOLOGY} Best Practices

Performance and quality guidelines for ${TECHNOLOGY} applications.

## When to Apply

Reference these guidelines when:
- Writing new ${TECHNOLOGY} code
- Reviewing ${TECHNOLOGY} code for quality
- Refactoring existing ${TECHNOLOGY} code
- Debugging performance issues in ${TECHNOLOGY}

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Core Patterns | CRITICAL | core- |
| 2 | Code Organization | HIGH | org- |

## Quick Reference

### 1. Core Patterns (CRITICAL)

- [\`core-pattern-one\`](references/core-pattern-one.md) - First core pattern
- [\`core-pattern-two\`](references/core-pattern-two.md) - Second core pattern
- [\`core-pattern-three\`](references/core-pattern-three.md) - Third core pattern

### 2. Code Organization (HIGH)

- [\`org-structure-one\`](references/org-structure-one.md) - First org pattern
- [\`org-structure-two\`](references/org-structure-two.md) - Second org pattern

## How to Use

Read individual reference files for detailed explanations and code examples:
- [Section definitions](references/_sections.md) - Category structure and impact levels
- [Rule template](assets/templates/_template.md) - Template for adding new rules
SKILL_EOF

      # === references/_sections.md ===
      mkdir -p "$SKILL_DIR/references"
      cat > "$SKILL_DIR/references/_sections.md" << 'SECTIONS_EOF'
# Sections

## 1. Core Patterns (core)

**Impact:** CRITICAL
**Description:** Foundational patterns that affect all downstream operations

## 2. Code Organization (org)

**Impact:** HIGH
**Description:** Structural patterns for maintainability and clarity
SECTIONS_EOF

      # === Generate rule files ===
      for n in one two three; do
        cat > "$SKILL_DIR/references/core-pattern-${n}.md" << RULE_EOF
---
title: Use Pattern ${n^} for Safety
impact: CRITICAL
impactDescription: prevents common runtime errors
tags: core, safety, patterns
---

## Use Pattern ${n^} for Safety

When you skip this pattern, the code silently fails at runtime because the default behavior doesn't handle the edge case. This cascades into hard-to-debug issues downstream.

**Incorrect (missing safety check):**

\`\`\`${TECHNOLOGY,,}
// Unsafe: no validation before use
result := process(input)
\`\`\`

**Correct (with safety check):**

\`\`\`${TECHNOLOGY,,}
// Safe: validates before processing
if err := validate(input); err != nil {
    return fmt.Errorf("invalid input: %w", err)
}
result := process(input)
\`\`\`

Reference: [${TECHNOLOGY} Documentation](https://example.com)
RULE_EOF
      done

      for n in one two; do
        cat > "$SKILL_DIR/references/org-structure-${n}.md" << RULE_EOF
---
title: Organize ${n^} by Domain
impact: HIGH
impactDescription: reduces coupling between modules
tags: org, structure, modules
---

## Organize ${n^} by Domain

Grouping by technical layer (all controllers together, all models together) forces changes to touch multiple directories. Grouping by domain keeps related code co-located, reducing cognitive load.

**Incorrect (layered structure):**

\`\`\`${TECHNOLOGY,,}
// controllers/user.go + models/user.go + services/user.go
// Changes to "user" feature touch 3 directories
\`\`\`

**Correct (domain structure):**

\`\`\`${TECHNOLOGY,,}
// user/handler.go + user/model.go + user/service.go
// All user code in one place
\`\`\`
RULE_EOF
      done

      # === assets/templates/_template.md ===
      mkdir -p "$SKILL_DIR/assets/templates"
      cat > "$SKILL_DIR/assets/templates/_template.md" << 'TEMPLATE_EOF'
---
title: {Rule Title}
impact: {CRITICAL|HIGH|MEDIUM|LOW}
impactDescription: {quantified impact}
tags: {prefix}, {tag1}, {tag2}
---

## {Rule Title}

{Why this matters.}

**Incorrect ({problem}):**

```
{bad code}
```

**Correct ({solution}):**

```
{good code}
```
TEMPLATE_EOF
      ;;

    composition)
      DESCRIPTION="Use this skill whenever you need to ${TECHNOLOGY,,} — automates the multi-step workflow with verification and error handling."
      cat > "$SKILL_DIR/SKILL.md" << SKILL_EOF
---
name: $SKILL_NAME
description: $DESCRIPTION
---

# Golden Test ${TECHNOLOGY} Workflow

Automates the ${TECHNOLOGY,,} process with verification.

## When to Apply

Use this skill when:
- Running the ${TECHNOLOGY,,} workflow
- Verifying ${TECHNOLOGY,,} results
- Automating repetitive ${TECHNOLOGY,,} tasks

## Workflow Overview

\`\`\`
Step 1 → Step 2 → Verification
     ↓ (on failure)
  Error handling
\`\`\`

| Step | Action | Script |
|------|--------|--------|
| 1 | Execute | scripts/run.sh |
| 2 | Verify | scripts/verify.sh |

## How to Use

1. Run the workflow: \`bash scripts/run.sh\`
2. Verify results: \`bash scripts/verify.sh\`

See [workflow details](references/workflow.md) for step-by-step documentation.
SKILL_EOF

      mkdir -p "$SKILL_DIR/scripts"
      cat > "$SKILL_DIR/scripts/run.sh" << 'SCRIPT_EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <target>" >&2
  exit 1
fi

TARGET="$1"
echo "Running workflow for: $TARGET"
echo "Step 1: Execute... done"
echo "Step 2: Verify... done"
SCRIPT_EOF
      chmod +x "$SKILL_DIR/scripts/run.sh"

      cat > "$SKILL_DIR/scripts/verify.sh" << 'SCRIPT_EOF'
#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
assert_eq() { if [[ "$2" == "$3" ]]; then echo "  PASS: $1"; ((PASS++)); else echo "  FAIL: $1"; ((FAIL++)); fi; }
echo "Verification results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
SCRIPT_EOF
      chmod +x "$SKILL_DIR/scripts/verify.sh"

      mkdir -p "$SKILL_DIR/references"
      echo "# Workflow Reference" > "$SKILL_DIR/references/workflow.md"
      echo "Step-by-step documentation for the ${TECHNOLOGY,,} workflow." >> "$SKILL_DIR/references/workflow.md"
      ;;

    investigation)
      DESCRIPTION="Use this skill to investigate and diagnose issues with the ${TECHNOLOGY,,} — follows structured decision trees with diagnostic queries."
      cat > "$SKILL_DIR/SKILL.md" << SKILL_EOF
---
name: $SKILL_NAME
description: $DESCRIPTION
---

# Golden Test ${TECHNOLOGY} Runbook

Structured investigation and diagnosis for ${TECHNOLOGY,,} issues.

## When to Apply

Use this skill when:
- ${TECHNOLOGY} is showing errors or degraded performance
- Investigating incidents involving ${TECHNOLOGY,,}
- Running diagnostic queries against ${TECHNOLOGY,,}

## Common Symptoms

| Symptom | Usual Cause | Quick Check | Tree |
|---------|-------------|-------------|------|
| High latency | Database locks | \`queries/slow.sql\` | [latency-tree](references/latency-tree.md) |
| Error spike | Bad deploy | \`git log -5\` | [errors-tree](references/errors-tree.md) |

## How to Use

1. Identify the symptom in the table above
2. Follow the linked decision tree
3. Use queries in references/queries/ at each decision point
4. Produce a report using assets/templates/report.md
SKILL_EOF

      mkdir -p "$SKILL_DIR/references/queries"
      cat > "$SKILL_DIR/references/symptoms.md" << 'SYM_EOF'
# Symptom Catalog

| # | Symptom | Entry Point | Severity |
|---|---------|-------------|----------|
| 1 | High latency | latency-tree.md | P1 |
| 2 | Error spike | errors-tree.md | P1 |
SYM_EOF

      cat > "$SKILL_DIR/references/latency-tree.md" << 'TREE_EOF'
# Decision Tree: High Latency

**Check:** Is latency elevated across all endpoints?
- **Yes** → Check database: `queries/slow.sql`
  - Slow query found → **Resolution:** Kill query, investigate lock
  - No slow queries → **Escalate:** Infrastructure team
- **No** → Check recent deploys: `git log --oneline -5`
  - Recent deploy found → **Resolution:** Rollback and investigate
  - No recent deploy → **Escalate:** Service owner
TREE_EOF

      cat > "$SKILL_DIR/references/errors-tree.md" << 'TREE_EOF'
# Decision Tree: Error Spike

**Check:** Are errors from one endpoint or many?
- **One endpoint** → Check recent changes to that handler
  - Changes found → **Resolution:** Revert the change
  - No changes → **Escalate:** Service owner
- **Many endpoints** → Check upstream dependencies
  - Upstream down → **Resolution:** Enable circuit breaker
  - Upstream healthy → **Escalate:** Infrastructure team
TREE_EOF

      cat > "$SKILL_DIR/references/queries/slow.sql" << 'SQL_EOF'
-- Find queries running longer than 1000ms
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '1000 milliseconds'
ORDER BY duration DESC;
SQL_EOF

      mkdir -p "$SKILL_DIR/assets/templates"
      echo "# Investigation Report: {Symptom}" > "$SKILL_DIR/assets/templates/report.md"
      echo "**Date:** {date}" >> "$SKILL_DIR/assets/templates/report.md"
      echo "## Summary" >> "$SKILL_DIR/assets/templates/report.md"
      echo "## Root Cause" >> "$SKILL_DIR/assets/templates/report.md"
      echo "## Resolution" >> "$SKILL_DIR/assets/templates/report.md"
      ;;

    extraction)
      DESCRIPTION="Use this skill to scaffold new ${TECHNOLOGY} components following team conventions — generates files from parameterized templates."
      cat > "$SKILL_DIR/SKILL.md" << SKILL_EOF
---
name: $SKILL_NAME
description: $DESCRIPTION
---

# Golden Test ${TECHNOLOGY} Scaffold

Generate ${TECHNOLOGY} components from parameterized templates.

## When to Apply

Use this skill when:
- Creating a new ${TECHNOLOGY} component
- Scaffolding a new module or feature
- Need to follow team conventions for ${TECHNOLOGY}

## Available Templates

| Template | Produces | Parameters |
|----------|----------|------------|
| [component](assets/templates/component.template) | Component + test | name, type |
| [hook](assets/templates/hook.template) | Custom hook + test | name |

## How to Use

1. Tell Claude what you want to create
2. Claude reads the appropriate template and generates files
3. Review generated files and fill in implementation

See [conventions](references/conventions.md) for the standards these templates enforce.
SKILL_EOF

      mkdir -p "$SKILL_DIR/assets/templates"
      cat > "$SKILL_DIR/assets/templates/component.template" << 'TPL_EOF'
// {name}.tsx — {description}
import React from 'react';

interface {Name}Props {
  // Add props here
}

export function {Name}({ }: {Name}Props) {
  return <div>{Name}</div>;
}
TPL_EOF

      cat > "$SKILL_DIR/assets/templates/hook.template" << 'TPL_EOF'
// use-{name}.ts — Custom hook for {description}
import { useState, useEffect } from 'react';

export function use{Name}() {
  // Implementation here
  return {};
}
TPL_EOF

      mkdir -p "$SKILL_DIR/references"
      cat > "$SKILL_DIR/references/conventions.md" << 'CONV_EOF'
# Conventions

## File Naming: kebab-case
Files use kebab-case (e.g., `user-profile.tsx`).
**Why:** Filesystem case sensitivity across OS.

## Component Naming: PascalCase
Components use PascalCase (e.g., `UserProfile`).
**Why:** Distinguishes components from utilities in imports.

## Test Co-location
Tests live next to the code they test (e.g., `user-profile.test.tsx`).
**Why:** Easy to find and maintain.
CONV_EOF
      ;;
  esac

  # === metadata.json (all disciplines) ===
  DISC_FIELD=$(jq -r ".specs[$i].structural_checks.metadata_fields.discipline" "$SPECS_FILE")
  TYPE_FIELD=$(jq -r ".specs[$i].structural_checks.metadata_fields.type" "$SPECS_FILE")
  cat > "$SKILL_DIR/metadata.json" << META_EOF
{
  "version": "0.1.0",
  "organization": "golden-test",
  "technology": "$TECHNOLOGY",
  "discipline": "$DISC_FIELD",
  "type": "$TYPE_FIELD",
  "date": "$(date +'%B %Y')",
  "abstract": "Golden set test skill for ${TYPE} (${DISCIPLINE} discipline). This is a minimal skill generated for regression testing of the dev-skill plugin's generation pipeline.",
  "references": ["https://example.com/docs"]
}
META_EOF

  # === Validate ===
  if $VERBOSE; then
    node "$VALIDATOR" "$SKILL_DIR" 2>&1
    RESULT=$?
  else
    OUTPUT=$(node "$VALIDATOR" "$SKILL_DIR" 2>&1)
    RESULT=$?
  fi

  ERRORS=$(echo "$OUTPUT" | grep -c "✗" 2>/dev/null || echo "0")

  if [[ $RESULT -eq 0 ]]; then
    WARNINGS=$(echo "$OUTPUT" | grep -c "⚠" 2>/dev/null || echo "0")
    echo "  PASS ($WARNINGS warnings)"
    PASSED=$((PASSED + 1))
    RESULTS+=("PASS $TYPE ($DISCIPLINE) - $WARNINGS warnings")
  else
    echo "  FAIL ($ERRORS errors)"
    if ! $VERBOSE; then
      echo "$OUTPUT" | grep "✗" 2>/dev/null || true
    fi
    FAILED=$((FAILED + 1))
    RESULTS+=("FAIL $TYPE ($DISCIPLINE) - $ERRORS errors")
  fi
  echo ""
done

# Summary
echo "========================================"
echo "Results: $PASSED/$TOTAL passed, $FAILED failed"
echo "========================================"
for result in "${RESULTS[@]}"; do
  echo "  $result"
done

# Save metrics
METRICS_FILE="$OUTPUT_DIR/metrics.json"
cat > "$METRICS_FILE" << METRICS_EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit": "$(git -C "$PLUGIN_ROOT" rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "total": $TOTAL,
  "passed": $PASSED,
  "failed": $FAILED,
  "results": [$(printf '"%s",' "${RESULTS[@]}" | sed 's/,$//')]
}
METRICS_EOF

echo ""
echo "Metrics: $METRICS_FILE"
echo "Skills: $OUTPUT_DIR"

exit $FAILED

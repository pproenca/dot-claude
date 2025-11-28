---
description: Refactor a shell script to follow Google Shell Style Guide
argument-hint: path/to/script.sh
allowed-tools: [Bash, Read, Edit, Glob, AskUserQuestion, Task]
---

# Refactor Shell Script to Google Style Guide

Refactor the specified shell script to follow Google Shell Style Guide.

## Step 1: Identify Target Script

If `$ARGUMENTS` is provided, use it as the target script path. Store this path for use in all subsequent steps.

Otherwise, find shell scripts in the project and prompt user:

```bash
fd -e sh -e bash --type f 2>/dev/null | head -20
```

Use AskUserQuestion to let user select which file to refactor:

### File Selection
- Header: "Script"
- Question: "Which shell script would you like to refactor?"
- Options: [dynamically populated from fd results, up to 4 scripts]

**Important:** Store the selected/provided script path. You will need this exact path for shellcheck, verification, and dispatching the shell-expert agent.

## Step 2: Read Script and Analyze

Read the target script content to understand its structure and identify style issues.

## Step 3: Run Shellcheck Analysis

Before manual analysis, run shellcheck on the script to identify issues:

```bash
shellcheck -f gcc "<target_script_path>" 2>&1 || true
```

If shellcheck is not installed, warn the user:
> Note: shellcheck is not installed. Consider installing it for better analysis:
> - macOS: `brew install shellcheck`
> - Linux: `apt install shellcheck`

Parse shellcheck output to:
- Identify error codes (SC1xxx = parsing, SC2xxx = quoting/expansion, SC3xxx = bashisms)
- Map issues to Google Style Guide rules
- Prioritize critical issues:
  - SC2086: Double quote to prevent globbing and word splitting
  - SC2046: Quote this to prevent word splitting
  - SC2006: Use $(...) notation instead of legacy backticks

## Step 4: Load Style Guide Knowledge

Reference the google-shell-style skill for refactoring rules. Key areas to check:

**Formatting:**
- 2-space indentation (no tabs)
- 80-char max line length
- `; then`/`; do` on same line as `if`/`for`/`while`
- Proper pipeline formatting

**Variables & Quoting:**
- Use `"${var}"` with braces and quotes
- Use `"$@"` for argument passing
- Quote command substitutions

**Commands:**
- `$(command)` not backticks
- `[[ ]]` not `[ ]` or `test`
- `(( ))` for arithmetic

**Functions & Structure:**
- `lower_case()` function naming
- `local` for function variables
- `main` function for multi-function scripts
- `main "$@"` as last line

**Avoid:**
- `eval`
- `let`, `expr`, `$[]`
- Aliases in scripts
- Pipes to while (use process substitution)

## Step 5: Identify All Violations

Combine shellcheck findings with manual style guide analysis. For each violation found, note:
- Line number
- Current code
- Recommended fix
- Rule reference (shellcheck code or style guide section)

## Step 6: Propose Changes

Present a summary of proposed changes:

**Summary format:**
- Total violations found: N
- Critical fixes (must apply): N
- Style improvements: N
- Estimated lines affected: N

Then use AskUserQuestion to confirm:

### Change Approval
- Header: "Refactor"
- Question: "How would you like to proceed with these changes?"
- Options:
  - Apply all: Apply all changes at once
  - Review each: Show me each change before applying
  - Critical only: Only apply critical fixes, skip style improvements
  - Cancel: Do not make any changes

## Step 7: Apply Refactoring

Use the Edit tool to apply approved changes to the script.

Apply changes in order:
1. Critical fixes first (security, correctness)
2. Structural changes (main function, function organization)
3. Formatting changes (indentation, line length)
4. Style improvements (variable braces, quoting)

## Step 8: Verify Refactored Script

After applying changes, run verification.

### Syntax Check
```bash
bash -n "<target_script_path>"
```
If syntax check fails, fix the issue before proceeding.

### Shellcheck Comparison
```bash
shellcheck -f gcc "<target_script_path>" 2>&1 || true
```

Compare with baseline from Step 3:
- Count errors/warnings before and after
- Refactoring should reduce issues, not add them
- If new issues appeared, investigate and fix

### Test Depth Selection

Use AskUserQuestion to ask how thoroughly to test:

**Header:** "Test"
**Question:** "How would you like to verify the script still works?"
**Options:**
- Syntax only: Syntax check passed, proceed to expert review
- Dry run: Also run --help or --dry-run if script supports it
- Manual: I'll test it myself before continuing

If user selects "Dry run" and script appears to support it:
```bash
"<target_script_path>" --help 2>&1 | head -20 || "<target_script_path>" --dry-run 2>&1 | head -20 || echo "Script does not support --help or --dry-run"
```

## Step 9: Dispatch Shell Expert Agent

Launch the shell-expert agent to validate the refactored script.

**Use the Task tool with these parameters:**
- `subagent_type`: `"shell:shell-expert"`
- `prompt`: Include the exact file path from Step 1

**Example Task prompt (replace the path with your actual target script):**
```
REVIEW the shell script at /Users/example/scripts/deploy.sh

This script was just refactored to follow Google Shell Style Guide. Analyze:
1. Structure (main function, function organization)
2. Safety (quoting, variable expansion, error handling)
3. Style (formatting, naming conventions)

Report issues by severity (Critical/Important/Minor) with specific line numbers.
Provide a final recommendation: PASS, NEEDS_FIXES, or CRITICAL_ISSUES.
```

**IMPORTANT:** The file path in the prompt must be the actual path you stored in Step 1, not a placeholder. The agent reads the file using this path.

## Step 10: Final Report

Present final results:

```
## Refactoring Complete

**File:** [actual path from Step 1]

### Changes Applied
- [List of key changes made, grouped by category]

### Shellcheck Comparison
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Errors | N | N | -N |
| Warnings | N | N | -N |
| Info | N | N | -N |

### Verification Results
- Syntax check: [PASS/FAIL]
- Shellcheck delta: [Improved/Same/Regressed]
- Test run: [PASS/SKIPPED/N/A]

### Shell Expert Assessment
- **Recommendation:** [PASS/NEEDS_FIXES/CRITICAL_ISSUES]
- **Confidence:** [HIGH/MODERATE/LOW]
- **Summary:** [1-2 sentence summary from agent]

### Remaining Items (if any)
- [Any issues the expert reviewer identified that need attention]
```

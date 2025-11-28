---
description: Refactor a shell script to follow Google Shell Style Guide
argument-hint: path/to/script.sh
allowed-tools: [Bash, Read, Edit, Glob, AskUserQuestion, Task]
---

# Refactor Shell Script to Google Style Guide

Refactor the specified shell script to follow Google Shell Style Guide.

## Step 1: Identify Target Script

If `$ARGUMENTS` is provided, use it as the target script path.

Otherwise, find shell scripts in the project and prompt user:

```bash
fd -e sh -e bash --type f 2>/dev/null | head -20
```

Use AskUserQuestion to let user select which file to refactor:

### File Selection
- Header: "Script"
- Question: "Which shell script would you like to refactor?"
- Options: [dynamically populated from fd results, up to 4 scripts]

## Step 2: Read Script and Analyze

Read the target script content to understand its structure and identify style issues.

## Step 3: Load Style Guide Knowledge

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

## Step 4: Analyze and Identify Violations

Analyze the script against style guide rules. For each violation found, note:
- Line number
- Current code
- Recommended fix
- Rule reference

## Step 5: Propose Changes

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

## Step 6: Apply Refactoring

Use the Edit tool to apply approved changes to the script.

Apply changes in order:
1. Critical fixes first (security, correctness)
2. Structural changes (main function, function organization)
3. Formatting changes (indentation, line length)
4. Style improvements (variable braces, quoting)

## Step 7: Dispatch Shell Expert Agent

Launch the shell-expert agent in REVIEW mode to validate the refactored script:

> Dispatch the shell-expert agent to review the refactored script at `<script_path>` using REVIEW mode. Verify it meets Google Shell Style Guide standards and report any remaining issues by severity.

## Step 8: Final Report

Present final results:

```
## Refactoring Complete

**File:** <script_path>

### Changes Applied
- [List of key changes made]

### Shell Expert Assessment
- [Pass/Needs attention based on agent feedback]

### Remaining Items (if any)
- [Any issues reviewer identified]
```

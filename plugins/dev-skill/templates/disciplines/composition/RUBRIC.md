# Composition Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Script Validity (check every script in scripts/)

For each script:

1. **Syntax check.** Run `bash -n {script}` (or equivalent for the script's language). Does it pass?
2. **Safety header.** Does the script begin with `set -euo pipefail` (or equivalent strict mode)?
3. **Input validation.** Does the script validate required arguments before proceeding?
4. **Error messages.** When the script fails, does it tell the user what to do next, not just what went wrong?
5. **Exit codes.** Does the script exit with appropriate codes? (0 = success, non-zero = failure)
6. **Tool availability.** Are all referenced commands/tools likely to be installed on the target system? Flag obscure dependencies that should be documented in SKILL.md.

Record each finding: script file, check performed, result (PASS/FAIL).

## Workflow Completeness

1. **Step coverage.** Is every step in the workflow diagram represented by either a script, a documented manual step, or a tool invocation?
2. **Failure paths.** For each step: what happens when it fails? Is there an error handler, a retry strategy, or at minimum a clear error message?
3. **Verification.** Is there a verification step that asserts the workflow succeeded? (Not just "command exited 0" but "state is correct")
4. **Resumability.** For multi-step workflows: if step 3 fails, can the user resume from step 3 without re-running steps 1-2? Is this documented?
5. **Idempotency.** Running the workflow twice: does it produce the same result, or does it create duplicates/conflicts?

## Guardrail Assessment (for write/destructive skills only)

Skip this section for read-only skills.

1. **Destructive operation detection.** List every command that modifies external state (git push, API calls, file deletion, resource creation). Are ALL of them guarded?
2. **Confirmation prompts.** Do destructive operations require explicit user confirmation before executing?
3. **Dry-run mode.** Can the user preview what would happen without executing? Is the dry-run output realistic (not just "would do X")?
4. **Rollback documentation.** For each destructive step: is there a documented way to undo it? Are the undo steps concrete (exact commands), not vague ("revert the changes")?
5. **Hook effectiveness.** If hooks/hooks.json exists: do the PreToolUse matchers actually catch the dangerous patterns? Test by mentally running a destructive command through the matcher.

## Setup & Configuration

1. **Config completeness.** Does `config.json` (if present) have `_setup_instructions` for every field?
2. **Graceful handling.** If config is missing or incomplete, does the skill detect this and prompt the user? (Not crash with a cryptic error)
3. **Secret safety.** Are secrets referenced by environment variable name, never stored as values in config.json?
4. **Documentation.** Does SKILL.md explain what needs to be configured and how?

## Usefulness Assessment

1. **Value proposition.** Does this workflow actually save time vs doing it manually? Count the steps — if the workflow is 2 steps that the user could type themselves, it's not worth being a skill.
2. **Generality.** Would this work across different projects, or is it hardcoded to one specific setup?
3. **Trust level.** Would an engineer trust this to run without supervision? If not, what would need to change?

## Verdict

- **SHIP**: All scripts pass syntax check. Error paths handled for every step. Guardrails present and effective for destructive ops. Config handles missing values gracefully.
- **NEEDS WORK**: Scripts valid but missing error handling for some steps, or guardrails incomplete, or config crashes on missing values. Specific fixes identified.
- **REJECT**: Scripts don't execute. Destructive operations ungated. Workflow has dead ends with no error handling. Unsafe for use.

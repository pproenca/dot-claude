# Composition Recipe

Composition takes tools, MCPs, scripts, and workflow steps and composes them into automated workflows. This is the production method for **Product Verification**, **Workflow Automation**, **CI/CD & Deployment**, and **Infrastructure Ops** skills.

## What Composition Produces

```
{skill-name}/
├── SKILL.md              # Workflow overview + trigger phrases
├── metadata.json         # discipline: "composition"
├── config.json           # User-specific setup (service URLs, channels, paths)
├── gotchas.md            # Failure points discovered over time
├── scripts/              # Executable scripts the skill uses
│   ├── {step-name}.sh    # Individual workflow steps
│   └── verify.sh         # Verification/assertion script
├── hooks/                # On-demand hooks (active during skill session)
│   └── hooks.json        # Hook definitions
└── references/
    └── workflow.md        # Detailed workflow documentation
```

## Inputs Needed

1. **Workflow description**: What process is being automated? What triggers it?
2. **Tool inventory**: What tools, MCPs, CLIs, or APIs does the workflow use?
3. **Success criteria**: How do you know the workflow succeeded?
4. **Risk assessment**: Read-only, write, or destructive operations?

## Discovery Workflow

### Step 1: Interview

Ask the user with `AskUserQuestion`:

```
Question: "What type of skill are you creating?"
Header: "Composition Type"
Options:
- "Verification — test and assert that code/features work correctly"
- "Workflow Automation — automate a repetitive multi-step process"
- "CI/CD & Deployment — build, test, deploy, and monitor"
- "Infrastructure Ops — operational procedures with safety guardrails"
```

Then ask free-form:
- "Describe the workflow step by step. What triggers it, what does each step do, and how do you know it worked?"
- "What tools do you use? (CLI commands, MCP servers, APIs, scripts)"

### Step 2: Map the Workflow

Structure the user's description into a workflow diagram:

```
Trigger → Step 1 → Step 2 → ... → Verification → Cleanup
              ↓ (on failure)
         Error handling / Rollback
```

For each step, identify:
- **Action**: What happens (command, API call, tool invocation)
- **Input**: What this step needs from the previous step
- **Output**: What this step produces for the next step
- **Failure mode**: What happens when this step fails
- **Rollback**: How to undo this step (if applicable)

### Step 3: Assess Risk Level

| Level | Criteria | Guardrails Required |
|-------|----------|---------------------|
| Read-only | Only fetches/analyzes data | None |
| Write | Creates PRs, posts messages, writes files | Confirmation before external side effects |
| Destructive | Deletes resources, force-pushes, drops tables | PreToolUse hook blocks + explicit confirmation + dry-run mode |

### Step 4: Planning Checkpoint

Display the workflow diagram, tool inventory, and risk assessment. Ask user to approve before generating.

## Generation Pipeline

After user approval, generate in this order:

### 1. Generate SKILL.md

Use the anatomy template with composition-specific sections:
- Workflow overview diagram (ASCII art or numbered steps)
- Tool requirements (what must be installed/configured)
- Risk level and guardrails in effect
- Quick reference of available workflow steps

### 2. Generate scripts/

For each workflow step, generate a script:

```bash
#!/usr/bin/env bash
# {step-name}.sh — {description}
# Part of: {skill-name}

set -euo pipefail

# --- Configuration ---
CONFIG_FILE="${CLAUDE_PLUGIN_DATA:-$(dirname "$0")/..}/config.json"

# --- Input validation ---
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <required-arg>" >&2
  exit 1
fi

# --- Main logic ---
{step implementation}

# --- Output ---
echo "Step completed: {description}"
```

Script requirements:
- `set -euo pipefail` in every script
- Input validation for required arguments
- Actionable error messages (tell user what to do, not just what failed)
- Exit codes: 0 = success, 1 = error, 2 = skipped (already done)

For verification skills, generate a `scripts/verify.sh` with assertions:

```bash
#!/usr/bin/env bash
# verify.sh — Assert expected state after workflow execution
set -euo pipefail

PASS=0
FAIL=0

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS: $label"
    ((PASS++))
  else
    echo "  FAIL: $label (expected: $expected, got: $actual)"
    ((FAIL++))
  fi
}

# --- Assertions ---
{generated assertions based on success criteria}

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
```

### 3. Generate hooks/ (if risk level is write or destructive)

For destructive operations, generate guardrail hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/guardrail.sh \"$TOOL_INPUT\"",
          "timeout": 5
        }]
      }
    ]
  }
}
```

Guardrail patterns:
- Block specific commands: `rm -rf`, `DROP TABLE`, `git push --force`
- Require dry-run first: check if `--dry-run` flag was used before allowing the real command
- Rate limit: prevent rapid successive executions

### 4. Generate config.json

```json
{
  "{field}": "",
  "_setup_instructions": {
    "{field}": "Description of what to enter and where to find it"
  }
}
```

### 5. Generate references/workflow.md

Detailed workflow documentation with:
- Step-by-step instructions with expected inputs/outputs
- Error handling for each step
- Rollback procedures
- Troubleshooting common failures

### 6. Generate metadata.json and gotchas.md

metadata.json with `discipline: "composition"` and the appropriate `type` field.
gotchas.md with "No known gotchas yet" — to be filled during use.

### 7. Validate

Run validate-skill.js + skill-reviewer with composition RUBRIC.md.

## Type-Specific Guidance

### Product Verification Skills

Focus on: assertions, recording, state checking.

- Include `scripts/verify.sh` with programmatic assertions
- Consider recording output (screenshots, logs) for human review
- Assert on STATE, not just output: "the database row exists" not "the command printed success"
- Structure assertions as: setup → action → wait → assert → cleanup

Example workflow:
```
1. Set up test data (seed user, create test card)
2. Drive the UI flow (playwright, tmux)
3. Wait for async operations to complete
4. Assert state (database, API, UI)
5. Clean up test data
```

### Workflow Automation Skills

Focus on: composition, logging, idempotency.

- Save results in log files for cross-run consistency
- Make workflows idempotent (running twice produces same result)
- Use structured output (JSON) between steps for composability
- Include a `--dry-run` flag that shows what would happen without executing

Example: standup-post skill
```
1. Fetch git log since last standup
2. Fetch ticket tracker updates
3. Merge and format
4. Post to Slack channel
5. Append to standups.log
```

### CI/CD & Deployment Skills

Focus on: multi-step pipelines with rollback.

- Every deploy step must have a rollback counterpart
- Include error-rate comparison (before/after deploy)
- Support gradual rollout (canary, blue-green)
- Auto-rollback on regression detection

Example: deploy-service skill
```
1. Build and test locally
2. Push to staging → smoke test
3. Deploy canary (10% traffic)
4. Compare error rates (5 min window)
5. If regression: auto-rollback
6. If stable: full rollout
```

### Infrastructure Ops Skills

Focus on: guardrails, dry-run, soak periods.

- MUST include dry-run mode for destructive operations
- MUST include confirmation prompts before irreversible actions
- Include soak period for cleanup operations (find orphans → wait → confirm → delete)
- Log every destructive action for audit trail

Example: orphan-cleanup skill
```
1. Scan for orphaned resources (dry-run mode)
2. Post findings to Slack for review
3. Wait for soak period (configurable, default 24h)
4. Request explicit confirmation
5. Execute cleanup with audit logging
6. Verify cleanup completed
```

## Composition vs Distillation: Key Differences

| Aspect | Distillation | Composition |
|--------|-------------|-------------|
| Core output | Reference docs (40+ rules) | Scripts + workflow instructions |
| Value lives in | Knowledge and code examples | Tool orchestration and error handling |
| Validation focus | Factual accuracy of claims | Scripts execute, error paths handled |
| Bootstrap depth | Full (complete on first generation) | Scaffold + seed (grows through use) |
| Growth pattern | Add rules as new patterns emerge | Add steps as workflows expand |

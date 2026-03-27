---
description: Run functional evals on a skill — test with real prompts, baseline comparison, human review, iterative improvement
argument-hint: <skill-path>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, WebSearch
---

# Functional Skill Evaluation

You are an expert at measuring skill quality through empirical testing. You run structured eval loops: draft prompts, execute with and without the skill, grade results, show the human, incorporate feedback, and iterate. Comparison against a no-skill baseline is the core method — without it you cannot distinguish "the skill helped" from "the model would have done this anyway."

**IMPORTANT**: This command requires the Opus model for accurate evaluation. Always use `model: opus` when invoking agents.

## Input Required

You will receive a **path to an existing skill** (e.g., `~/.claude/skills/react-best-practices` or `.claude/skills/acme-deploy-workflow`).

---

## Step 0: Validate Skill and Detect Discipline

### 0a: Verify Skill Exists

Read the skill directory and verify `SKILL.md` exists. If absent, tell the user and stop.

Read `metadata.json` for version, technology, discipline, and type fields.

Store the skill path as `{skill-path}` and the skill's parent directory as `{skill-parent}` for all subsequent operations.

### 0b: Detect Discipline

Read `{skill-path}/metadata.json` and extract the `discipline` field.

If `metadata.json` has no `discipline` field, infer from directory structure:

| Signal | Discipline |
|--------|-----------|
| Has `references/` with rule files containing frontmatter with `impact` field | distillation |
| Has `scripts/` directory with executable files | composition |
| Has `*-tree.md` files or `references/queries/` directory | investigation |
| Has `assets/templates/*.template` files | extraction |
| None of the above | distillation (backwards compatible) |

Check signals in order. Use the first match.

### 0c: Load Eval Guide

Read the discipline-specific eval patterns:

```
${CLAUDE_PLUGIN_ROOT}/templates/anatomy/EVAL_GUIDE.md
```

You will reference this guide when drafting prompts, assertions, and trigger queries. Keep the content in working memory throughout the eval loop.

### 0d: Create Workspace

Create the workspace directory as a **sibling** to the skill directory:

```
{skill-parent}/{skill-name}-workspace/
```

The workspace must never be inside the skill directory itself.

### 0e: Determine Iteration Number

Check for existing `iteration-N` directories inside the workspace:

```bash
ls -d {workspace}/iteration-* 2>/dev/null | sort -V | tail -1
```

If none exist, this is iteration 1. Otherwise increment the highest found number.

---

## Step 1: Draft or Load Test Prompts

### If `{workspace}/evals/evals.json` exists:

1. Read and parse the existing evals file
2. Display the eval prompts in a summary table:

```markdown
## Existing Eval Prompts

| # | Name | Prompt (truncated) | Assertions |
|---|------|--------------------|------------|
| 1 | {name} | {first 80 chars}... | {count} |
| 2 | {name} | {first 80 chars}... | {count} |
```

3. Ask via AskUserQuestion:

```
Question: "Found existing eval prompts. How do you want to proceed?"
Header: "Eval Prompts"
Options:
- "Use existing evals as-is"
- "Modify or add to existing evals"
- "Start fresh with new evals"
```

If "Use existing evals as-is", skip to Step 2. If "Modify" or "Start fresh", continue below.

### If no evals exist (or user chose to start fresh):

1. Re-read the EVAL_GUIDE.md discipline-specific section for the detected discipline
2. Read the skill's SKILL.md thoroughly to understand what the skill teaches/automates
3. Draft 2-3 test prompts that:
   - Use realistic, user-like phrasing (not robotic test language)
   - Represent the range of tasks the skill should handle
   - Include enough context that an agent could attempt the task
   - For skills that operate on files, describe or create minimal input files

4. For each prompt, describe the expected output in plain language — what a good result looks like

5. Display the drafted prompts as regular markdown (NOT inside AskUserQuestion):

```markdown
## Drafted Eval Prompts

### Eval 1: {descriptive-name}
**Prompt:** {the full prompt text}
**Expected output:** {description of what good looks like}

### Eval 2: {descriptive-name}
**Prompt:** {the full prompt text}
**Expected output:** {description of what good looks like}

### Eval 3: {descriptive-name}
**Prompt:** {the full prompt text}
**Expected output:** {description of what good looks like}
```

6. Then ask via AskUserQuestion:

```
Question: "Do these test cases look right, or do you want to modify/add more?"
Header: "Test Cases"
Options:
- "These look good — proceed"
- "I want to modify some prompts"
- "Add more test cases"
- "Start over with different prompts"
```

7. Once approved, save to `{workspace}/evals/evals.json`:

```json
{
  "evals": [
    {
      "id": "eval-1",
      "name": "descriptive-name",
      "prompt": "the full prompt text",
      "expected_output": "description of what good looks like",
      "input_files": [],
      "assertions": []
    }
  ]
}
```

Do not write assertions yet. Prompts and expected_output only. Assertions come in Step 3.

---

## Step 2: Spawn All Runs in the Same Turn

**CRITICAL**: Launch ALL with-skill AND without-skill (baseline) runs in a SINGLE message with multiple Task tool calls. This is non-negotiable — sequential spawning wastes time and introduces ordering bias.

For N evals, you will spawn 2N tasks in one turn.

### Create iteration directory

```bash
mkdir -p {workspace}/iteration-{N}
```

### For each eval, spawn two tasks:

#### With-skill run (Task tool):

```
Execute this task:
- Skill path: {skill-path}
- Read the skill's SKILL.md and follow its guidance while completing the task.
- Task: {eval prompt}
- Input files: {eval input_files if any, or "none"}
- Save ALL output files to: {workspace}/iteration-{N}/eval-{ID}-{name}/with_skill/run-1/outputs/
- Save a transcript of your execution to: {workspace}/iteration-{N}/eval-{ID}-{name}/with_skill/run-1/transcript.md

The transcript must include:
1. What you understood the task to be
2. Each major step you took and why
3. What tools you used
4. Any issues encountered and how you resolved them
5. What you produced as output

Outputs to save depend on the task. At minimum, save the primary deliverable files and a brief summary.
```

#### Baseline run — same prompt, no skill (Task tool):

```
Execute this task:
- Task: {eval prompt}
- Input files: {eval input_files if any, or "none"}
- Save ALL output files to: {workspace}/iteration-{N}/eval-{ID}-{name}/without_skill/run-1/outputs/
- Save a transcript of your execution to: {workspace}/iteration-{N}/eval-{ID}-{name}/without_skill/run-1/transcript.md

The transcript must include:
1. What you understood the task to be
2. Each major step you took and why
3. What tools you used
4. Any issues encountered and how you resolved them
5. What you produced as output

Do NOT read any skill files. Complete the task using only your default knowledge and the tools available to you.
```

### Write eval metadata

For each eval, write `{workspace}/iteration-{N}/eval-{ID}-{name}/eval_metadata.json`:

```json
{
  "id": "eval-1",
  "name": "descriptive-name",
  "prompt": "the full prompt text",
  "expected_output": "description of what good looks like",
  "assertions": [],
  "configs": ["with_skill", "without_skill"]
}
```

### Capture timing data

When each subagent task completes, a task notification arrives with `total_tokens` and `duration_ms`. Capture these immediately and save to `timing.json` in the run directory:

```json
{
  "total_tokens": 45230,
  "duration_ms": 182500,
  "duration_seconds": 182.5
}
```

Write to: `{workspace}/iteration-{N}/eval-{ID}-{name}/{config}/run-1/timing.json`

This is the ONLY opportunity to capture timing data. It is not persisted elsewhere. If you miss the notification, the timing data is lost.

---

## Step 3: While Runs Are In Progress, Draft Assertions

Do not wait for runs to complete. Use the time productively by drafting assertions.

### 3a: Read discipline-specific assertion patterns

Re-read the EVAL_GUIDE.md section on assertion patterns for the detected discipline.

### 3b: Draft quantitative assertions

For each eval, draft 3-6 assertions that are:

- **Objectively verifiable** — no subjective quality judgments. "Output contains a function named X" not "Output is well-structured."
- **Discriminating** — would fail for a bad output, not just trivially pass for anything. "JSON has field `total` with a numeric value" not "Output is not empty."
- **Named descriptively** — these names show up in the benchmark viewer. Use names that tell the user what was tested at a glance.

Good assertion examples by discipline:

**Distillation**: "Generated code uses Promise.all for independent fetches", "No nested await inside loop body"
**Composition**: "Deploy script exited with code 0", "Rollback was triggered after health check failure"
**Investigation**: "Root cause section identifies the memory leak", "Recommended fix references the specific config file"
**Extraction**: "Generated component file follows PascalCase naming", "Template parameters were all substituted (no {placeholder} remains)"

### 3c: Prefer scripted assertions

For assertions that can be checked programmatically (file exists, string contains X, JSON has field Y, line count within range), write a check script rather than relying on the grader's reading comprehension. Scripts are faster, more reliable, and reusable across iterations.

Save check scripts to `{workspace}/evals/checks/`:

```bash
#!/bin/bash
# check_eval1_has_function.sh
# Returns 0 (pass) or 1 (fail), prints evidence to stdout
OUTPUT_DIR="$1"
if grep -q "function processOrder" "$OUTPUT_DIR"/*.ts 2>/dev/null; then
  echo "PASS: Found 'function processOrder' in output"
  exit 0
else
  echo "FAIL: 'function processOrder' not found in any .ts file"
  exit 1
fi
```

### 3d: Present assertions to the user

Display as regular markdown:

```markdown
## Drafted Assertions

### Eval 1: {name}
1. {assertion text}
2. {assertion text}
3. {assertion text}

### Eval 2: {name}
1. {assertion text}
2. {assertion text}
3. {assertion text}
```

Then explain the reasoning: why these assertions are discriminating, what they would catch, and what they would miss.

### 3e: Update metadata

After presenting (no need to ask for approval — assertions can be refined after seeing results):

1. Update each `eval_metadata.json` with the assertions array
2. Update `{workspace}/evals/evals.json` with the assertions

```json
{
  "assertions": [
    "Generated code uses Promise.all for independent fetches",
    "No nested await inside loop body",
    "Output includes error handling for network failures"
  ]
}
```

---

## Step 4: Grade, Aggregate, and Launch Viewer

Wait for ALL subagent tasks from Step 2 to complete before proceeding. Verify that every run directory has both `transcript.md` and files in `outputs/`.

### 4a: Grade each run

For each eval and each config (with_skill, without_skill), spawn a grader subagent:

```
subagent_type: "dev-skill:grader"

Grade this eval run:

- Expectations: {assertions list from eval_metadata.json}
- Transcript: {workspace}/iteration-{N}/eval-{ID}-{name}/{config}/transcript.md
- Outputs dir: {workspace}/iteration-{N}/eval-{ID}-{name}/{config}/outputs/
- Save grading to: {workspace}/iteration-{N}/eval-{ID}-{name}/{config}/../grading_{config}.json

The skill's discipline is {discipline}. Adapt evidence gathering accordingly.

IMPORTANT: The grading.json expectations array MUST use these exact field names:
- text: the assertion text
- passed: boolean
- evidence: specific evidence supporting the verdict

The viewer depends on these exact field names. Do not rename them.
```

Spawn all grader tasks in a single turn — they are independent of each other.

If scripted checks exist in `{workspace}/evals/checks/`, run them first and pass the results to the grader as additional context:

```bash
for script in {workspace}/evals/checks/check_eval{ID}_*.sh; do
  bash "$script" "{workspace}/iteration-{N}/eval-{ID}-{name}/{config}/outputs/"
done
```

### 4b: Aggregate into benchmark

Once all grading is complete, aggregate results:

```bash
python3 -m scripts.eval.aggregate_benchmark \
  {workspace}/iteration-{N} \
  --skill-name {skill-name}
```

This produces `{workspace}/iteration-{N}/benchmark.json` with per-eval and per-config summaries.

### 4c: Analyst pass

Read `{workspace}/iteration-{N}/benchmark.json` and surface patterns that aggregate stats hide. Reference the "Analyzing Benchmark Results" section in `${CLAUDE_PLUGIN_ROOT}/agents/analyzer.md`:

Patterns to surface:

- **Non-discriminating assertions**: Assertions that always pass in BOTH with_skill and without_skill configs. These do not prove the skill adds value. Flag them for replacement.
- **High-variance evals**: Evals where pass rates swing wildly across configs or across runs within the same config. These may be flaky or non-deterministic.
- **Time/token tradeoffs**: If the skill significantly increases execution time or token usage, note the cost-benefit ratio. A skill that doubles token usage for a 5% improvement may not be worth it.
- **Skill-hurting patterns**: Assertions that consistently pass WITHOUT skill but fail WITH skill. The skill may be introducing confusion or unnecessary constraints.
- **Clean wins**: Assertions that consistently fail without skill but pass with skill. These are the skill's strongest value propositions.

Write analysis notes to `{workspace}/iteration-{N}/analysis_notes.json` as a JSON array of strings.

### 4d: Launch the viewer

```bash
nohup python3 ${CLAUDE_PLUGIN_ROOT}/eval-viewer/generate_review.py \
  {workspace}/iteration-{N} \
  --skill-name "{skill-name}" \
  --benchmark {workspace}/iteration-{N}/benchmark.json \
  > /dev/null 2>&1 &
VIEWER_PID=$!
echo "Viewer PID: $VIEWER_PID"
```

For iteration 2 and above, add the previous iteration for diff comparison:

```bash
nohup python3 ${CLAUDE_PLUGIN_ROOT}/eval-viewer/generate_review.py \
  {workspace}/iteration-{N} \
  --skill-name "{skill-name}" \
  --benchmark {workspace}/iteration-{N}/benchmark.json \
  --previous-workspace {workspace}/iteration-{N-1} \
  > /dev/null 2>&1 &
VIEWER_PID=$!
```

For headless or cowork environments where a browser cannot be opened, generate a static file instead:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/eval-viewer/generate_review.py \
  {workspace}/iteration-{N} \
  --skill-name "{skill-name}" \
  --benchmark {workspace}/iteration-{N}/benchmark.json \
  --static {workspace}/iteration-{N}/review.html
```

### 4e: Present results to the user

Display a summary of the benchmark as regular markdown:

```markdown
## Eval Results — Iteration {N}

### Benchmark Summary

| Eval | With Skill | Without Skill | Delta |
|------|-----------|---------------|-------|
| {name} | {pass_rate}% | {pass_rate}% | {+/-}% |
| {name} | {pass_rate}% | {pass_rate}% | {+/-}% |

### Analysis Notes
- {note 1}
- {note 2}
- {note 3}
```

Then tell the user:

"I've opened the results in your browser. The 'Outputs' tab lets you click through each test case and see actual outputs side-by-side. The 'Benchmark' tab shows the quantitative comparison. Leave feedback on any outputs that need improvement — when you're done reviewing, come back and let me know."

---

## Step 5: Read Feedback and Improve

When the user says they are done reviewing:

### 5a: Read feedback

```bash
cat {workspace}/iteration-{N}/feedback.json 2>/dev/null || echo "No feedback file found"
```

### 5b: Kill the viewer

```bash
kill $VIEWER_PID 2>/dev/null
```

### 5c: Analyze feedback

Parse `feedback.json`. The structure is an array of entries, each with an eval ID and freeform text:

- **Empty feedback** (all entries have empty or null text) = the user looked at the outputs and found them acceptable.
- **Specific feedback** = the user identified concrete problems that need fixing.

### 5d: Determine next action

**If all feedback is empty AND benchmark looks good** (skill configs consistently outperform baseline):
- The skill passes functional evals. Move to Step 6.

**If feedback contains specific complaints:**

1. Read the transcripts for the flagged evals to understand what went wrong
2. Read the skill's SKILL.md and relevant referenced files
3. Apply improvements following these principles (from Anthropic's guidance on skill iteration):

**Generalize from feedback.** Do not overfit to specific test cases. If the skill will be used thousands of times on varied inputs, fiddly fixes for one case are useless. Ask: "What general principle would fix this AND prevent similar failures on unseen inputs?"

**Keep the skill lean.** Read transcripts to spot unproductive agent behavior caused by the skill. If the agent is spending tokens on busywork the skill demands (e.g., writing verbose logs nobody reads, running unnecessary validation steps), remove or simplify those instructions. Every line in a skill should earn its place.

**Explain the why.** If you find yourself writing ALWAYS/NEVER in uppercase, stop. Reframe as reasoning the model can generalize from. "Always validate JSON before writing" is less useful than "Invalid JSON will cause the downstream parser to crash silently, producing empty output instead of an error — validate before writing to catch issues early."

**Bundle repeated work.** If every test case's subagent independently wrote similar helper scripts (a common sign), bundle that script into the skill's `scripts/` directory. If every run duplicated the same setup steps, add a setup section to the skill.

4. Apply improvements to SKILL.md and any referenced files
5. Explain what you changed and why as regular markdown
6. Rerun ALL test cases into `iteration-{N+1}/`
7. Go back to Step 4 (grade, aggregate, view, feedback)

### 5e: Iteration cap

Keep iterating until one of these conditions is met:
- User explicitly says they are happy with the results
- All feedback is empty and benchmark shows clear skill advantage
- Three consecutive iterations show no meaningful progress on the flagged issues (diminishing returns)

When the loop terminates, report the final state:

```markdown
## Eval Loop Complete

**Iterations:** {N}
**Final pass rate (with skill):** {rate}%
**Final pass rate (without skill):** {rate}%
**Net skill advantage:** {delta}%
```

---

## Step 6: Optional — Description Optimization

After functional evals pass, offer description optimization as a separate phase.

Display as regular markdown:

```markdown
## Description Optimization

The skill passes functional evals. The next step is to optimize its description for triggering accuracy — making sure Claude correctly invokes the skill when relevant queries arrive, and does NOT invoke it for unrelated queries.

This tests the skill's discoverability, not its content quality.
```

Then ask via AskUserQuestion:

```
Question: "Want to optimize the skill's description for triggering accuracy?"
Header: "Description Optimization"
Options:
- "Yes, optimize the description"
- "No, the description is fine — skip to validation"
```

### If "No": Skip to Step 7.

### If "Yes":

#### 6a: Generate trigger eval queries

Following the EVAL_GUIDE.md trigger guidance, generate 20 trigger eval queries:

**10 should-trigger queries:**
- Varied phrasings from casual to formal
- Implicit intent (user describes the problem, not the solution)
- Different levels of specificity
- Include domain jargon and also plain language
- Mix short queries ("fix my react perf") with detailed ones ("I have a React app that re-renders 200 times on page load, how do I profile and fix this?")

**10 should-not-trigger queries:**
- Near-misses: share keywords but have fundamentally different intent
- Adjacent domains: similar technology but different problem space
- Superficially similar: use the same verbs but for different tasks
- Tricky negatives that a loose keyword match would incorrectly trigger on

Make every query realistic — include context, detail, and varying style. Avoid sterile test language.

#### 6b: Present queries for review

Read the HTML template:

```bash
cat ${CLAUDE_PLUGIN_ROOT}/assets/eval_review.html
```

Build the eval data JSON:

```json
[
  {
    "id": 1,
    "query": "the trigger query text",
    "expected": true,
    "rationale": "why this should/shouldn't trigger"
  }
]
```

Replace placeholders in the HTML:
- `__EVAL_DATA_PLACEHOLDER__` with the JSON array
- `__SKILL_NAME_PLACEHOLDER__` with the skill name
- `__SKILL_DESCRIPTION_PLACEHOLDER__` with the current description from SKILL.md frontmatter

Write to a temp file and open:

```bash
EVAL_HTML="/tmp/eval_review_${skill_name}.html"
# ... write the HTML with substituted placeholders ...
open "$EVAL_HTML"
```

Tell the user: "I've opened the trigger eval review in your browser. Review the queries — mark any that are wrong, add new ones if needed — then export the eval set. The export will save to ~/Downloads/eval_set.json."

#### 6c: Load exported eval set

When the user confirms they have exported:

```bash
cat ~/Downloads/eval_set.json
```

Parse the exported eval set. If the file does not exist, ask the user where they saved it.

#### 6d: Run the description optimization loop

```bash
python3 -m scripts.eval.run_loop \
  --eval-set {eval-set-path} \
  --skill-path {skill-path} \
  --model {current-model-id} \
  --max-iterations 5 \
  --verbose
```

Run this in the background and periodically check progress:

```bash
# Check if still running
ps -p $OPT_PID > /dev/null 2>&1 && echo "Still running..." || echo "Completed"
```

When complete, read the output and report:

```markdown
## Description Optimization Results

**Iterations:** {N}
**Best accuracy:** {score}%

### Before
```
{original description}
```

### After
```
{optimized description}
```

### Score progression
| Iteration | Accuracy | Change |
|-----------|----------|--------|
| 0 (original) | {score}% | — |
| 1 | {score}% | {+/-}% |
| ... | ... | ... |
```

#### 6e: Apply the optimized description

Read `best_description` from the optimization output and update the SKILL.md frontmatter `description` field.

Show the before/after to the user. If the new description is significantly different in meaning (not just phrasing), ask for confirmation before applying.

---

## Step 7: Final Structural Validation

Run structural validation as the final gate to catch any issues introduced during the eval/improvement loop:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-path}
```

### If validation passes (zero errors):

```markdown
## Validation: PASS

Skill is structurally sound and passes functional evals.

**Skill:** {skill-name}
**Discipline:** {discipline}
**Functional eval pass rate:** {rate}%
**Skill advantage over baseline:** {delta}%
**Structural errors:** 0

Skill is ready to ship.
```

### If validation finds errors:

Report each error with its file path and description. Fix blocking errors (severity: ERROR) automatically, then re-run validation. For warnings, report them but do not block.

If fixes were applied:

```markdown
## Validation: PASS (after fixes)

Fixed {N} structural issues introduced during the eval loop:
{list of fixes}

Skill is ready to ship.
```

---

## Mandatory Requirements

**NEVER:**
- Skip the baseline (without_skill) runs — comparison against a no-skill baseline is the entire point. Without it you cannot distinguish "the skill helped" from "the model would have done this anyway."
- Spawn with-skill and baseline runs in separate turns — launch ALL tasks in one message. Sequential spawning wastes time and introduces ordering bias.
- Write assertions before the user approves the eval prompts — prompts first, assertions second.
- Apply skill improvements without running another iteration to verify they helped — every change must be validated empirically.
- Skip the viewer — the human MUST see actual outputs before you iterate. Aggregate metrics lie; outputs don't.
- Grade your own work — always use the grader subagent for objective evaluation.
- Overfit improvements to specific test cases — generalize from feedback.

**ALWAYS:**
- Read EVAL_GUIDE.md before drafting eval prompts — it contains discipline-specific patterns.
- Capture `timing.json` when task notifications arrive — this data is not persisted elsewhere and is lost if you miss it.
- Use descriptive names for eval directories (e.g., `eval-1-form-submission`, not `eval-0` or `test-a`).
- Use `text`, `passed`, `evidence` field names in grading.json — the viewer depends on these exact names.
- Save the workspace as a sibling to the skill directory, never inside it.
- Spawn all runs for a given iteration in a single turn with multiple Task calls.
- Run scripted assertions before grader subagents when check scripts exist — feed script results to the grader as additional evidence.
- Kill the viewer process before starting a new iteration.
- Present benchmark summaries as markdown before directing the user to the viewer — give them context for what they are about to see.
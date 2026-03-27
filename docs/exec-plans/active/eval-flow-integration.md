# Eval Flow Integration

> **Execution:** Use `/dev-workflow:execute-plan docs/exec-plans/active/eval-flow-integration.md` to implement milestone-by-milestone.

## Purpose / Big Picture

After this change, users can run `/dev-skill:eval <skill-path>` to functionally test any skill — regardless of discipline — before shipping it. The command spawns subagents to run the skill on real prompts alongside a baseline (no skill), grades results with assertions, shows the human actual outputs in a browser-based viewer, collects feedback, and iterates. Once functional evals pass, the user can optimize the skill's description for triggering accuracy. This closes the gap between "structurally valid" and "demonstrably works."

## Progress

- [x] (2026-03-27 23:30Z) Milestone 1: Adopt Anthropic's Python eval scripts into `scripts/eval/`
- [x] (2026-03-27 23:35Z) Milestone 2: Adopt and adapt eval agents (grader, comparator, analyzer)
- [x] (2026-03-27 23:35Z) Milestone 3: Adopt eval-viewer assets
- [x] (2026-03-27 23:45Z) Milestone 4: Write discipline-aware eval guide (`templates/anatomy/EVAL_GUIDE.md`)
- [x] (2026-03-27 23:45Z) Milestone 5: Write `/dev-skill:eval` command
- [x] (2026-03-27 23:50Z) Milestone 6: Integrate eval into `/dev-skill:new` and `/dev-skill:evolve`
- [x] (2026-03-27 23:55Z) Milestone 7: Update hooks, plugin.json, validate dependencies

## Surprises & Discoveries

(none yet)

## Decision Log

- **2026-03-27**: One command (`/dev-skill:eval`) instead of separate eval + optimize-trigger commands. Description optimization folds in as a final step after functional evals pass.
- **2026-03-27**: Adopt Anthropic's Python scripts wholesale instead of rewriting in Node.js. They use `claude -p` + Anthropic SDK — no reason to reimplement.
- **2026-03-27**: Eval is optional, not gated. `/dev-skill:new` suggests it after generation but doesn't require it.
- **2026-03-27**: Blind comparison (comparator + analyzer) is used by `/dev-skill:evolve` for old-vs-new, not by `/dev-skill:eval` for initial testing.

## Outcomes & Retrospective

(fill when complete)

---

## Context and Orientation

### What exists today

The `dev-skill` plugin at `plugins/dev-skill/` has:
- **Commands:** `new.md` (discipline-aware generation), `evolve.md` (improvement), `validate.md` (structural+substance checks), `migrate.md`, `shrink.md`
- **Agents:** `skill-reviewer.md` (rubric-aware quality review), `preflight-validator.md` (plan validation)
- **Scripts:** `scripts/validate-skill.js` (Node.js, ~40 structural checks), `scripts/build-agents-md.js`, `scripts/validation/` subdir, `scripts/setup.sh`, `scripts/check-dependencies.sh`
- **Templates:** `templates/anatomy/` (universal), `templates/disciplines/{distillation,composition,investigation,extraction}/` (per-discipline RECIPE.md, RUBRIC.md, templates)
- **Hooks:** `hooks/session-start.sh` (dependency check + command listing)
- **Dependencies:** Node.js 18+ (for validate-skill.js), npm packages (unified, remark, yaml)

### Anthropic source (being adopted from)

Cloned to `/tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/`. Key files:

| Source file | Purpose | Adopt strategy |
|---|---|---|
| `scripts/run_eval.py` | Tests description triggering via `claude -p` | Copy, minimal adaptation |
| `scripts/improve_description.py` | Claude + extended thinking to improve descriptions | Copy directly |
| `scripts/run_loop.py` | Eval+improve loop with train/test split | Copy directly |
| `scripts/aggregate_benchmark.py` | Statistical aggregation of run results | Copy directly |
| `scripts/generate_report.py` | HTML report generation | Copy directly |
| `scripts/quick_validate.py` | Basic frontmatter validation | Skip (we have validate-skill.js) |
| `scripts/package_skill.py` | .skill file packaging | Copy directly |
| `scripts/utils.py` | Shared utilities (parse_skill_md) | Copy directly |
| `scripts/__init__.py` | Python package marker | Copy directly |
| `agents/grader.md` | Evaluates assertions against outputs | Copy, add discipline awareness |
| `agents/comparator.md` | Blind A/B comparison | Copy directly |
| `agents/analyzer.md` | Post-hoc analysis + benchmark analysis | Copy directly |
| `eval-viewer/generate_review.py` | Browser-based eval viewer | Copy directly |
| `eval-viewer/viewer.html` | Viewer HTML template | Copy directly |
| `assets/eval_review.html` | Description optimization review template | Copy directly |
| `references/schemas.md` | JSON schemas for all data structures | Copy, extend for disciplines |

### Terms

| Term | Meaning |
|------|---------|
| **Eval** | A test case: a prompt + expected output + assertions, run against the skill |
| **Assertion / Expectation** | A verifiable statement about what the output should contain or achieve |
| **Baseline** | The control run — same prompt but without the skill (or with the old version) |
| **Grading** | Evaluating each assertion as PASS/FAIL with evidence |
| **Benchmark** | Aggregated statistics (pass rate, time, tokens) across multiple runs |
| **Trigger eval** | Testing whether a skill's description causes it to be invoked for relevant queries |
| **Train/test split** | Dividing trigger eval queries into training (optimize against) and test (measure against) to prevent overfitting |
| **Viewer** | Browser-based HTML tool where the human reviews actual outputs and leaves feedback |
| **Workspace** | Directory structure organizing eval results by iteration |

### Workspace structure (what gets created when eval runs)

```
{skill-name}-workspace/          # Sibling to the skill directory
├── evals/
│   └── evals.json               # Test prompts + assertions
├── iteration-1/
│   ├── eval-0-{descriptive-name}/
│   │   ├── with_skill/
│   │   │   ├── outputs/         # Files the skill produced
│   │   │   ├── transcript.md    # Execution log
│   │   │   └── timing.json      # Tokens + duration
│   │   ├── without_skill/       # Baseline (same prompt, no skill)
│   │   │   ├── outputs/
│   │   │   ├── transcript.md
│   │   │   └── timing.json
│   │   ├── eval_metadata.json   # Prompt + assertions for this eval
│   │   └── grading.json         # Grader output
│   ├── benchmark.json           # Aggregated stats
│   ├── benchmark.md             # Human-readable summary
│   └── feedback.json            # Human feedback from viewer
├── iteration-2/
│   └── ...
└── trigger-optimization/        # Description optimization (optional)
    ├── eval_set.json            # Trigger eval queries
    └── results/                 # run_loop.py output
```

---

## Plan of Work

### Milestone 1: Adopt Anthropic's Python eval scripts

**Goal:** Copy the Python eval infrastructure into `plugins/dev-skill/scripts/eval/` as a self-contained Python package. Verify scripts load and `--help` works.

**Work:**

1. Create `plugins/dev-skill/scripts/eval/` directory
2. Copy these files from `/tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/`:
   - `scripts/__init__.py` → `scripts/eval/__init__.py`
   - `scripts/utils.py` → `scripts/eval/utils.py`
   - `scripts/run_eval.py` → `scripts/eval/run_eval.py`
   - `scripts/improve_description.py` → `scripts/eval/improve_description.py`
   - `scripts/run_loop.py` → `scripts/eval/run_loop.py`
   - `scripts/aggregate_benchmark.py` → `scripts/eval/aggregate_benchmark.py`
   - `scripts/generate_report.py` → `scripts/eval/generate_report.py`
   - `scripts/package_skill.py` → `scripts/eval/package_skill.py`

3. Fix internal imports: the scripts use `from scripts.utils import ...` and `from scripts.run_eval import ...`. Update to `from scripts.eval.utils import ...` etc., OR add a compatibility `__init__.py` that re-exports. Simplest: update the imports.

4. Verify each script loads:
   ```bash
   cd plugins/dev-skill
   python -c "from scripts.eval.utils import parse_skill_md; print('OK')"
   python -m scripts.eval.run_eval --help
   python -m scripts.eval.run_loop --help
   python -m scripts.eval.aggregate_benchmark --help
   ```

5. Add Python dependencies note: `anthropic` package required for `improve_description.py` and `run_loop.py`. The `claude` CLI required for `run_eval.py`. Add to `scripts/eval/README.md`.

**Result:** All eval Python scripts are importable and runnable from `plugins/dev-skill/`.

**Proof:** `python -m scripts.eval.run_eval --help` prints usage without errors.

---

### Milestone 2: Adopt and adapt eval agents

**Goal:** Add grader, comparator, and analyzer agents. Adapt the grader to reference discipline rubrics.

**Work:**

1. Copy `agents/comparator.md` directly from Anthropic source (no changes needed — it's discipline-agnostic by design; blind comparison works on any output type).

2. Copy `agents/analyzer.md` directly (the benchmark analysis section is universal; the post-hoc comparison section works on any skill type).

3. Copy `agents/grader.md` and adapt:
   - Keep the core grading process (Steps 1-8) identical
   - Add a preamble section about discipline awareness:
     ```
     ## Discipline-Aware Grading

     Before grading, read the skill's metadata.json to determine its discipline.
     Adjust your evidence gathering based on the discipline:

     - **Distillation**: Check if generated code follows the skill's rules.
       Look for patterns the rules recommend and anti-patterns they prohibit.
     - **Composition**: Check if scripts executed successfully.
       Verify workflow steps completed. Check error handling was invoked if errors occurred.
     - **Investigation**: Check if the diagnostic path was followed.
       Verify the correct decision tree branches were taken. Check report completeness.
     - **Extraction**: Check if generated files follow conventions.
       Verify templates were used. Check file naming and structure.
     ```
   - Keep all output format requirements exactly as Anthropic specifies (the viewer depends on `text`, `passed`, `evidence` field names)

**Result:** Three new agents in `plugins/dev-skill/agents/`. Grader is discipline-aware; comparator and analyzer are adopted directly.

**Proof:** `ls plugins/dev-skill/agents/` shows 5 agents: skill-reviewer, preflight-validator, grader, comparator, analyzer.

---

### Milestone 3: Adopt eval-viewer assets

**Goal:** Copy the eval-viewer and description review template into the plugin.

**Work:**

1. Create `plugins/dev-skill/eval-viewer/` directory
2. Copy from Anthropic source:
   - `eval-viewer/generate_review.py` → `plugins/dev-skill/eval-viewer/generate_review.py`
   - `eval-viewer/viewer.html` → `plugins/dev-skill/eval-viewer/viewer.html`
   - `assets/eval_review.html` → `plugins/dev-skill/assets/eval_review.html`

3. Verify the viewer works:
   ```bash
   python plugins/dev-skill/eval-viewer/generate_review.py --help
   ```

**Result:** Eval viewer is available at `${CLAUDE_PLUGIN_ROOT}/eval-viewer/generate_review.py`.

**Proof:** `python eval-viewer/generate_review.py --help` prints usage.

---

### Milestone 4: Write discipline-aware eval guide

**Goal:** Create `templates/anatomy/EVAL_GUIDE.md` — a reference that the `/dev-skill:eval` command reads to draft discipline-appropriate test prompts and assertions.

**Work:**

Write `templates/anatomy/EVAL_GUIDE.md` with:

1. **Universal eval principles** (from Anthropic's guidance):
   - Test prompts should be realistic, the kind of thing a user would actually say
   - Assertions must be objectively verifiable — don't force assertions on subjective outputs
   - Draft assertions while runs are in progress (don't waste time waiting)
   - Good assertions are discriminating — they pass when the skill genuinely works and fail when it doesn't
   - Empty feedback from the human means it looked fine

2. **Eval patterns per discipline:**

   **Distillation** (Library/API Reference, Code Quality):
   - Prompt pattern: "Write/refactor {code type} that {task requiring the skill's rules}"
   - Assertion pattern: "Uses {pattern from rule X}", "Does not use {anti-pattern from rule Y}", "Code compiles/lints without errors"
   - Baseline comparison: with-skill code should follow more rules than without-skill code
   - Example: `"Write a React component that fetches and displays a list of users"` → assert server component, parallel fetching, no barrel imports

   **Composition** (Verification, Automation, CI/CD, Infra Ops):
   - Prompt pattern: "Execute {the workflow this skill automates}"
   - Assertion pattern: "Ran script {X}", "Workflow completed all steps", "Error handling triggered on failure", "Guardrails blocked destructive operation"
   - Baseline comparison: with-skill should execute faster/more reliably than improvising without
   - Example: `"Deploy to staging and verify it's healthy"` → assert deploy script ran, verification passed, timing.json captured

   **Investigation** (Runbooks, Data Analysis):
   - Prompt pattern: "Diagnose: {symptom matching a decision tree}"
   - Assertion pattern: "Followed decision tree for {symptom}", "Used query from {queries/X.sql}", "Produced investigation report", "Reached a terminal action (fix/escalate/dismiss)"
   - Baseline comparison: with-skill should follow structured investigation vs ad-hoc without
   - Example: `"The /api/checkout endpoint is returning 500 errors"` → assert checked database, used slow-queries.sql, produced report

   **Extraction** (Scaffolding):
   - Prompt pattern: "Create/scaffold a new {component type} called {name}"
   - Assertion pattern: "Created file at {expected path}", "File uses {naming convention}", "Includes test file", "Follows template structure"
   - Baseline comparison: with-skill should produce convention-following code vs generic without
   - Example: `"Create a new API handler called OrderProcessor"` → assert kebab-case file, correct directory, test file present

3. **evals.json schema** (adopted from Anthropic's `references/schemas.md` with discipline field added):
   ```json
   {
     "skill_name": "example-skill",
     "discipline": "distillation",
     "evals": [
       {
         "id": 1,
         "name": "descriptive-name",
         "prompt": "User's task prompt",
         "expected_output": "Description of expected result",
         "files": [],
         "expectations": [
           "Verifiable assertion 1",
           "Verifiable assertion 2"
         ]
       }
     ]
   }
   ```

4. **How many evals to start with**: 2-3 per skill for initial testing. Expand to 5-8 once the skill is functional and you want to catch edge cases.

5. **Trigger eval guidance** (for description optimization):
   - Generate 20 queries: 10 should-trigger, 10 should-not-trigger
   - Should-trigger queries: different phrasings of the same intent, varying formality, including cases where the user doesn't name the skill type explicitly
   - Should-not-trigger queries: near-misses that share keywords but need something different
   - Make them realistic — include file paths, personal context, typos, casual speech
   - Bad: `"Format this data"`. Good: `"ok so my boss sent me this xlsx file called 'Q4 sales FINAL v2.xlsx' and she wants a profit margin column"`

**Result:** Comprehensive eval guide that the `/dev-skill:eval` command references for discipline-specific eval drafting.

**Proof:** File exists at `templates/anatomy/EVAL_GUIDE.md` with sections for all 4 disciplines.

---

### Milestone 5: Write `/dev-skill:eval` command

**Goal:** The main orchestration command. Runs the full eval loop: draft prompts → run with/without skill → grade → view → feedback → improve → repeat. Includes optional description optimization as a final step.

**Work:**

Write `commands/eval.md` with this structure:

**Frontmatter:**
```yaml
---
description: Run functional evals on a skill — test prompts, baseline comparison, human review, iterative improvement
argument-hint: <skill-path>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, WebSearch
---
```

**Command flow:**

**Step 0: Validate skill and detect discipline**
- Read SKILL.md, metadata.json
- Detect discipline (same inference as evolve.md/validate.md)
- Read `${CLAUDE_PLUGIN_ROOT}/templates/anatomy/EVAL_GUIDE.md`
- Create workspace: `{skill-parent}/{skill-name}-workspace/`

**Step 1: Draft or load test prompts**
- If `{workspace}/evals/evals.json` exists: load and display existing evals, ask to use/modify
- If not: draft 2-3 test prompts using EVAL_GUIDE.md's discipline-specific patterns
  - Display the drafted prompts and assertions
  - Ask user to approve, modify, or add more
  - Save to `{workspace}/evals/evals.json`
- Don't write assertions yet — just prompts and expected_output. Assertions are drafted in Step 3.

**Step 2: Spawn all runs (with-skill AND baseline) in the same turn**
- For each eval, spawn TWO subagents in a SINGLE message:
  - With-skill: execute the prompt with the skill loaded, save outputs
  - Without-skill (baseline): same prompt, no skill, save outputs
- Write `eval_metadata.json` for each eval
- Capture `timing.json` from task completion notifications

**Step 3: While runs are in progress, draft assertions**
- Don't wait — use this time to draft quantitative assertions
- Load discipline-specific assertion patterns from EVAL_GUIDE.md
- Explain assertions to user
- Update `eval_metadata.json` and `evals/evals.json`

**Step 4: Grade, aggregate, and launch viewer**
(Following Anthropic's exact flow)
1. Grade each run — spawn grader agent (reads `agents/grader.md`) for each eval
2. Aggregate — `python -m scripts.eval.aggregate_benchmark {workspace}/iteration-N --skill-name {name}`
3. Analyst pass — read benchmark data, surface patterns (reference `agents/analyzer.md`)
4. Launch viewer — `python ${CLAUDE_PLUGIN_ROOT}/eval-viewer/generate_review.py {workspace}/iteration-N --skill-name {name} --benchmark {workspace}/iteration-N/benchmark.json`
   - For headless: use `--static {output_path}`
   - For iteration 2+: add `--previous-workspace {workspace}/iteration-{N-1}`
5. Tell user to review in browser

**Step 5: Read feedback and improve**
- Wait for user to say they're done
- Read `{workspace}/iteration-N/feedback.json`
- Empty feedback = looks good. Focus on entries with specific complaints.
- Apply improvements following Anthropic's improvement philosophy:
  - Generalize from feedback, don't overfit
  - Keep the skill lean — remove what isn't pulling its weight
  - Explain the why — avoid heavy-handed MUSTs
  - Look for repeated work across test cases — bundle into scripts
- Rerun into `iteration-{N+1}/`
- Loop until: user is happy, all feedback empty, or no meaningful progress

**Step 6: Optional — Description optimization**
- After functional evals pass, ask: "Want to optimize the skill's description for triggering accuracy?"
- If yes:
  1. Generate 20 trigger eval queries (discipline-aware from EVAL_GUIDE.md)
  2. Present for user review using `${CLAUDE_PLUGIN_ROOT}/assets/eval_review.html`
  3. Run optimization: `python -m scripts.eval.run_loop --eval-set {queries} --skill-path {skill} --model {model} --max-iterations 5 --verbose`
  4. Apply best_description to SKILL.md frontmatter
  5. Show before/after and scores

**Step 7: Final structural validation**
- Run `node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-path}`
- Report any remaining structural issues

**Result:** Complete eval command covering functional testing, human review, iterative improvement, description optimization, and structural validation.

**Proof:** `commands/eval.md` exists and references all adopted scripts, agents, and viewer correctly.

---

### Milestone 6: Integrate eval into `/dev-skill:new` and `/dev-skill:evolve`

**Goal:** After generating a skill with `/new`, suggest eval. In `/evolve`, use blind comparison for old-vs-new.

**Work:**

1. **Update `commands/new.md`**: Add a final section after validation:
   ```markdown
   ## Step N: Suggest Eval

   After generation and structural validation, ask the user:

   "The skill is structurally valid. Want to test it on real prompts before shipping?"
   Options:
   - "Yes, run evals" → suggest: /dev-skill:eval {skill-path}
   - "No, ship as-is" → done
   ```

2. **Update `commands/evolve.md`**: Add blind comparison option in Step 6 (Apply Fixes):
   ```markdown
   ### Blind Comparison (optional)

   For significant changes, offer blind comparison between old and new versions:
   1. Snapshot old skill before changes: `cp -r {skill-path} {workspace}/skill-snapshot/`
   2. Apply changes to the skill
   3. Run 2-3 test prompts against both versions (subagents)
   4. Launch blind comparator agent (reads agents/comparator.md)
   5. Launch analyzer agent (reads agents/analyzer.md) to explain why winner won
   6. Report results to user with evidence

   This is more rigorous than rubric-based review — it compares actual outputs.
   ```

**Result:** `/new` suggests eval. `/evolve` can use blind comparison.

**Proof:** grep for "eval" in `commands/new.md` finds the suggestion step. grep for "comparator" in `commands/evolve.md` finds the blind comparison section.

---

### Milestone 7: Update hooks, plugin.json, validate dependencies

**Goal:** Update session-start hook to list `/dev-skill:eval`. Add Python dependency check. Update plugin description.

**Work:**

1. **Update `hooks/session-start.sh`**: Add `/dev-skill:eval` to command listing. Add Python + `anthropic` package check (warning, not blocking — eval is optional).

2. **Update `scripts/check-dependencies.sh`**: Add checks for `python3`, `anthropic` package, `claude` CLI. Mark as optional (needed for eval only).

3. **Update `scripts/setup.sh`**: Add `pip install anthropic` or note about Python dependencies.

4. **Update `.claude-plugin/plugin.json` description** (already mentions 9 types, just ensure eval is referenced).

5. **Add `plugins/dev-skill/scripts/eval/README.md`**: Document the adopted scripts, their origin (Anthropic's claude-plugins-official), dependencies, and usage.

**Result:** Plugin is fully updated with eval flow integrated.

**Proof:**
- `bash hooks/session-start.sh` mentions `/dev-skill:eval`
- `bash scripts/check-dependencies.sh` checks for python3 and anthropic
- `cat scripts/eval/README.md` explains the eval infrastructure

---

## Concrete Steps

### Milestone 1 commands:
```bash
# Create directory
mkdir -p plugins/dev-skill/scripts/eval

# Copy scripts (from the cloned repo)
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/__init__.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/utils.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/run_eval.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/improve_description.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/run_loop.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/aggregate_benchmark.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/generate_report.py plugins/dev-skill/scripts/eval/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/scripts/package_skill.py plugins/dev-skill/scripts/eval/

# Fix imports in each file
# Change: from scripts.X → from scripts.eval.X

# Verify
cd plugins/dev-skill
python -c "from scripts.eval.utils import parse_skill_md; print('OK')"
python -m scripts.eval.run_eval --help
```

### Milestone 3 commands:
```bash
mkdir -p plugins/dev-skill/eval-viewer
mkdir -p plugins/dev-skill/assets

cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/eval-viewer/generate_review.py plugins/dev-skill/eval-viewer/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/eval-viewer/viewer.html plugins/dev-skill/eval-viewer/
cp /tmp/claude-plugins-official/plugins/skill-creator/skills/skill-creator/assets/eval_review.html plugins/dev-skill/assets/

python plugins/dev-skill/eval-viewer/generate_review.py --help
```

### Milestone 7 commands:
```bash
# Verify after all changes
ls plugins/dev-skill/commands/
# Expected: eval.md evolve.md migrate.md new.md shrink.md validate.md

ls plugins/dev-skill/agents/
# Expected: analyzer.md comparator.md grader.md preflight-validator.md skill-reviewer.md

ls plugins/dev-skill/scripts/eval/
# Expected: __init__.py aggregate_benchmark.py generate_report.py improve_description.py package_skill.py run_eval.py run_loop.py utils.py README.md

ls plugins/dev-skill/eval-viewer/
# Expected: generate_review.py viewer.html
```

---

## Validation and Acceptance

1. **Scripts load:** `python -m scripts.eval.run_eval --help` exits 0
2. **Viewer loads:** `python eval-viewer/generate_review.py --help` exits 0
3. **Agents present:** `ls agents/` shows grader.md, comparator.md, analyzer.md
4. **Eval command present:** `ls commands/eval.md` exists
5. **Eval guide present:** `ls templates/anatomy/EVAL_GUIDE.md` exists
6. **New command suggests eval:** `grep -l "eval" commands/new.md` finds a match
7. **Evolve command has comparison:** `grep -l "comparator" commands/evolve.md` finds a match
8. **Hook updated:** `grep "eval" hooks/session-start.sh` finds a match
9. **No broken imports:** `python -c "from scripts.eval.run_eval import run_eval; print('OK')"` succeeds

## Idempotence and Recovery

- Milestones 1-4 are purely additive (new files). Rollback: delete the new files.
- Milestone 5 adds a command. Rollback: delete `commands/eval.md`.
- Milestone 6 edits existing commands. Rollback: `git checkout -- commands/new.md commands/evolve.md`.
- Milestone 7 edits hooks/setup. Rollback: `git checkout -- hooks/ scripts/check-dependencies.sh scripts/setup.sh`.

All adopted scripts have their own MIT license from Anthropic. The LICENSE.txt from the source repo should be preserved in `scripts/eval/`.

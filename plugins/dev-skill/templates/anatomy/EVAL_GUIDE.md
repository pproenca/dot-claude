# Eval Guide

Reference for drafting discipline-appropriate test prompts, assertions, and trigger evals. Read by the `/dev-skill:eval` command.

## Universal Eval Principles

These principles apply to every skill regardless of discipline.

**Test prompts must be realistic.** Write prompts the way a real user would. Include file paths, personal context, casual speech, varying lengths. Not: "Format this data." Yes: "ok so my boss sent me this xlsx file called 'Q4 sales FINAL v2.xlsx' and she wants a profit margin column added before the board meeting tomorrow."

**Assertions must be objectively verifiable.** Never write assertions about subjective quality. "Output reads well" is unverifiable. "Output contains a section titled 'Root Cause'" is verifiable. "Code uses async/await instead of callbacks" is verifiable.

**Good assertions are discriminating.** A discriminating assertion passes when the skill works and fails when it does not. An assertion that passes for both with-skill and without-skill configurations is non-discriminating and may be testing nothing useful. Design assertions that catch the specific behavior the skill adds.

**Draft assertions while runs are in progress.** Execution takes time. Use the wait to draft assertions based on what you expect to see. Revise after reading the transcript.

**Empty human feedback means it looked fine.** When the user reviews grading results and provides no feedback on an entry, treat it as approved. Focus attention on entries with specific complaints.

**Start small, expand when functional.** Begin with 2-3 evals. Expand to 5-8 once the skill passes basic evals and assertions are stable. More evals earlier just means more things to fix simultaneously.

**Generalize from feedback.** When the user corrects an assertion or prompt, ask whether the correction applies to other evals too. Do not overfit to one test case.

## Eval Patterns Per Discipline

### Distillation (Library/API Reference, Code Quality)

**Prompt pattern:** "Write/refactor {code type} that {task requiring the skill's rules}"

The prompt must require decisions the rules address. "Write hello world" will not test anything. "Refactor this Express middleware to handle async errors properly" forces the agent to apply error-handling rules.

**Assertion pattern:**
- "Uses {pattern from rule X}" — verify the correct pattern appears
- "Does not use {anti-pattern from rule Y}" — verify the anti-pattern is absent
- "Code compiles/lints without errors" — verify syntactic correctness

**Baseline comparison:** With-skill code should follow more rules than without-skill. The without-skill output is the agent's natural behavior; the with-skill output should show measurable improvement in rule adherence.

**Example eval 1:**
```json
{
  "id": 1,
  "name": "async-error-handling-middleware",
  "prompt": "I have this Express route that calls three different database queries and I keep getting unhandled promise rejections in production. Can you refactor it to handle errors properly? The file is at src/routes/orders.ts",
  "expected_output": "Refactored route with centralized async error handling following the skill's patterns",
  "files": ["src/routes/orders.ts"],
  "expectations": [
    "Uses asyncHandler wrapper or try/catch around all await calls",
    "Does not use .then().catch() chains (anti-pattern per rule async-03)",
    "Passes errors to next() rather than sending responses directly from catch blocks",
    "Code compiles with tsc --noEmit"
  ]
}
```

**Example eval 2:**
```json
{
  "id": 2,
  "name": "react-memo-optimization",
  "prompt": "this component re-renders like 50 times when I type in the search box, it's driving me nuts. here's the profiler screenshot and the component: src/components/ProductList.tsx",
  "expected_output": "Optimized component with memoization following the skill's performance rules",
  "files": ["src/components/ProductList.tsx"],
  "expectations": [
    "Wraps expensive child components with React.memo",
    "Uses useCallback for event handlers passed as props",
    "Does not wrap the entire component in memo without splitting (anti-pattern per rule perf-07)",
    "Search input state is isolated from list rendering"
  ]
}
```

**What makes a good distillation eval:** The prompt must force decisions the rules address. If the task can be completed correctly without ever consulting the rules, the eval is not testing the skill.

### Composition (Verification, Automation, CI/CD, Infra Ops)

**Prompt pattern:** "Execute {the workflow this skill automates}"

The prompt should trigger the workflow end-to-end, not just one step. A composition skill that automates deployment should be tested with "deploy this to staging," not "run the lint step."

**Assertion pattern:**
- "Ran script {X}" — verify the skill's bundled scripts were used
- "Workflow completed all steps" — verify no steps were skipped
- "Error handling triggered on failure" — verify recovery behavior
- "Guardrails blocked destructive operation" — verify safety mechanisms

**Baseline comparison:** With-skill should use bundled scripts and follow the defined workflow. Without-skill will improvise steps and likely miss safety checks.

**Example eval 1:**
```json
{
  "id": 1,
  "name": "full-deploy-to-staging",
  "prompt": "Deploy the current branch to staging. Last deploy was 3 days ago and there have been 12 commits since then.",
  "expected_output": "Complete deployment following the skill's workflow with pre-deploy checks and post-deploy verification",
  "files": [],
  "expectations": [
    "Ran scripts/pre-deploy-check.sh before deploying",
    "Executed deployment steps in the order defined in workflow.md",
    "Ran post-deploy health check and reported results",
    "Did not force-push or skip CI checks"
  ]
}
```

**Example eval 2:**
```json
{
  "id": 2,
  "name": "deploy-with-migration-failure",
  "prompt": "deploy to staging please, there's a new migration in db/migrations/20260315_add_user_preferences.sql",
  "expected_output": "Deployment that detects migration failure and triggers rollback procedure",
  "files": ["db/migrations/20260315_add_user_preferences.sql"],
  "expectations": [
    "Detected migration in the changeset and ran migration step",
    "Error handling triggered when migration failed",
    "Rollback procedure followed the skill's documented steps",
    "Did not leave the database in a partially migrated state"
  ]
}
```

**What makes a good composition eval:** The prompt should trigger the full workflow. If it only exercises one step, you are testing a script, not the composition.

### Investigation (Runbooks, Data Analysis)

**Prompt pattern:** "Diagnose: {symptom matching a decision tree}" or "Analyze: {question matching a query pattern}"

The symptom must map to a decision tree in the skill. Novel symptoms that do not match any tree test generalization rather than the skill's core content.

**Assertion pattern:**
- "Followed decision tree for {symptom}" — verify the structured investigation path
- "Used query from {queries/X.sql}" — verify skill queries were used, not improvised
- "Produced investigation report matching template" — verify output structure
- "Reached a terminal action" — verify the investigation reached a conclusion

**Baseline comparison:** With-skill should follow structured investigation via decision trees and produce a formatted report. Without-skill will investigate ad-hoc and likely miss diagnostic steps.

**Example eval 1:**
```json
{
  "id": 1,
  "name": "high-latency-checkout-flow",
  "prompt": "Users are reporting checkout is taking 15+ seconds. Started about 2 hours ago. No recent deploys that I know of.",
  "expected_output": "Structured investigation following the latency decision tree, ending with root cause and remediation",
  "files": [],
  "expectations": [
    "Followed the latency decision tree from references/latency-tree.md",
    "Ran the database connection pool query from references/queries/db-pool-check.sql",
    "Checked external dependency latency before concluding it was internal",
    "Produced a report with Summary, Timeline, Root Cause, and Remediation sections"
  ]
}
```

**Example eval 2:**
```json
{
  "id": 2,
  "name": "quarterly-revenue-anomaly",
  "prompt": "Q3 revenue is 22% below forecast but Q2 was on target. Can you figure out what changed? Data is in analytics/revenue_by_segment.csv",
  "expected_output": "Segment-level analysis identifying which segments drove the shortfall",
  "files": ["analytics/revenue_by_segment.csv"],
  "expectations": [
    "Used the segment decomposition query from references/queries/revenue-by-segment.sql",
    "Compared Q3 vs Q2 at the segment level, not just aggregate",
    "Identified the specific segment(s) responsible for the shortfall",
    "Reached a terminal conclusion with recommended next steps"
  ]
}
```

**What makes a good investigation eval:** The symptom must map to a decision tree in the skill. If the symptom is novel, you are testing the agent's general reasoning, not the skill's investigation structure.

### Extraction (Scaffolding)

**Prompt pattern:** "Create/scaffold a new {component type} called {name}"

Use realistic component names with edge cases: multi-word names, abbreviations, names that test casing conventions.

**Assertion pattern:**
- "Created file at {expected path}" — verify file placement follows conventions
- "Uses {naming convention}" — verify casing and naming rules
- "Includes test file" — verify co-located test was generated
- "Follows template structure" — verify generated code matches the template

**Baseline comparison:** With-skill should produce convention-following code at the correct paths with co-located tests. Without-skill will produce generic scaffolding that may not match project conventions.

**Example eval 1:**
```json
{
  "id": 1,
  "name": "scaffold-multi-word-component",
  "prompt": "Create a new component called UserProfileSettings — it needs to show the user's notification preferences and let them toggle each one",
  "expected_output": "Component at the correct path with proper naming, co-located test, and template-matching structure",
  "files": [],
  "expectations": [
    "Created src/components/UserProfileSettings/UserProfileSettings.tsx",
    "Created src/components/UserProfileSettings/UserProfileSettings.test.tsx",
    "Component file uses PascalCase for the component name",
    "Test file imports from the sibling component file, not from an index"
  ]
}
```

**Example eval 2:**
```json
{
  "id": 2,
  "name": "scaffold-api-endpoint-abbreviation",
  "prompt": "scaffold a new API endpoint for SSO callback handling, we're using the REST conventions from the style guide",
  "expected_output": "API endpoint files following the skill's REST conventions with proper abbreviation handling",
  "files": [],
  "expectations": [
    "Created route file at the path matching the skill's convention for API routes",
    "Abbreviation 'SSO' handled correctly in file naming (kebab-case: sso-callback)",
    "Includes request validation schema",
    "Includes integration test file"
  ]
}
```

**What makes a good extraction eval:** Use realistic component names with edge cases. Names like "Thing" or "MyComponent" do not test convention enforcement. Multi-word names, abbreviations, and names with numbers test whether the templates handle casing correctly.

## evals.json Schema

```json
{
  "skill_name": "example-skill",
  "discipline": "distillation",
  "evals": [
    {
      "id": 1,
      "name": "descriptive-name-for-test-case",
      "prompt": "User's task prompt - realistic, as a real user would phrase it",
      "expected_output": "Human-readable description of what success looks like",
      "files": [],
      "expectations": [
        "Verifiable assertion 1",
        "Verifiable assertion 2"
      ]
    }
  ]
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `skill_name` | string | The skill's name from SKILL.md frontmatter |
| `discipline` | string | One of: `distillation`, `composition`, `investigation`, `extraction` |
| `evals` | array | List of eval objects |
| `evals[].id` | integer | Sequential identifier, starting at 1 |
| `evals[].name` | string | Descriptive, kebab-case. Used as the directory name under `iteration-N/eval-{id}-{name}/` and as the heading in the eval viewer. Choose names that distinguish test cases at a glance: `async-error-middleware` not `test-1` |
| `evals[].prompt` | string | The full prompt sent to the agent. Write it as a real user would. Include file paths, personal context, casual speech, typos if natural |
| `evals[].expected_output` | string | Human-readable summary of what a successful execution produces. Not used for grading. Helps the eval author remember intent |
| `evals[].files` | array | Paths to files the agent needs in its workspace. Empty array if the prompt is self-contained |
| `evals[].expectations` | array | List of verifiable assertion strings. Can be empty initially. Draft them while execution runs are in progress, then refine after reading the transcript |

## Trigger Eval Guidance

Trigger evals test whether the skill's description causes the agent to activate the skill for relevant queries and ignore it for irrelevant ones. Write 20 queries total.

### 10 Should-Trigger Queries

Different phrasings of the same intent, with varying formality. The user does not name the skill explicitly in most of these.

Rules:
- Vary formality: formal request, casual ask, frustrated complaint, terse shorthand
- Include file paths, personal context, typos when natural
- At least 2 queries should not mention the skill's technology by name (test intent detection)
- At least 1 query should include a typo or abbreviation

### 10 Should-Not-Trigger Queries

Near-misses that share keywords but need something different. These must NOT be obviously irrelevant.

Rules:
- Share vocabulary with the skill but require a different capability
- At least 3 queries should mention the skill's technology explicitly (tests that keyword overlap alone is not enough)
- At least 2 should be tasks a user might ask in the same work session but that need a different skill
- None should be completely unrelated ("What's the weather?")

### Discipline-Specific Trigger Examples

**Distillation triggers:**
- Should: "this react component is doing weird stuff with useEffect, can you clean it up? src/hooks/useAuth.ts"
- Should not: "scaffold a new React component for user settings" (extraction, not distillation)

**Composition triggers:**
- Should: "run the full deploy pipeline for the payments service"
- Should not: "why did the last deploy fail? check the logs" (investigation, not composition)

**Investigation triggers:**
- Should: "checkout latency spiked to 12s about an hour ago, can you figure out what's going on"
- Should not: "set up monitoring alerts for checkout latency" (composition, not investigation)

**Extraction triggers:**
- Should: "create a new API endpoint called verify-email following our conventions"
- Should not: "the verify-email endpoint has a bug in the validation logic" (distillation or investigation, not extraction)

### Bad vs Good Trigger Queries

Bad should-trigger:
- "Format this data" (too vague, could match dozens of skills)
- "Use the acme-checkout-verifier skill" (names the skill explicitly, does not test discovery)

Good should-trigger:
- "ok so my boss sent me this xlsx file called 'Q4 sales FINAL v2.xlsx' and she wants a profit margin column added before the board meeting tomorrow" (realistic, contextual, tests intent)
- "can u check if the chekout flow is still broken after that hotfix from yesterday, we got like 200 tickets" (typos, casual, real scenario)

Bad should-not-trigger:
- "What is the meaning of life?" (obviously irrelevant, does not test discrimination)
- "Help me" (too vague to test anything)

Good should-not-trigger:
- "write unit tests for the checkout flow validation" (shares domain but needs testing skill, not verification)
- "our checkout conversion rate dropped 15% last month, can you pull the analytics?" (shares domain keywords, but this is analysis not verification)

## Workspace Structure Reference

The eval command creates this directory structure:

```
{skill-name}-workspace/
├── evals/
│   └── evals.json                       # Eval definitions (schema above)
├── iteration-1/
│   ├── eval-0-{name}/                   # One directory per eval
│   │   ├── with_skill/                  # Execution with the skill loaded
│   │   │   ├── outputs/                 # Files produced by the agent
│   │   │   ├── transcript.md            # Full execution transcript
│   │   │   └── timing.json              # Wall-clock timing data
│   │   ├── without_skill/               # Execution without the skill
│   │   │   ├── outputs/
│   │   │   ├── transcript.md
│   │   │   └── timing.json
│   │   ├── eval_metadata.json           # Eval id, name, prompt, config used
│   │   └── grading.json                 # Grader agent output (per-assertion verdicts)
│   ├── benchmark.json                   # Aggregated metrics across all evals
│   ├── benchmark.md                     # Human-readable benchmark summary
│   └── feedback.json                    # User feedback from review session
└── trigger-optimization/
    ├── eval_set.json                    # 20 trigger queries (10 should, 10 should-not)
    └── results/                         # Trigger eval run outputs
        └── {description-hash}.json      # Results per description variant tested
```

### Directory Naming

- `eval-{id}-{name}`: id is zero-indexed from evals.json, name is the eval's `name` field
- `iteration-N`: increments each time the eval cycle runs. Previous iterations are preserved for comparison
- `trigger-optimization/results/`: one file per description variant tested, named by a hash of the description text

### Key Files

| File | Written By | Read By |
|------|-----------|---------|
| `evals.json` | eval command (initial), user (edits) | executor, grader, comparator |
| `transcript.md` | executor agent | grader agent |
| `grading.json` | grader agent | comparator, analyzer, benchmark aggregator |
| `benchmark.json` | benchmark aggregator | analyzer agent, eval command |
| `feedback.json` | eval command (from user input) | next iteration planning |
| `eval_set.json` | eval command | `scripts/eval/run_eval.py` |

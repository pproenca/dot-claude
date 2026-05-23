# Diagnose with repo-health, then pin behavior

## Reading `repo-health.py` output

Run `python3 <plugin>/scripts/repo-health.py <repo>` (add `--bots-separate` for
autonomous-loop repos where a bot makes most commits).

| Signal | Healthy | Warning | Action |
|---|---|---|---|
| feat:fix (overall) | 1:2 – 1:4 | `< 1:1` (no hardening) or `> 1:6` (fragile) | sweep tests on the worst scope |
| feat:fix (per scope) | even across scopes | one scope ≫ others | redesign or characterization-test that scope |
| churn concentration | top file is a test/spec file | top file is a fragile impl file | pin it with tests; consider splitting it |
| deletion bursts | spiky | flat-zero for long stretches | schedule a refactor burst |
| bot % (`--bots-separate`) | intentional (loop) or ~0 | accidental | confirm state is in a separate repo |
| CI commit share | modest | very high (clawsweeper humans = 15%) | the automation IS the product — invest deliberately |

Real readings: clawpatch overall 1:3.4 but `pr` scope **1:10** (a redesign candidate);
`mapper.test.ts` touched in 144/372 commits (the real spec); refactor day = 66% of all
deletions. crabbox 1:2.3. clawsweeper humans 1:4.9 with 15% CI commits.

## Contract gap audit (do this before evolving)
Run the **audit-agent-cli** checklist quickly. If any of these are missing, fix them
*first* — evolving on a broken contract just multiplies the breakage:
- no `--json` / unstable output schema
- exit codes not enumerated by failure class
- prompts in agent mode (no `--no-input`)
- model holds write credentials during analysis
- state mixed into the code repo (not gitignored / not separated)
- no boundary validation (model output trusted without parse)

## Pin behavior FIRST (characterization tests)
The non-negotiable step before any refactor. The pattern (from clawpatch):

1. Identify the churn-hot file from `repo-health.py` (the top of "churn concentration").
2. If its behavior isn't already covered, add **characterization tests** — tests that
   capture *current* behavior exactly (not desired behavior), so any drift is caught.
   Use a real temp-dir fixture + the deterministic `mock` provider; assert on
   structured result objects with `toMatchObject` and on error `code` strings. No
   snapshots.
3. Run them green against the unchanged code. Now they're a safety net.
4. Refactor / harden. The tests must stay green (refactor) or get one new `it` per new
   edge case (harden).

```ts
// characterization test: lock CURRENT behavior before refactoring the mapper
it("currently maps an Express router mounted at a prefix", async () => {
  const root = await mkdtemp(join(tmpdir(), "tool-"));
  await writeFixture(root, "src/api.ts",
    "import { Router } from 'express';\nconst r = Router();\nr.get('/users', h);\nexport default r;\n");
  await writeFixture(root, "src/app.ts", "import api from './api';\napp.use('/v1', api);\n");
  const { features } = await mapFeatures(root, await detectProject(root), []);
  expect(features.map((f) => f.title)).toContain("Route /v1/users"); // pin the prefix behavior
});
```

## Why this discipline enables speed
Breadth (new languages/providers) is contributed by humans and agents via PRs against
a stable interface; the maintainer's job is the hardening loop. That loop is only safe
because every behavior is pinned by a focused test. Test coverage is the thing that
lets you accept a flood of breadth PRs and grind their edge cases without regressions.

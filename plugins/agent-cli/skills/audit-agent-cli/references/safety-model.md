# The guarded-mutation safety model

For tools that mutate (especially autonomous loops). Distilled from `clawsweeper`'s
production model — the bar that lets an agent run unattended without doing damage. Audit
a mutating/autonomous CLI against all five.

## 1. The credential boundary — the model never holds write creds during analysis
Scrub every token from the environment before spawning the model; re-inject ONLY a
read-scoped token. clawsweeper's `codexEnv`:
```ts
export function codexEnv(options: { ghToken?: string } = {}): NodeJS.ProcessEnv {
  const env = { ...process.env };
  delete env.GH_TOKEN; delete env.GITHUB_TOKEN;
  delete env.OPENAI_API_KEY; delete env.CODEX_API_KEY;
  delete env.APP_PRIVATE_KEY; // ...every write/admin credential
  if (options.ghToken) env.GH_TOKEN = options.ghToken; // only a READ-scoped token, explicitly
  return env;
}
```
Audit: review/analysis runs with `--sandbox read-only` and a read-only token; **no write
credential is reachable from the model's process.** FAIL = critical.

## 2. Two-phase / two-token split — thinking is read-only, applying is deterministic
The model only ever **proposes**; a separate deterministic code path **applies**. In CI
these are different jobs with different token scopes:
- review/plan job → token `contents: read, issues: read, pull-requests: read`
- execute job → token `contents: write, issues: write, ...`, gated by an org var
  (`ALLOW_EXECUTE == '1'`) and `mode in {execute, autonomous} && !dry_run`.
The model's output schema even bakes this in: action status enum is
`planned/skipped/blocked/failed` — there is **no `executed`**, because only the
deterministic applicator records execution.

## 3. Recheck live state immediately before every mutation
Store the target's `updated_at` (or a snapshot hash) at review time; the apply path
re-fetches live state and **skips if it drifted**:
```ts
const { item } = fetchItem(number);                       // fresh fetch at apply time
const updatedSinceReview = storedUpdatedAt && item.updatedAt !== storedUpdatedAt;
const reviewCommentOnly  = item.updatedAt === commentUpdatedAt(existingReviewComment);
if (isCloseProposal && updatedSinceReview && !reviewCommentOnly) {
  return { number, action: "skipped_changed_since_review", reason: "updated_at changed" };
}
```
Plus the close itself only runs after re-validating gates (labels, maintainer-authorship,
age) on the *freshly fetched* item. README states it verbatim: *"every GitHub mutation is
rechecked against live target state immediately before it happens."* FAIL on an
autonomous tool = critical.

## 4. One deterministic apply path
There is exactly one code path that writes. Auto-mutation payloads must carry the proof
they need (e.g. a close payload requires `target_updated_at`; a merge action requires a
`merge_preflight` object with `security_status` const-locked to `"cleared"` and
`findings_addressed: true`). Missing proof blocks the action. Audit: count the write
call sites — there should be one guarded chokepoint, not writes scattered through the model-facing code.

## 5. Idempotent, marker-backed side effects
External side effects are upserted, not appended. clawsweeper keeps **one** durable
review comment per item, found by an HTML marker (`<!-- clawsweeper-review item=N -->`),
edited in place, and only on comments it authored. Hidden verdict markers
(`<!-- ...-verdict:pass -->`) let downstream automation route off structure, not prose.
Audit: re-running the tool must not duplicate comments/PRs/labels.

## Defaults that make the above cheap (from clawpatch)
- Config default: `git: { requireCleanWorktreeForFix: true, commit: false, openPr: false }`.
- Every provider method runs read-only except the single mutating method, which opts into
  a write sandbox explicitly.
- Dirty-worktree refusal excludes the tool's own state dir (so its writes don't trip it).
- Record base SHA into the patch record at plan time; re-verify before committing; refuse
  if HEAD moved or unrelated files are dirty.

## Externalize the boundary as policy (see agent-spec-kit)
The security boundary itself should be a versioned `instructions/security-boundary.md`
the model reads at runtime, with explicit escalation verbs (`route_security`,
`needs_human`) and an anti-overuse clause — not a rule buried in code.

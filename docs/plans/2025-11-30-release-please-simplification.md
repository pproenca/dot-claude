# Release-Please Simplification Plan

> **For Claude:** REQUIRED SUB-SKILL: Use super:executing-plans to implement this plan task-by-task.

**Goal:** Simplify release-please setup by removing unnecessary validation job, resetting version to 1.0.0, and establishing a lean standard configuration.

**Architecture:** Single-job GitHub workflow that runs release-please on push to master. Manifest-based configuration with extra-files for JSON version updates. Clean slate starting at v1.0.0.

**Tech Stack:** GitHub Actions, release-please-action@v4, manifest configuration

---

## Current State Analysis

**Issues identified:**
1. Unnecessary `validate` job in workflow that checks JSON syntax
2. Version currently at 3.1.0, user wants to reset to 1.0.0
3. PR #5 exists proposing 4.0.0 - needs to be closed
4. GitHub ruleset needs simplification (separate from release-please)

**Files to modify:**
- `.github/workflows/release-please.yml` - Remove validate job
- `.release-please-manifest.json` - Reset to 1.0.0
- `version.txt` - Reset to 1.0.0
- `.claude-plugin/marketplace.json` - Reset to 1.0.0
- `plugins/*/.claude-plugin/plugin.json` (8 files) - Reset to 1.0.0

---

### Task 1: Close Existing Release PR

**Files:**
- None (GitHub API operation)

**Step 1: Close PR #5**

Close the existing release-please PR since we're resetting versions.

Run:
```bash
gh pr close 5 --repo pproenca/dot-claude --comment "Closing to reset release-please at v1.0.0"
```

Expected: PR closed successfully

**Step 2: Delete the release-please branch**

Run:
```bash
gh api -X DELETE repos/pproenca/dot-claude/git/refs/heads/release-please--branches--master--components--dot-claude
```

Expected: Branch deleted (204 response or success message)

---

### Task 2: Simplify GitHub Actions Workflow

**Files:**
- Modify: `.github/workflows/release-please.yml`

**Step 1: Replace workflow with simplified version**

```yaml
name: release-please

on:
  push:
    branches:
      - master

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

**Step 2: Verify YAML syntax**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release-please.yml'))"
```

Expected: No output (valid YAML)

**Step 3: Commit the change**

```bash
git add .github/workflows/release-please.yml
git commit -m "build(ci): simplify release-please workflow

Remove unnecessary validate job that checked JSON syntax.
The workflow now only runs release-please on push to master."
```

---

### Task 3: Reset Version to 1.0.0 in Manifest

**Files:**
- Modify: `.release-please-manifest.json`

**Step 1: Update manifest to 1.0.0**

```json
{
  ".": "1.0.0"
}
```

**Step 2: Commit the change**

```bash
git add .release-please-manifest.json
git commit -m "build: reset release-please manifest to v1.0.0"
```

---

### Task 4: Reset version.txt

**Files:**
- Modify: `version.txt`

**Step 1: Update version.txt**

```
1.0.0
```

**Step 2: Commit the change**

```bash
git add version.txt
git commit -m "build: reset version.txt to 1.0.0"
```

---

### Task 5: Reset marketplace.json Version

**Files:**
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Update version field**

Change line 3 from `"version": "3.1.0"` to `"version": "1.0.0"`.

**Step 2: Commit the change**

```bash
git add .claude-plugin/marketplace.json
git commit -m "build: reset marketplace.json version to 1.0.0"
```

---

### Task 6: Reset All Plugin Versions

**Files:**
- Modify: `plugins/super/.claude-plugin/plugin.json`
- Modify: `plugins/commit/.claude-plugin/plugin.json`
- Modify: `plugins/shell/.claude-plugin/plugin.json`
- Modify: `plugins/dev/.claude-plugin/plugin.json`
- Modify: `plugins/doc/.claude-plugin/plugin.json`
- Modify: `plugins/debug/.claude-plugin/plugin.json`
- Modify: `plugins/agent/.claude-plugin/plugin.json`
- Modify: `plugins/blackbox/.claude-plugin/plugin.json`

**Step 1: Update all plugin.json files to version 1.0.0**

For each file, change the `"version"` field to `"1.0.0"`.

**Step 2: Commit all plugin version changes together**

```bash
git add plugins/*/.claude-plugin/plugin.json
git commit -m "build: reset all plugin versions to 1.0.0"
```

---

### Task 7: Simplify release-please-config.json (Optional Cleanup)

**Files:**
- Modify: `release-please-config.json`

**Step 1: Review current config for any unnecessary complexity**

The current config is mostly fine. Optional: remove hidden changelog sections if not needed.

Current config keeps:
- `release-type: simple`
- `include-v-in-tag: true`
- All extra-files for JSON version updates
- Changelog sections for feat, fix, perf, refactor, docs

No changes needed unless user wants further simplification.

**Step 2: Skip or commit if changes made**

If no changes: Skip this task.

---

### Task 8: Create Initial Git Tag

**Files:**
- None (git operation)

**Step 1: Create v1.0.0 tag**

After all version resets are committed and pushed:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Expected: Tag created and pushed

**Step 2: Verify tag exists**

```bash
git tag -l "v1.0.0"
```

Expected: `v1.0.0`

---

### Task 9: Push Changes and Verify

**Files:**
- None (git operation)

**Step 1: Push all commits to master**

```bash
git push origin master
```

**Step 2: Verify workflow runs**

Check GitHub Actions to confirm release-please workflow runs without the validate job.

Run:
```bash
gh run list --repo pproenca/dot-claude --limit 3
```

Expected: See release-please workflow running or completed

---

### Task 10: Configure GitHub Ruleset (Separate Task)

**Note:** This is separate from release-please. The user mentioned "lean ruleset" - this requires GitHub repository settings.

**Recommended lean ruleset for master branch:**

1. **Require pull request before merging** - Yes
2. **Required approvals** - 0 (for solo projects) or 1
3. **Require status checks** - None required (or just release-please)
4. **Allow force pushes** - No
5. **Allow deletions** - No

**Step 1: Configure via GitHub UI or API**

Go to: `https://github.com/pproenca/dot-claude/settings/rules`

Or use GitHub API:
```bash
gh api repos/pproenca/dot-claude/rulesets \
  --method POST \
  --field name="master-protection" \
  --field target="branch" \
  --field enforcement="active" \
  --field conditions='{"ref_name":{"include":["refs/heads/master"],"exclude":[]}}' \
  --field rules='[{"type":"pull_request","parameters":{"required_approving_review_count":0,"dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,"require_last_push_approval":false}}]'
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `.github/workflows/release-please.yml` | Remove validate job |
| `.release-please-manifest.json` | 3.1.0 → 1.0.0 |
| `version.txt` | 3.1.0 → 1.0.0 |
| `.claude-plugin/marketplace.json` | 3.1.0 → 1.0.0 |
| `plugins/*/.claude-plugin/plugin.json` | 3.1.0 → 1.0.0 (8 files) |
| Git tag | Create v1.0.0 |
| PR #5 | Close |

---

## Post-Implementation Verification

After all tasks complete:

1. **Check versions are 1.0.0:**
   ```bash
   grep -r '"version"' .claude-plugin/ plugins/*/.claude-plugin/ | grep -v "1.0.0" && echo "FAIL: Version mismatch" || echo "PASS: All versions 1.0.0"
   ```

2. **Check tag exists:**
   ```bash
   git tag -l "v1.0.0"
   ```

3. **Check workflow runs without validate job:**
   - Visit GitHub Actions page
   - Confirm only `release-please` job runs (no `validate`)

4. **Future releases will work:**
   - Next conventional commit with `feat:` or `fix:` will trigger release-please
   - PR will be created proposing next version (1.1.0 or 1.0.1)

# CI/CD

This document describes the CI/CD setup for dot-claude, including automated releases and branch protection.

## Overview

```mermaid
flowchart LR
    subgraph "Developer Workflow"
        DEV[Developer] --> PR[Pull Request]
        PR --> CHECKS[Status Checks]
        CHECKS --> REVIEW[Code Review]
        REVIEW --> MERGE[Merge to master]
    end

    subgraph "Automated Release"
        MERGE --> RP[release-please]
        RP --> RPR[Release PR]
        RPR --> APPROVE[Approve & Merge]
        APPROVE --> TAG[Create Tag]
        TAG --> RELEASE[GitHub Release]
    end

    subgraph "Branch Protection"
        RULES[3 Rulesets]
        RULES --> BASE[Base Protection]
        RULES --> PRR[PR Requirements]
        RULES --> PUSH[Push Restrictions]
    end
```

## Release Process

We use [release-please](https://github.com/googleapis/release-please) for automated versioning and changelog generation.

### How It Works

1. **Conventional Commits**: All commits to `master` must follow [Conventional Commits](https://www.conventionalcommits.org/) format
2. **Release PR**: release-please automatically creates/updates a Release PR with:
   - Version bump based on commit types (`feat:` = minor, `fix:` = patch)
   - Generated CHANGELOG.md entries
   - Updated version in all plugin.json files
3. **Release**: Merging the Release PR triggers:
   - Git tag creation
   - GitHub Release with release notes

### Commit Types and Versioning

| Commit Type | Version Bump | Changelog Section |
|-------------|--------------|-------------------|
| `feat:` | Minor (0.X.0) | Features |
| `fix:` | Patch (0.0.X) | Bug Fixes |
| `perf:` | Patch | Performance |
| `refactor:` | Patch | Code Refactoring |
| `docs:` | Patch | Documentation |
| `chore:` | None | Hidden |

### Configuration Files

| File | Purpose |
|------|---------|
| `release-please-config.json` | Release configuration (type, changelog sections, extra files) |
| `.release-please-manifest.json` | Current version tracking |
| `.github/workflows/release-please.yml` | GitHub Actions workflow |

## GitHub App Authentication

The release-please workflow uses a GitHub App for authentication, enabling it to bypass branch protection rulesets.

### Why a GitHub App?

- `GITHUB_TOKEN` cannot bypass repository rulesets
- GitHub Apps can be granted bypass permissions for specific rulesets
- Provides audit trail of automated actions

### App Configuration

| Setting | Value |
|---------|-------|
| App Name | `release-please-dot-claude` |
| App ID | Stored in `vars.RELEASE_PLEASE_APP_ID` |
| Private Key | Stored in `secrets.RELEASE_PLEASE_PRIVATE_KEY` |
| Permissions | Contents (R/W), Pull requests (R/W), Metadata (R) |

### Workflow Authentication Flow

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant TOKEN as create-github-app-token
    participant APP as GitHub App
    participant RP as release-please
    participant REPO as Repository

    GHA->>TOKEN: Request token
    TOKEN->>APP: Authenticate with App ID + Private Key
    APP-->>TOKEN: Installation token
    TOKEN-->>GHA: Token output
    GHA->>RP: Run with app token
    RP->>REPO: Create PR / Push commits
    Note over REPO: Bypasses rulesets<br/>(app is exempt)
```

## Branch Protection Rulesets

The `master` branch is protected by three rulesets following the 3-ruleset pattern:

### Ruleset 1: Base Protection (No Bypass)

Applies to **everyone**, including the release-please bot.

| Rule | Purpose |
|------|---------|
| Restrict deletions | Cannot delete master branch |
| Restrict force pushes | Cannot force push |
| Require linear history | No merge commits |

### Ruleset 2: PR Requirements (Bot Exempt)

Applies to developers; release-please bot can bypass.

| Rule | Purpose |
|------|---------|
| Require pull request | All changes via PR |
| Required approvals: 1 | At least one review |
| Dismiss stale reviews | Re-review after push |
| Require status checks | `validate` must pass |

### Ruleset 3: Push Restrictions (Bot Exempt)

Applies to developers; release-please bot can bypass.

| Rule | Purpose |
|------|---------|
| Restrict pushes | Cannot push directly to master |

### Visual Summary

```
+-----------------------------------------------------------+
|                    MASTER BRANCH                          |
+-----------------------------------------------------------+
|  Ruleset 1: Base Protection (NO BYPASS)                   |
|  - No force push                                          |
|  - No deletion                                            |
|  - Linear history                                         |
+-----------------------------------------------------------+
|  Ruleset 2: PR Requirements (release-please EXEMPT)       |
|  - Require PR with 1+ approval                            |
|  - Require status checks (validate)                       |
|  - Dismiss stale reviews                                  |
+-----------------------------------------------------------+
|  Ruleset 3: Push Restrictions (release-please EXEMPT)     |
|  - Block direct pushes                                    |
+-----------------------------------------------------------+

Developers: Must create PR -> Pass checks -> Get approval -> Merge
Bot:        Can push directly (version bumps, tags, changelog)
```

## Validation Workflow

Before release-please runs, a validation job checks all plugin JSON files:

```yaml
validate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Validate plugin JSON files
      run: |
        for f in .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json; do
          jq empty "$f" || exit 1
          jq -e '.name and .version' "$f" > /dev/null || exit 1
        done
```

This ensures:
- Valid JSON syntax in all plugin manifests
- Required fields (`name`, `version`) are present

## Troubleshooting

### Release PR Not Created

1. Check workflow ran: `gh run list --workflow=release-please.yml`
2. Verify commits follow Conventional Commits format
3. Check for existing Release PR: `gh pr list --label "autorelease: pending"`

### Bot Cannot Push

1. Verify app is installed on repository
2. Check app has correct permissions (Contents, Pull requests)
3. Verify rulesets have app in bypass list:
   ```bash
   gh api repos/OWNER/REPO/rulesets/ID --jq '.bypass_actors'
   ```

### Status Checks Failing

1. Check `validate` job output in workflow run
2. Verify JSON syntax: `jq empty plugins/*/.claude-plugin/plugin.json`
3. Check required fields: `jq '.name, .version' plugins/*/.claude-plugin/plugin.json`

## Setup Reference

To replicate this setup on another repository, see the implementation plan:
[2025-11-29-github-app-rulesets-release-please.md](plans/2025-11-29-github-app-rulesets-release-please.md)

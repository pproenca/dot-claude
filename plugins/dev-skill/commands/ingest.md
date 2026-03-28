---
description: "Ingest an existing skill, plugin, or documentation into a quality-gated skill. Accepts GitHub repos, local directories, or URLs — fetches, analyzes, restructures, and validates."
argument-hint: "<source> [output-path]"
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, AskUserQuestion, WebFetch, WebSearch, TaskCreate, TaskUpdate, TaskList
---

# Skill Ingest

Transform existing source material — GitHub repos, local directories, documentation URLs, or existing skill folders — into a quality-gated skill that follows dev-skill conventions.

This is the **curation** path. Unlike `/dev-skill:new` (which creates from scratch), ingest starts from source material that already exists and restructures it into a validated skill.

**IMPORTANT**: This command requires the Opus model for high-quality analysis. Always use `model: opus` when invoking agents.

## Input

A source path or URL:
- **GitHub repo path**: `owner/repo/path/to/skill` or a full GitHub URL
- **Local directory**: `./path/to/existing-skill` or `~/vendor/some-docs/`
- **Documentation URL**: `https://docs.example.com/api-reference`
- **Existing skill folder**: `~/.claude/skills/some-skill` (remix/upgrade)

Optional output path (defaults to asking the user).

---

## Step 0: Determine Source Type and Output Location

### 0a: Classify the source

Detect what was provided:

| Input Pattern | Source Type | Fetch Method |
|---|---|---|
| `owner/repo` or `owner/repo/path` | GitHub repo | `gh api` to list + fetch files |
| `https://github.com/...` | GitHub URL | Parse owner/repo/path, then `gh api` |
| `https://...` (non-GitHub) | Documentation URL | `WebFetch` to pull content |
| Path starting with `.`, `/`, or `~` | Local directory | Direct `Read` + `Glob` |

### 0b: Ask output location

Use `AskUserQuestion`:

```
Question: "Where should I create the ingested skill?"
Header: "Location"
Options:
- "~/.claude/skills/ (Global)" — Available across all projects
- ".claude/skills/ (Project)" — Specific to this project, shared via git
```

Store as `{output-base}`.

---

## Step 1: Fetch & Inventory

### For GitHub sources:

```bash
# List all files at the path
gh api repos/{owner}/{repo}/contents/{path} --jq '.[].name'

# Fetch each file
gh api repos/{owner}/{repo}/contents/{path}/{file} --jq '.content' | base64 -d
```

### For local directories:

Read the directory tree with `Glob` and `Read`.

### For documentation URLs:

Use `WebFetch` to pull content. For multi-page docs, follow navigation links to pull related pages.

### Display inventory

Show the user what was found:

```markdown
## Source Inventory

| # | File | Type | Lines | Description |
|---|------|------|-------|-------------|
| 1 | SKILL.md | Skill entry | 280 | Main workflow doc |
| 2 | references/auth.md | Reference | 150 | OAuth patterns |
| 3 | scripts/deploy.sh | Script | 60 | Deploy automation |
```

Ask via `AskUserQuestion`:

```
Question: "Which files should be included in the skill?"
Header: "File Selection"
Options:
- "Include all files"
- "Let me select specific files"
```

If the user selects specific files, ask which to include.

---

## Step 2: Analyze & Detect Structure

Read all included files and analyze their content to infer the skill's natural structure. **Do not force a discipline** — detect the shape from the content.

### Structure Detection Signals

| Signal | Inferred Structure | Discipline |
|---|---|---|
| Phased workflow (Phase 1, Phase 2...) | Guided decision workflow | composition |
| 40+ rule files with impact/tags frontmatter | Progressive-disclosure reference | distillation |
| Template files with parameter placeholders | Scaffolding templates | extraction |
| Decision trees, symptom catalogs, queries | Investigation runbook | investigation |
| Scripts with verification/assertion logic | Verification workflow | composition |
| Mixed (references + scripts + workflow) | Hybrid — use dominant pattern | infer from content ratio |

### Content Analysis

For each file, determine:
- **Role**: Is it an entry point, reference doc, script, template, or config?
- **Quality**: Does it follow dev-skill conventions already? What needs adaptation?
- **Dependencies**: Does it reference other files? External tools? Companion skills?

### Propose skill structure

Present the proposed structure as regular text:

```markdown
## Proposed Skill Structure

**Inferred discipline:** composition (guided workflow with reference docs)
**Inferred type:** scaffolding

```
{skill-name}/
├── SKILL.md              ← from source SKILL.md (adapted)
├── metadata.json          ← generated
├── gotchas.md             ← initialized
├── scripts/
│   └── test-server.sh     ← from source scripts/test.sh (adapted)
└── references/
    ├── auth.md            ← from source docs/auth.md (as-is)
    └── tool-design.md     ← from source docs/tools.md (restructured)
```

### Adaptations needed:
- SKILL.md: Add frontmatter (name + description), "When to Apply" section, "Prerequisites" section
- scripts/test.sh → test-server.sh: Add safety header, input validation, actionable errors
- docs/tools.md → references/tool-design.md: No changes needed, content is already well-structured
```

Ask via `AskUserQuestion`:

```
Question: "Does this structure look right?"
Header: "Structure Review"
Options:
- "Approve and proceed"
- "Adjust structure"
- "Major revisions needed"
```

**Only proceed after user approval.**

---

## Step 3: Transform & Generate

Transform source files into dev-skill convention-following files. The goal is **minimal modification** — preserve the source's voice and content, only add what's missing.

### 3a: SKILL.md Adaptation

If the source has a SKILL.md or main entry document:

1. **Add frontmatter** if missing:
   ```yaml
   ---
   name: {skill-name}
   description: {trigger description — infer from content}
   ---
   ```

2. **Add "When to Apply" section** if missing — derive from the skill's content (what triggers it)

3. **Add "Workflow Overview" section** if missing — extract from existing phase/step structure

4. **Add "Prerequisites" section** if missing — scan for tool dependencies (npx, python, etc.)

5. **Add "Reference files" section** at bottom — link to all reference docs with one-line descriptions

6. **Ensure under 500 lines** — if longer, extract detail into reference files

### 3b: Script Adaptation

For each script file:

1. **Add safety header** if missing: `set -euo pipefail`
2. **Add dependency check** if the script uses external tools (`command -v`)
3. **Add input validation** if missing (check required args, print usage)
4. **Add actionable error messages** (tell user what to do, not just what failed)
5. **Ensure executable**: `chmod +x`

### 3c: Reference File Adaptation

Reference files usually need minimal changes:

1. **Ensure they have a title** (H1 heading)
2. **Check internal links** — update paths if file structure changed
3. **Add cross-references** to other skill files where relevant

### 3d: Generate metadata.json

```json
{
  "version": "0.1.0",
  "organization": "{infer from source or ask user}",
  "technology": "{infer from content}",
  "discipline": "{detected in Step 2}",
  "type": "{detected in Step 2}",
  "date": "{current month and year}",
  "abstract": "{1-2 sentence summary — infer from content}",
  "references": ["{source URLs}"]
}
```

### 3e: Generate gotchas.md

```markdown
# Gotchas

No known gotchas yet. Append entries as they're discovered during use.
```

### 3f: Write all files

Write all transformed files to `{output-base}/{skill-name}/`.

---

## Step 4: Quality Gate (Automatic)

**This step is mandatory and runs automatically.** Unlike `/dev-skill:new` where validation and review are separate manual steps, ingest runs both as a single gate.

### 4a: Structural validation

```bash
node /Users/pedroproenca/.claude/plugins/marketplaces/dot-claude/plugins/dev-skill/scripts/validate-skill.js {output-base}/{skill-name}
```

Fix ALL errors before proceeding. Address warnings where feasible.

### 4b: Substance review

Launch the `skill-reviewer` agent with the discipline-appropriate rubric:

```
/Users/pedroproenca/.claude/plugins/marketplaces/dot-claude/plugins/dev-skill/templates/disciplines/{discipline}/RUBRIC.md
```

Fix ALL critical issues identified by the reviewer.

### 4c: Re-validate after fixes

If the reviewer caused changes, re-run validation to ensure no regressions.

---

## Step 5: Transformation Report

Display a summary of what was done:

```markdown
## Ingest Complete

**Source:** {source path/URL}
**Output:** {output-base}/{skill-name}/
**Discipline:** {discipline} | **Type:** {type}
**Validation:** PASS (0 errors, 0 warnings)

### Files

| Source File | → | Output File | Changes |
|-------------|---|-------------|---------|
| SKILL.md | → | SKILL.md | +frontmatter, +When to Apply, +Prerequisites |
| docs/auth.md | → | references/auth.md | Moved, no content changes |
| scripts/test.sh | → | scripts/test-server.sh | +safety header, +input validation |
| — | → | metadata.json | Generated |
| — | → | gotchas.md | Generated |

### Adaptations Applied
- Added SKILL.md frontmatter with trigger description
- Added "When to Apply" section (5 triggers)
- Added "Prerequisites" section (Node.js >= 18, jq)
- Added safety headers to 1 script
- Generated metadata.json and gotchas.md

### Source Preserved
- 6 reference files: no content changes, only path adjustments
- All code examples, diagrams, and technical content unchanged
```

---

## Step 6: Suggest Next Steps

After the report, suggest follow-up actions:

```markdown
## Next Steps

The skill is structurally valid and passes quality review. Consider:

1. **Test it:** `/dev-skill:eval {skill-path}` — run functional tests against real prompts
2. **Optimize the description:** The trigger description was inferred from content. Test whether it activates correctly for relevant queries.
3. **Add gotchas:** Use the skill for a few sessions and capture failure points in gotchas.md.
```

If the source had companion skills (referenced but not ingested), mention them:

```markdown
### Companion Skills Found
The source references these companion skills that weren't ingested:
- `build-mcp-app` — Interactive UI widgets (hand-off from Phase 2)
- `build-mcpb` — Bundled local servers (hand-off from Phase 2)

Run `/dev-skill:ingest` on each to bring them in.
```

---

## Special Cases

### Ingesting from an existing dev-skill skill (remix)

When the source is already a dev-skill skill (has metadata.json with discipline/type):
- Skip structure detection — use the existing discipline
- Focus on quality improvements: run reviewer, fix issues, update metadata version
- This is essentially `/dev-skill:evolve` but starting from a copy

### Ingesting from a CLAUDE.md file

When the source is a single CLAUDE.md:
- Analyze the content for discrete skill boundaries
- If it contains multiple unrelated topics, suggest splitting into separate skills
- Extract each skill section into its own SKILL.md + references

### Ingesting from documentation URLs

When fetching from a docs site:
- Follow table-of-contents links to pull all relevant pages
- Convert HTML to markdown (WebFetch handles this)
- Group pages into reference files by topic
- Generate a SKILL.md that navigates the references

### Large sources (100+ files)

When the source has many files:
- Show the top-level structure and ask the user to narrow scope
- Suggest splitting into multiple skills if the scope is too broad
- Flag files that are likely irrelevant (tests, CI config, node_modules)

---

## Mandatory Requirements

**NEVER:**
- Modify the source material's meaning or technical content — only add structure
- Skip the quality gate (Step 4) — validation + review are automatic and mandatory
- Force a discipline that doesn't fit — detect from content, ask if uncertain
- Generate AGENTS.md manually — use `build-agents-md.js` if the skill is distillation

**ALWAYS:**
- Read `/Users/pedroproenca/.claude/plugins/marketplaces/dot-claude/plugins/dev-skill/templates/anatomy/ANATOMY.md` before transforming
- Preserve the source's voice and terminology — don't rewrite content, add structure
- Show the transformation report (Step 5) — the user must see what changed vs source
- Suggest `/dev-skill:eval` as the next step after ingest

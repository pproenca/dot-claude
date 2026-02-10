---
description: Extract coding patterns from reference codebases and generate a style skill (40+ rules)
argument-hint: <repo-or-path> [repo-or-path2] ...
allowed-tools: Read, Write, Bash, Glob, Grep, Task, AskUserQuestion, TodoWrite
---

# Codebase Style Extraction and Skill Generation

You are an expert at extracting coding patterns, architecture, and style conventions from reference codebases and turning them into comprehensive skill files that teach AI agents to write code in that style.

## Input Required

You will receive one or more sources (Git URLs, GitHub shorthand, or local paths):
- Git URLs: `https://github.com/radix-ui/primitives`
- GitHub shorthand: `shadcn-ui/ui`
- Local paths: `/path/to/project` or `./relative/path`

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Parse input sources                                       │
│    ↓                                                         │
│ 2. Clone/link repos to tempdir                              │
│    ↓                                                         │
│ 3. Launch 2 analyzer agents in PARALLEL                     │
│    ├──► structure-analyzer   (org + naming)                  │
│    └──► code-patterns-analyzer (components + error handling) │
│    ↓                                                         │
│ 4. Merge results + review with user (planning checkpoint)   │
│    ↓                                                         │
│ 5. Generate skill using /dev-skill:new patterns             │
│    ↓                                                         │
│ 6. Validate with validate-skill.js + skill-reviewer         │
│    ↓                                                         │
│ 7. Cleanup tempdir                                          │
└─────────────────────────────────────────────────────────────┘
```

### Parallel Analysis Architecture

Analysis is split across 2 specialized Opus agents, dispatched directly from this command:

| Agent | Focus | Model |
|-------|-------|-------|
| `structure-analyzer` | Directory layout, file naming, import ordering, variable/function/type naming conventions | Opus |
| `code-patterns-analyzer` | Component anatomy, module patterns, error handling, validation, async patterns | Opus |

Both agents use Glob/Grep/Read tools (no shell commands). You dispatch them directly via Task and merge their results.

---

## Step 0: Ask Where to Write the Skill

**Before starting analysis**, ask the user where to write the skill using `AskUserQuestion`:

```
Question: "Where should I create this skill?"
Header: "Location"
Options:
- "~/.claude/skills/ (Global)" - Available across all projects, personal customizations
- ".claude/skills/ (Project)" - Specific to this project, shared with team via git
```

Store the chosen path as `{output-base}` and use it for all file generation.

Also ask for the skill name:

```
Question: "What should the skill be named?"
Header: "Skill Name"
Provide examples based on the input repos (e.g., "radix-style", "shadcn-patterns", "company-react-style")
```

---

## Step 1: Parse and Validate Sources

Parse the input argument(s) to identify source types:

**Input:** `$ARGUMENTS`

For each source, determine:
1. **Git URL**: Starts with `https://`, `git@`, or `ssh://`
2. **GitHub shorthand**: Matches `user/repo` pattern (no `/` prefix, no protocol)
3. **Local path**: Everything else - verify it exists as a directory

Validate all sources before proceeding:
- Git URLs: Must be accessible (test with `git ls-remote`)
- GitHub shorthand: Convert to `https://github.com/{user}/{repo}`
- Local paths: Must exist and be directories

Report any invalid sources and ask user to correct them before continuing.

---

## Step 2: Clone/Link Repositories

Create a temporary directory and clone/link all sources:

```bash
TEMP_DIR=$(mktemp -d)
bash ${CLAUDE_PLUGIN_ROOT}/scripts/clone-repos.sh "$TEMP_DIR" [sources...]
```

The script will:
- Shallow clone Git repositories (depth=1)
- Create symlinks for local directories
- Output JSON with status of each clone

Example output:
```json
[
  {"name": "primitives", "source": "radix-ui/primitives", "type": "git", "path": "/tmp/xxx/primitives", "files": 245, "language": "typescript", "status": "success"},
  {"name": "my-project", "source": "./my-project", "type": "local", "path": "/tmp/xxx/my-project", "files": 89, "language": "typescript", "status": "success"}
]
```

Store the paths and metadata for the analyzers.

---

## Step 3: Launch Parallel Analysis

**CRITICAL**: Launch BOTH agents in a SINGLE message with two Task tool calls so they run in parallel.

Use the Task tool to dispatch both agents directly:

### Agent 1: structure-analyzer

```
subagent_type: "dev-skill:structure-analyzer"

Prompt: Analyze the organization and naming conventions in these repositories:
- Paths: {list of repo paths}
- Language: {detected language from clone metadata}
- Framework: {detected framework}

Focus on: directory layout, file naming, test placement, import ordering,
variable/function/type/constant naming conventions, export patterns, co-location patterns.

Sample 15-30 files across different parts of the codebase.
Report patterns with 75%+ consistency and provide real code examples.
```

### Agent 2: code-patterns-analyzer

```
subagent_type: "dev-skill:code-patterns-analyzer"

Prompt: Analyze the implementation patterns in these repositories:
- Paths: {list of repo paths}
- Language: {detected language from clone metadata}
- Framework: {detected framework}

Focus on: component/module anatomy, props patterns, hooks/composables,
error handling, validation, null handling, async patterns, state management.

Read 15-25 complete files to understand context.
Report patterns with 75%+ consistency and provide real code examples.
```

### Merging Results

After both agents complete, merge their findings:

1. **Aggregate patterns** by category — structure-analyzer provides organization + naming patterns, code-patterns-analyzer provides implementation + error handling patterns
2. **Cross-validate** — check for consistency (e.g., if structure-analyzer reports kebab-case files but code-patterns-analyzer found PascalCase component files, note the distinction)
3. **Deduplicate** — merge overlapping observations
4. **Rank by impact** — CRITICAL: foundational patterns (structure, component anatomy), HIGH: consistency patterns (naming, imports), MEDIUM: style preferences, LOW: minor conventions
5. **Multi-repo synthesis** (if multiple repos) — identify patterns common to ALL repos (highest weight) vs repo-specific patterns

---

## Step 4: Planning Checkpoint

Present the merged analysis to the user for review:

```markdown
## Codebase Analysis Summary

### Repositories Analyzed
| Name | Language | Files | Source |
|------|----------|-------|--------|
| primitives | TypeScript | 245 | radix-ui/primitives |
| ...

### Key Patterns Found

**Organization & Naming:**
- [Pattern 1]
- [Pattern 2]

**Implementation Patterns:**
- [Pattern 1]
- [Pattern 2]

### Proposed Rule Categories
| # | Category | Prefix | Rules | Impact |
|---|----------|--------|-------|--------|
| 1 | Organization | org- | ~8 | HIGH |
| 2 | Component Patterns | comp- | ~10 | HIGH |
| 3 | Naming Conventions | name- | ~12 | MEDIUM |
| 4 | Error Handling | err- | ~5 | MEDIUM |
| 5 | ... | ... | ... | ... |

**Total estimated rules:** 40-50
```

Ask user to confirm or adjust:
```
Options:
- "Approve and generate skill"
- "Adjust categories or focus"
- "Show more details on a category"
```

---

## Step 5: Generate Skill

Using the confirmed analysis, generate the skill following `/dev-skill:new` patterns.

### Output Structure

```
{output-base}/{skill-name}/
├── SKILL.md              # Entry point with quick reference
├── AGENTS.md             # Compiled comprehensive guide (generated by script)
├── metadata.json         # Version, source repos, references
├── README.md             # Human-readable overview
├── references/
│   ├── _sections.md      # Category definitions
│   └── {prefix}-{slug}.md # Individual rules (40+ total)
└── assets/
    └── templates/
        └── _template.md  # Rule template for extensions
```

### Generation Process

1. **Generate references/_sections.md**
   - Define all categories with impact levels
   - Order by importance (organization before micro-optimizations)

2. **Generate individual rules** (references/{prefix}-{slug}.md)
   For each pattern found, create a rule with:
   - YAML frontmatter (title, impact, impactDescription, tags)
   - Brief explanation of WHY this pattern matters
   - **Incorrect** code example (what NOT to do)
   - **Correct** code example (what TO do)
   - Optional "When NOT to use" section for nuanced rules

3. **Generate SKILL.md**
   - Entry point with quick reference table
   - Links to all rule files
   - "When to Apply" section

4. **Generate metadata.json**
   - Version, source repos analyzed
   - Date generated
   - Reference URLs if available

5. **Build AGENTS.md**
   - Run: `node ${CLAUDE_PLUGIN_ROOT}/scripts/build-agents-md.js {skill-dir}`
   - NEVER write AGENTS.md manually

---

## Step 6: Validation

Run both automated and agent-based validation:

1. **Automated validation:**
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-dir} --verify-generated
   ```
   Fix ALL errors before proceeding.

2. **Quality review:**
   Launch `skill-reviewer` agent to check:
   - Teaching effectiveness
   - Code example realism
   - Impact claim accuracy
   - Minimal diff philosophy

Fix any issues identified.

---

## Step 7: Cleanup

Remove the temporary directory with cloned repos:

```bash
rm -rf "$TEMP_DIR"
```

---

## Output Summary

After completion, provide a summary:

```markdown
## Skill Generated Successfully

**Skill:** {skill-name}
**Location:** {output-base}/{skill-name}/

### Source Codebases
- radix-ui/primitives (TypeScript, 245 files)
- shadcn-ui/ui (TypeScript, 189 files)

### Rules Generated
| Category | Count | Impact |
|----------|-------|--------|
| Organization | 8 | HIGH |
| Components | 10 | HIGH |
| Naming | 12 | MEDIUM |
| Error Handling | 5 | MEDIUM |
| **Total** | **45** | |

### Next Steps
1. Review generated rules in {output-base}/{skill-name}/references/
2. Test the skill by asking Claude to write code in this style
3. Iterate on rules that need refinement
4. Share the skill with your team (if project-level)

### Usage
This skill will automatically activate when writing code that should match
the analyzed codebase's style. Trigger phrases include:
- "Write a component like radix-ui"
- "Follow the {skill-name} patterns"
- "Match the design system style"
```

---

## Error Handling

### Clone Failures
If a repo fails to clone:
- Check if URL is correct
- Check if repo is private (may need auth)
- Offer to continue with successfully cloned repos

### Empty Analysis
If analysis finds few patterns:
- Ask user if they want to analyze specific directories
- Suggest alternative repos that might be better references
- Offer to proceed with fewer rules

### Validation Failures
If validate-skill.js fails:
- Show specific errors
- Fix automatically where possible
- Re-run validation after fixes

---

## Important Notes

- This command generates STYLE skills (organization, naming, patterns), not performance skills
- The hybrid approach means performance patterns found in the codebase ARE included
- Minimum 40 rules to be comprehensive
- Always cleanup tempdir, even on failure
- Both analyzer agents run on Opus for high-quality pattern extraction

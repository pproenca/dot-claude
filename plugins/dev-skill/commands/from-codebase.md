---
description: Extract coding patterns from reference codebases and generate a style skill (40+ rules)
argument-hint: <repo-or-path> [repo-or-path2] ...
allowed-tools: Read, Write, Bash, Glob, Grep, Task, AskUserQuestion, TodoWrite
---

# Codebase Style Extraction and Skill Generation

You are an expert at extracting coding patterns, architecture, and style conventions from reference codebases and turning them into comprehensive skill files that teach AI agents to write code in that style.

**IMPORTANT**: This workflow requires the Opus model for high-quality analysis and rule generation. Always use `model: opus` when invoking the codebase-analyzer agent.

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
│ 3. Launch codebase-analyzer agent for deep analysis         │
│    ↓                                                         │
│ 4. Review analysis with user (planning checkpoint)          │
│    ↓                                                         │
│ 5. Generate skill using /dev-skill:new patterns             │
│    ↓                                                         │
│ 6. Validate with validate-skill.js + skill-reviewer         │
│    ↓                                                         │
│ 7. Cleanup tempdir                                          │
└─────────────────────────────────────────────────────────────┘
```

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

Store the paths for the analyzer.

---

## Step 3: Launch Codebase Analyzer Agent

Use the Task tool to launch the `codebase-analyzer` agent with `model: opus`:

**Provide to the agent:**
1. List of cloned repository paths
2. Primary language detected
3. Analysis focus areas: organization, components, naming, error handling

**Expected output:**
The agent will return a comprehensive JSON analysis covering:
- Directory and file organization patterns
- Component/module structure patterns
- Naming conventions (variables, functions, types, files)
- Error handling approaches
- A list of preliminary rules extracted

---

## Step 4: Planning Checkpoint

Present the analysis results to the user for review:

```markdown
## Codebase Analysis Summary

### Repositories Analyzed
| Name | Language | Files | Source |
|------|----------|-------|--------|
| primitives | TypeScript | 245 | radix-ui/primitives |
| ...

### Key Patterns Found

**Organization:**
- [Pattern 1]
- [Pattern 2]

**Naming Conventions:**
- [Convention 1]
- [Convention 2]

**Component Structure:**
- [Pattern 1]
- [Pattern 2]

**Error Handling:**
- [Pattern 1]

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
- Use Opus model for analysis (critical for quality)

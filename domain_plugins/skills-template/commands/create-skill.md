---
description: Create a best-practices skill for any language
argument-hint: <language> [--output-dir <path>]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, Task, TodoWrite, WebSearch, WebFetch
---

# Create Best Practices Skill

Generate a comprehensive best-practices skill for any programming language or framework.

## Overview

This command orchestrates the creation of a complete skill containing:
- 40-50 rules across 8 priority-ordered categories
- Detailed code examples (Incorrect/Correct patterns)
- YAML frontmatter for searchability
- Progressive disclosure structure for context efficiency

## Process

### Phase 1: Gather Requirements

**1.0 Parse Arguments**

Parse command arguments from `$ARGUMENTS`:
- First argument (`$1`): Language/framework name (e.g., "cpp", "typescript", "python")
- `--output-dir <path>`: Optional output directory override

Example invocations:
- `/skills-template:create-skill typescript` -> language=typescript
- `/skills-template:create-skill cpp --output-dir ./my-skills` -> language=cpp, output=./my-skills

If `$ARGUMENTS` contains a language, use it directly. Otherwise, proceed to ask.

**1.1 Identify Target Language**

If no language specified in `$ARGUMENTS`, ask the user:

```
AskUserQuestion:
  header: "Language"
  question: "Which language or framework should this skill target?"
  options:
    - label: "C++"
      description: "Modern C++ (C++17/20/23) best practices"
    - label: "TypeScript"
      description: "TypeScript/Node.js performance patterns"
    - label: "Python"
      description: "Python performance and idioms"
    - label: "Go"
      description: "Go idioms and performance patterns"
```

**1.2 Determine Output Location**

Default: `./skills/{language}-best-practices/`

If `--output-dir` provided, use that path.

**1.3 Identify Source Authority**

Ask the user or research the canonical sources:

```
AskUserQuestion:
  header: "Source"
  question: "What authority should be cited as the source?"
  options:
    - label: "Official Guidelines"
      description: "Use official language/framework guidelines (e.g., ISO C++, TypeScript Handbook)"
    - label: "Community Best Practices"
      description: "Aggregate from community resources and expert blogs"
    - label: "Custom"
      description: "I'll specify a custom source"
```

### Phase 2: Research & Planning

**2.1 Launch Research Agent**

Dispatch the skill-architect agent to research and plan the skill:

```
Task(
  subagent_type: "skills-template:skill-architect",
  prompt: "Research and plan a {language}-best-practices skill.

    Target: {language}
    Source: {source}
    Output: {output_dir}

    Perform comprehensive research on {language} performance best practices.
    Identify 8 categories ordered by impact (CRITICAL -> LOW).
    Plan 40-50 specific rules with example patterns.

    Return a structured plan with:
    1. Category definitions (name, prefix, impact, description)
    2. Rule list for each category (title, summary, key pattern)
    3. Reference sources found"
)
```

**2.2 Review Plan with User**

Present the agent's plan and ask for approval:

```markdown
## Proposed Skill Structure

### Categories (Priority Order)

| # | Category | Prefix | Impact | Rules |
|---|----------|--------|--------|-------|
| 1 | {category_1} | {prefix_1} | CRITICAL | 5 |
| 2 | {category_2} | {prefix_2} | CRITICAL | 5 |
...

### Sample Rules Preview

**{Category 1}:**
- {Rule 1.1}: {summary}
- {Rule 1.2}: {summary}
...

### Sources
- {source_1}
- {source_2}
```

Ask for confirmation:

```
AskUserQuestion:
  header: "Approve"
  question: "Does this structure look good?"
  options:
    - label: "Yes, proceed (Recommended)"
      description: "Generate the complete skill"
    - label: "Modify categories"
      description: "I want to adjust the category structure"
    - label: "Add/remove rules"
      description: "I want to change specific rules"
```

### Phase 3: Generate Skill Files

**3.1 Create Directory Structure**

```bash
mkdir -p "{output_dir}/references/rules"
```

**3.2 Generate Files in Parallel**

Use TodoWrite to track progress, then dispatch parallel generation:

```
TodoWrite([
  { content: "Generate SKILL.md", status: "pending" },
  { content: "Generate {language}-performance-guidelines.md", status: "pending" },
  { content: "Generate _sections.md", status: "pending" },
  { content: "Generate _template.md", status: "pending" },
  { content: "Generate Category 1 rules (5 files)", status: "pending" },
  { content: "Generate Category 2 rules (5 files)", status: "pending" },
  { content: "Generate Category 3 rules (4 files)", status: "pending" },
  { content: "Generate Category 4 rules (2 files)", status: "pending" },
  { content: "Generate Category 5 rules (6 files)", status: "pending" },
  { content: "Generate Category 6 rules (7 files)", status: "pending" },
  { content: "Generate Category 7 rules (12 files)", status: "pending" },
  { content: "Generate Category 8 rules (2 files)", status: "pending" },
  { content: "Validate all files", status: "pending" },
  { content: "Create zip package", status: "pending" }
])
```

**3.3 Generate Core Files First**

Generate these sequentially (they define the structure):

1. **_sections.md** - Category definitions
2. **SKILL.md** - Entry point with quick reference
3. **_template.md** - Rule template

**3.4 Generate Guidelines and Rules**

Launch parallel agents for content generation:

```
# Generate main guidelines document
Task(
  subagent_type: "skills-template:skill-architect",
  prompt: "Generate the complete {language}-performance-guidelines.md file.
    Follow the structure from the approved plan.
    Include all {rule_count} rules with detailed Incorrect/Correct examples.
    Use realistic, production-quality code.
    Reference: Read starter/references/guidelines.md for format."
)

# Generate rule files in parallel batches
Task(
  subagent_type: "skills-template:skill-architect",
  prompt: "Generate individual rule files for Category 1 ({prefix_1}).
    Create 5 files: {prefix_1}-{rule_1}.md through {prefix_1}-{rule_5}.md
    Follow _template.md format with YAML frontmatter.
    Impact level: CRITICAL"
)

# ... repeat for other categories
```

### Phase 4: Validation

**4.1 Structure Validation**

```bash
# Check all required files exist
required_files=(
  "SKILL.md"
  "references/{language}-performance-guidelines.md"
  "references/rules/_sections.md"
  "references/rules/_template.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "{output_dir}/${file}" ]]; then
    echo "MISSING: ${file}"
  fi
done

# Count rule files
rule_count=$(find "{output_dir}/references/rules" -name "*.md" ! -name "_*" | wc -l)
echo "Rule files: ${rule_count}"
```

**4.2 Content Validation**

```bash
# Check for remaining placeholders
grep -r '{[A-Z_]*}' "{output_dir}" && echo "ERROR: Placeholders remain" || echo "OK: No placeholders"

# Check YAML frontmatter in rules
for file in {output_dir}/references/rules/*.md; do
  if [[ ! "$file" =~ ^_ ]]; then
    head -1 "$file" | grep -q "^---" || echo "MISSING FRONTMATTER: $file"
  fi
done
```

**4.3 Prefix Consistency Check**

```bash
# Verify rule file prefixes match _sections.md
prefixes=$(grep -oP '\(\K[a-z]+(?=\))' "{output_dir}/references/rules/_sections.md")
for prefix in $prefixes; do
  count=$(ls "{output_dir}/references/rules/${prefix}-"*.md 2>/dev/null | wc -l)
  echo "${prefix}: ${count} rules"
done
```

### Phase 5: Package & Report

**5.1 Create Distribution Package**

```bash
cd "{output_dir}/.."
zip -r "{language}-best-practices.zip" "{language}-best-practices/"
```

**5.2 Final Report**

Present completion summary:

```markdown
## Skill Created Successfully

**Location:** {output_dir}
**Package:** {output_dir}/../{language}-best-practices.zip

### Statistics

| Metric | Count |
|--------|-------|
| Categories | 8 |
| Total Rules | {rule_count} |
| CRITICAL rules | 10 |
| HIGH rules | 4 |
| MEDIUM rules | ~20 |
| LOW rules | ~10 |

### File Structure

```
{language}-best-practices/
+-- SKILL.md (XXX lines)
`-- references/
    +-- {language}-performance-guidelines.md (XXXX lines)
    `-- rules/
        +-- _sections.md
        +-- _template.md
        `-- {rule_count} rule files
```

### Installation

**Claude Code:**
```bash
cp -r {output_dir} ~/.claude/skills/
```

**Claude.ai:**
Add to project knowledge or upload the zip file.

### Next Steps

1. Review generated rules for accuracy
2. Test code examples compile/run
3. Add to your Claude configuration
```

## Tips

- For best results, provide a specific language/framework (e.g., "React 19" not just "JavaScript")
- The skill-architect agent will search for current best practices and official guidelines
- Generation takes 2-5 minutes depending on rule count
- Review generated code examples before publishing - they should be production-quality

## Template Reference

The starter templates are located in:
- `starter/SKILL.md` - Entry point template
- `starter/references/guidelines.md` - Main documentation template
- `starter/references/rules/_sections.md` - Category definitions
- `starter/references/rules/_template.md` - Individual rule template

See `PLACEHOLDERS.md` for complete placeholder documentation.
See `SKILL-TEMPLATE.md` for the full specification.

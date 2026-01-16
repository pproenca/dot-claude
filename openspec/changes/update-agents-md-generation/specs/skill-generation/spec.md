# Skill Generation Capability

## ADDED Requirements

### Requirement: Automated AGENTS.md Generation

The skill generation workflow SHALL use the `build-agents-md.js` script to compile AGENTS.md from individual rule files. Manual creation of AGENTS.md SHALL NOT be permitted.

#### Scenario: AGENTS.md generated from rules

- **WHEN** the skill generator reaches the "Build AGENTS.md" step
- **THEN** it MUST execute `node scripts/build-agents-md.js <skill-directory>`
- **AND** the generated AGENTS.md MUST reflect all rules in the `rules/` directory
- **AND** the script MUST exit with error if required files are missing (metadata.json, _sections.md)

#### Scenario: Validation detects manual AGENTS.md

- **WHEN** `validate-skill.js --verify-generated` is run on a skill
- **THEN** it MUST compare existing AGENTS.md with freshly generated output
- **AND** report error if content differs (indicating manual edits or stale generation)

### Requirement: Consistent Rule Template Structure

All rule files in `rules/` directory SHALL follow the established template structure to enable automated AGENTS.md generation.

#### Scenario: Rule file structure validated

- **WHEN** a rule file is parsed by build-agents-md.js
- **THEN** it MUST have YAML frontmatter with `title`, `impact`, `impactDescription`, and `tags` fields
- **AND** the markdown body MUST start with `## {title}` heading matching frontmatter title

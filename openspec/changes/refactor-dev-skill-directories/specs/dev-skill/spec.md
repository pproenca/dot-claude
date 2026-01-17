## ADDED Requirements

### Requirement: Generated Skill Directory Structure

Generated skills SHALL use the following directory structure:
- `references/` for rule documentation files (e.g., `async-parallel.md`)
- `references/_sections.md` for category definitions
- `assets/templates/` for scaffolding files (e.g., `_template.md`)
- `SKILL.md`, `AGENTS.md`, `metadata.json`, `README.md` at root

#### Scenario: Skill generation creates correct directories
- **WHEN** a new skill is generated via `/dev-skill:new`
- **THEN** rule files are placed in `references/` directory
- **AND** template files are placed in `assets/templates/` directory
- **AND** `_sections.md` is placed in `references/`

### Requirement: Markdown Links in SKILL.md

Generated SKILL.md files SHALL use markdown link format `[text](path)` for all file references.

#### Scenario: SKILL.md contains navigable links
- **WHEN** SKILL.md is generated
- **THEN** references to rule files use format `[rule-name](references/rule-name.md)`
- **AND** references to AGENTS.md use format `[AGENTS.md](AGENTS.md)`
- **AND** a "Reference Files" section lists key file links

### Requirement: Markdown Links in AGENTS.md

Generated AGENTS.md files SHALL include a "Source Files" footer section with markdown links to source files.

#### Scenario: AGENTS.md contains source file links
- **WHEN** AGENTS.md is generated via build-agents-md.js
- **THEN** a "Source Files" section is appended
- **AND** it includes links to `references/_sections.md`
- **AND** it includes links to `assets/templates/_template.md`

## MODIFIED Requirements

### Requirement: build-agents-md.js Path Configuration

The build-agents-md.js script SHALL look for rule files in `references/` directory instead of `rules/`.

#### Scenario: Build script reads from references directory
- **WHEN** build-agents-md.js is invoked on a skill directory
- **THEN** it looks for `_sections.md` in `references/`
- **AND** it reads rule files from `references/{prefix}-{slug}.md`
- **AND** it generates AGENTS.md with correct relative links

# Change: Refactor dev-skill Generated Output Structure

## Why

The current `dev-skill` plugin generates skills with confusing directory naming:
- Generated skills use `rules/` for rule files, but `references/` is more descriptive for documentation meant to guide agents
- Templates like `_sections.md.template` and `_template.md` are not separated from the actual references
- Generated `SKILL.md` and `AGENTS.md` don't use markdown links to reference supporting files, making navigation harder for both humans and agents

Clarifying the output structure will make generated skills more intuitive and improve discoverability of resources.

## What Changes

1. **Generated skill output uses `references/` instead of `rules/`**
   - Rule files like `async-parallel.md` go in `references/` instead of `rules/`
   - This is about the OUTPUT of the dev-skill plugin, not the plugin itself

2. **Generated skills include `assets/templates/` directory**
   - Scaffolding files (`_sections.md`, `_template.md`) move to `assets/templates/`
   - Clear separation between reference docs and scaffolding templates

3. **Update SKILL.md template to use markdown links**
   - Change from plain text references to `[text](path)` links
   - E.g., `[_sections.md](references/_sections.md)` with proper link format

4. **Update build-agents-md.js to generate markdown links**
   - Generated AGENTS.md includes links to source reference files
   - Makes navigation explicit for agents

5. **Update all templates and commands to reflect new output structure**
   - `templates/skill-generator/*.template` files updated
   - `commands/new.md` updated with new paths

## Impact

- Affected files:
  - `plugins/dev-skill/templates/skill-generator/SKILL.md.template`
  - `plugins/dev-skill/templates/skill-generator/AGENTS.md.template`
  - `plugins/dev-skill/templates/skill-generator/_sections.md.template`
  - `plugins/dev-skill/templates/skill-generator/_template.md.template`
  - `plugins/dev-skill/scripts/build-agents-md.js`
  - `plugins/dev-skill/commands/new.md`
  - `plugins/dev-skill/references/README.md`
- **Output change**: Generated skills will use `references/` and `assets/templates/` instead of `rules/`
- The plugin's own `references/rules/` directory may also be renamed to match

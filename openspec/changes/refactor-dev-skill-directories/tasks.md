# Tasks

## 1. Update Templates for New Output Structure

- [x] 1.1 Update `templates/skill-generator/SKILL.md.template`:
  - Change `rules/` references to `references/`
  - Add markdown links: `[filename](path)` format
  - Add "Reference Files" section with links to key files
- [x] 1.2 Update `templates/skill-generator/_sections.md.template`:
  - No path changes needed (content stays same, just location changes in output)
- [x] 1.3 Update `templates/skill-generator/_template.md.template`:
  - No content changes needed (moves to `assets/templates/` in output)
- [x] 1.4 Update `templates/skill-generator/AGENTS.md.template`:
  - Add "Source Files" footer section with markdown links
  - Reference `references/_sections.md` and `assets/templates/_template.md`

## 2. Update Build Script

- [x] 2.1 Update `build-agents-md.js` path constants:
  - Change `rulesDir` from `rules/` to `references/`
  - Look for `_sections.md` in `references/` instead of `rules/`
  - Added backwards compatibility: falls back to `rules/` if `references/` not found
- [x] 2.2 Add footer generation to AGENTS.md output:
  - Include "Source Files" section with links
  - Generate links to all rule files used

## 3. Update Command Documentation

- [x] 3.1 Update `commands/new.md` output structure section:
  - Change `rules/` to `references/` in directory tree
  - Add `assets/templates/` directory
  - Update all path examples
- [x] 3.2 Update file generation templates section:
  - Show new SKILL.md with markdown links
  - Show new directory structure

## 4. Update Plugin's Own References (to match output pattern)

- [x] 4.1 Rename `references/rules/` to `references/examples/`
- [x] 4.2 Update `references/README.md` with new paths
- [x] 4.3 Update `references/QUALITY_CHECKLIST.md` path references

## 5. Update Validation Script

- [x] 5.1 Update `scripts/validation/validator.js` to support both `references/` and `rules/`
- [x] 5.2 Update `scripts/validation/constants.js` error messages

## 6. Validation

- [x] 6.1 Run `make check` to verify all validations pass
- [x] 6.2 Run bats tests to verify functionality
- [x] 6.3 Verify markdown links in generated files resolve correctly

## Dependencies

- Task 2 depends on Task 1 (build script uses template patterns)
- Task 4 can run in parallel with Tasks 1-3
- Task 6 depends on all previous tasks

# Tasks

## 1. Verify Current Script Functionality

- [x] 1.1 Test `build-agents-md.js` with reference skill to confirm output matches expected format
- [x] 1.2 Verify script handles all YAML frontmatter fields correctly (`title`, `impact`, `impactDescription`, `tags`)
- [x] 1.3 Confirm script correctly parses `_sections.md` format (section headers, impact, description)

## 2. Update Command Documentation

- [x] 2.1 Update `commands/new.md` Step 4 to explicitly mandate script usage (no manual AGENTS.md writing)
- [x] 2.2 Add error handling guidance if script fails (missing metadata.json, malformed _sections.md)

## 3. Add Validation Check

- [x] 3.1 Add optional `--verify-generated` flag to `validate-skill.js` that checks AGENTS.md matches what script would produce
- [x] 3.2 Document the validation flag in `scripts/README.md`

## 4. Structure Fix (discovered during implementation)

- [x] 4.1 Move `references/_sections.md` to `references/rules/_sections.md` to match expected skill structure
- [x] 4.2 Move `references/_template.md` to `references/rules/_template.md` to match expected skill structure

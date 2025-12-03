---
description: Validate Claude Code extensions in home or project directory
allowed-tools: AskUserQuestion, Bash, Read, Glob, Grep, TodoWrite
---

# Claude Code Extension Validation

Ask the user where they want to run the validation:

<AskUserQuestion>
Which Claude Code configuration would you like to validate?

Options:

1. **Home Configuration** (~/.claude) - Validates your global Claude Code extensions
2. **Project Configuration** (./.claude) - Validates extensions in the current project
3. **Both** - Validates both home and project configurations

</AskUserQuestion>

Based on their selection, validate all Claude Code extensions are working correctly at the chosen location(s):

## Validation Checklist

For each location, test and verify:

### 1. Plugin Discovery

- Scan for all installed plugins
- Verify plugin.json files are valid
- Check plugin metadata (name, version, description)

### 2. Skills Validation

- Test each skill is accessible via the Skill tool
- Verify SKILL.md files are properly formatted with valid YAML frontmatter
- Check `allowed-tools` restrictions are valid
- Confirm skills execute their documented workflows

### 3. Hooks Validation

- Verify hooks.json configuration is valid
- Test hooks trigger at correct lifecycle points:
  - SessionStart hooks fire on conversation start
  - PreToolUse hooks fire before tool execution
  - PostToolUse hooks fire after tool execution
  - Stop hooks fire on conversation end
- Confirm hook scripts (.sh, .py) exist and are executable
- Check hooks return proper JSON responses

### 4. Agents Validation

- Verify agent markdown files exist and are readable
- Test agents respond when invoked via Task tool
- Confirm agent descriptions match their capabilities

### 5. Commands Validation

- Verify command markdown files exist in commands/ directories
- Test slash commands expand to their documented prompts
- Check command frontmatter is valid (description, allowed-tools)

### 6. Scripts Validation

- Test any validation or utility scripts run without errors
- Verify script dependencies are available
- Check script permissions are correct

### 7. Settings.json Validation

- Scan all settings.json locations:
  - Global: ~/.claude/settings.json
  - Project shared: ./.claude/settings.json
  - Project local: ./.claude/settings.local.json
  - Enterprise managed (if present): /Library/Application Support/ClaudeCode/managed-settings.json (macOS)
- Validate JSON syntax
- Check permission pattern references (Bash(*), Skill(*))
- Verify tool/skill references exist
- Test command executability (statusLine)
- Detect permission conflicts
- Validate hooks.json schema in all plugins

## Validation Process

1. **Run automated validation script first** (if in project with scripts/validate-settings.py):

   ```bash
   uv run python -S scripts/validate-settings.py
   ```

   - This will catch plugin reference mismatches quickly
   - Check for errors about plugins "not found in marketplace"

2. **Check and fix plugin reference mismatches**:

   ```bash
   uv run python -S scripts/fix-plugin-references.py
   ```

   - This script will:
     - Scan actual plugins in the project
     - Compare with plugins referenced in ~/.claude/settings.json
     - Report any mismatches (plugins in settings but not in project)
     - Offer to automatically fix by removing non-existent plugin references
   - Removes from both `enabledPlugins` and `permissions.allow` Skill() patterns
   - If errors found and fixed, re-run validation to confirm

3. Create a TodoWrite checklist with all validation items (including settings.json validation)

4. For each component:
   - Test functionality
   - Verify file format and accessibility
   - Check for errors or warnings
   - Document any failures
   - For settings.json files:
     - Verify permission patterns reference existing skills/tools
     - Test statusLine command executability
     - Report conflicts and invalid references

5. Flag any failures or unexpected behavior immediately

6. Provide a summary report with:
   - Total components tested
   - Passed vs failed validations
   - Detailed failure descriptions
   - Recommended fixes or applied fixes

## Success Criteria

All components must:

- Be accessible and properly formatted
- Execute without errors
- Trigger at expected points (for hooks)
- Match documented behavior
- Pass format validation

Settings.json files must:

- Parse as valid JSON
- Reference only existing skills/plugins/tools in permission patterns
- Have executable commands in statusLine configuration
- Have no conflicting permission rules

Confirm all components are stable before marking validation complete.

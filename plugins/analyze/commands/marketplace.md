---
description: Analyze plugins in the marketplace for quality, DX, and improvements
argument-hint: "[plugin-name]"
allowed-tools: [Read, Glob, Grep, Bash, Task, Skill, TodoWrite, Edit]
---

Analyze plugins in the marketplace to identify quality improvements.

**Scope:**
- If no argument provided, analyze all plugins in `plugins/` directory
- If plugin name provided ($ARGUMENTS), analyze only that plugin

**Process:**

1. **Load the methodology:**
   Use `Skill` tool with `skill: "analyze:marketplace-analysis"`

2. **Analyze the plugin(s):**
   Read all plugin components (skills, agents, commands, hooks) and apply the methodology.

3. **Present findings** as prioritized actionable todos with validation approach for each.

4. **If user requests changes:**
   - Apply improvements using Edit tool
   - **MANDATORY:** Use `Skill` tool with `skill: "super:verification-before-completion"` before claiming changes are complete
   - Run validation commands and report evidence

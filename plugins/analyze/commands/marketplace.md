---
description: Analyze plugins in the marketplace for quality, DX, and improvements
argument-hint: [plugin-name]
---

Analyze plugins in the marketplace to identify quality improvements.

**Scope:**
- If no argument provided, analyze all plugins in `plugins/` directory
- If plugin name provided ($1), analyze only that plugin

**Process:**

1. **Load the methodology:**
   Use the `marketplace-analysis` skill.

2. **Launch the orchestrator:**
   Use Task tool with `subagent_type='marketplace-orchestrator'` to coordinate analysis.

3. **Present findings** as prioritized actionable todos with validation approach for each.

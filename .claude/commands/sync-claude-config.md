---
description: Sync hookify, statusline, and settings between project and home ~/.claude/
---

Sync Claude configuration files between this project's `.claude/` directory and the user's home `~/.claude/` directory.

## Steps

1. **Compare files** between project `.claude/` and `~/.claude/`:
   - List all `hookify.*.local.md` files in both locations
   - Compare `statusline.sh` contents
   - Compare `settings.json` (note differences in permissions, plugins, etc.)

2. **Ask user for sync direction** using AskUserQuestion:
   - "Project -> Home" (copy project files to ~/.claude/)
   - "Home -> Project" (copy home files to project)
   - "Merge both" (combine settings intelligently)

3. **For settings.json, ask about merge strategy** if applicable:
   - "Merge intelligently" (preserve plugins, combine permissions)
   - "Full overwrite" (replace entirely)
   - "Skip settings.json" (only sync other files)

4. **Execute the sync**:
   - Copy statusline.sh to target and make it executable (`chmod +x`)
   - Copy hookify files to target
   - Merge or copy settings.json based on user choice

5. **Report what was synced** and any conflicts resolved.

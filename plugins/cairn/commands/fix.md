---
description: Fix a bounded bug — failing repro first, then make it pass for good.
argument-hint: [what's broken]
---
Engage fix-workflow for: $ARGUMENTS
Write a RED repro that captures the bug before the fix, make it GREEN, leave it
as a permanent regression lock. Fix the root cause at the right boundary.

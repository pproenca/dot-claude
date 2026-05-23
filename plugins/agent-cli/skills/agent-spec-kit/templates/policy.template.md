# <Policy Name>

<One-sentence statement of what this policy governs and its risk posture, e.g.
"Merging is higher risk than closure. Prefer non-mutating classification unless the
merge path is obvious.">

## When this policy applies (gate)
Use this policy only when <explicit condition>. It is not the default <X> policy.

## <Decision> only when
- <positive criterion 1>
- <positive criterion 2>
- a comment was posted first and preserves credit + a reopen path
- the action is allowed by the job frontmatter

## Evidence order (ranked)
1. <live preflight artifact>
2. <bodies / comments / discussion>
3. <diffs>
4. <CI / mergeability state>
5. <cluster / cross-item notes>

Do not act on <title similarity / red CI> alone.

## Comment shapes (literal templates — output style is data)
**Default <action> comment:**
```
<exact markdown to post, including credit wording such as "Thanks @user" and a reopen
invitation>
```

## Never <act> when
- <hard exclusion 1>
- <hard exclusion 2>
- the item is maintainer-authored or carries a protected label

## Escalation
- `route_security` — quarantine only the affected item with a non-mutating action; keep
  classifying unrelated items; route to central security handling.
- `needs_human` — only when the unresolved decision genuinely needs a maintainer. Do not
  use `needs_human` as a synonym for "not actionable."

## Required proof (for mutating actions)
Every <merge/close> action must include `<preflight>` proving <security cleared,
checks passed, findings addressed, target_updated_at present>. Missing proof blocks the action.

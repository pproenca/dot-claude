#!/usr/bin/env bash
# Surfaces in-flight squad stories and pending gates when a session starts in a
# repository that has been initialised with /swarmforge:squad-init.
# Silent and successful when there is no .squad/ or no python3.
set -uo pipefail

root="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$root/.squad/stories" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 - "$root" <<'PY'
import json, pathlib, sys

root = pathlib.Path(sys.argv[1])
stories, gates, blocked = [], [], []

for state_file in sorted((root / ".squad" / "stories").glob("*/state.json")):
    try:
        state = json.loads(state_file.read_text())
    except (OSError, ValueError):
        continue
    stages = state.get("stages") or []
    done = state.get("completed") or []
    if len(done) >= len(stages) and stages:
        continue
    sid = state.get("story_id", state_file.parent.name)
    stories.append(f"  {sid} — {state.get('stage', '?')} ({len(done)}/{len(stages)} stages)")
    for gate, status in (state.get("gates") or {}).items():
        if status == "pending":
            gates.append(f"  {sid} — {gate} gate awaiting a decision")
    if state.get("blocked"):
        blocked.append(f"  {sid} — {state['blocked']}")

if not stories:
    sys.exit(0)

print("SwarmForge: stories in flight")
print("\n".join(stories))
if gates:
    print("Pending gates (run /swarmforge:squad-approve):")
    print("\n".join(gates))
if blocked:
    print("Blocked:")
    print("\n".join(blocked))
print("Board: /swarmforge:squad-status")
PY

exit 0

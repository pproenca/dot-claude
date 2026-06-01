#!/usr/bin/env python3
"""The knowledge ratchet: turn recurring friction into durable fixes.

The inner loop (feature-workflow) ships features; this outer loop improves the
harness itself. Each time something rubs — a scanner false-positive, a primitive
reused a third time, a boundary misplaced the same way twice — you log an
observation here. The ratchet counts recurrences and tells you what's RIPE to
promote, so a one-off annoyance and a real pattern are treated differently.

Two ripeness rules, because they are different things:
- **defect** — something is simply wrong (a false-positive, a broken check). One
  observation is enough; fix on sight. The Rule of Three does NOT gate defects.
- **abstraction** — a candidate generalization (a shared primitive, a new skill,
  a lint rule). Gated by the Rule of Three: ripe at 3 occurrences, because
  extracting earlier risks the wrong abstraction.

Storage: ratchet.jsonl at the repo root, one record per friction key. The log is
inherently small (frictions are rare), so it is a plain JSONL — no storage port,
no search; that machinery would be anticipation, not evidence.

Usage:
    ratchet.py --observe "<friction>" --key <slug> [--kind defect|abstraction] [--where <loc>]
    ratchet.py --status        # all frictions, counts, ripeness
    ratchet.py --ripe          # only what's actionable now (gate-able: exit 1 if any unpromoted-ripe)
    ratchet.py --promote <key> --as <sink> --landed <where>   # record the durable fix
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path

RULE_OF_THREE = 3
SINKS = ["convention", "reference", "scan-pattern", "lint-rule", "type-constraint", "skill"]


def store_path(repo: Path) -> Path:
    return repo / "ratchet.jsonl"


def load(repo: Path) -> dict[str, dict]:
    p = store_path(repo)
    out: dict[str, dict] = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("key"):
            out[r["key"]] = r
    return out


def save(repo: Path, records: dict[str, dict]) -> None:
    lines = [json.dumps(records[k], ensure_ascii=False) for k in sorted(records)]
    store_path(repo).write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_ripe(r: dict) -> bool:
    if r.get("status") == "promoted":
        return False
    if r.get("kind") == "defect":
        return len(r.get("occurrences", [])) >= 1
    return len(r.get("occurrences", [])) >= RULE_OF_THREE


def do_observe(repo: Path, friction: str, key: str, kind: str, where: str | None) -> int:
    recs = load(repo)
    r = recs.get(key) or {"key": key, "friction": friction, "kind": kind,
                          "occurrences": [], "status": "open"}
    r["friction"] = friction or r["friction"]
    r["kind"] = kind or r.get("kind", "abstraction")
    stamp = where or _dt.date.today().isoformat()
    if stamp not in r["occurrences"]:
        r["occurrences"].append(stamp)
    if r["status"] != "promoted":
        r["status"] = "ripe" if is_ripe(r) else "open"
    recs[key] = r
    save(repo, recs)
    n = len(r["occurrences"])
    tag = "RIPE" if is_ripe(r) else f"{n}/{RULE_OF_THREE}" if r["kind"] == "abstraction" else "open"
    print(f"logged '{key}' ({r['kind']}): {n} occurrence(s) [{tag}]")
    return 0


def render(r: dict) -> str:
    n = len(r.get("occurrences", []))
    if r.get("status") == "promoted":
        state = f"PROMOTED -> {r.get('resolution_sink')} ({r.get('landed_in')})"
    elif is_ripe(r):
        state = "RIPE — promote it"
    else:
        state = f"{n}/{RULE_OF_THREE}" if r.get("kind") == "abstraction" else "open"
    return f"  [{state}] {r['key']} ({r.get('kind')}) — {r.get('friction')}  · seen: {', '.join(r.get('occurrences', []))}"


def do_status(repo: Path, ripe_only: bool) -> int:
    recs = load(repo)
    if not recs:
        print("ratchet log is empty — nothing recorded yet.")
        return 0
    items = [r for r in recs.values() if (is_ripe(r) if ripe_only else True)]
    if ripe_only and not items:
        print("nothing ripe — no durable fix is owed right now.")
        return 0
    print("ripe (actionable now):" if ripe_only else "ratchet log:")
    for r in sorted(items, key=lambda x: (x.get("status") == "promoted", x["key"])):
        print(render(r))
    unpromoted_ripe = [r for r in recs.values() if is_ripe(r)]
    return 1 if (ripe_only and unpromoted_ripe) else 0


def do_promote(repo: Path, key: str, sink: str, landed: str) -> int:
    recs = load(repo)
    r = recs.get(key)
    if not r:
        print(f"no friction '{key}' logged.")
        return 2
    if sink not in SINKS:
        print(f"sink must be one of: {', '.join(SINKS)}")
        return 2
    if not is_ripe(r):
        print(f"friction '{key}' is not ripe yet; promotion is owed only for defects or abstractions at the Rule of Three.")
        return 2
    r["status"] = "promoted"
    r["resolution_sink"] = sink
    r["landed_in"] = landed
    r["promoted_on"] = _dt.date.today().isoformat()
    recs[key] = r
    save(repo, recs)
    print(f"promoted '{key}' -> {sink} ({landed}). Friction closed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The knowledge ratchet — recurring friction -> durable fix.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--observe", default=None, help="Describe the friction.")
    ap.add_argument("--key", default=None, help="Short slug identifying the friction.")
    ap.add_argument("--kind", default="abstraction", choices=["defect", "abstraction"])
    ap.add_argument("--where", default=None, help="Where it was seen this time.")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--ripe", action="store_true")
    ap.add_argument("--promote", default=None, help="Friction key to mark promoted.")
    ap.add_argument("--as", dest="sink", default=None, help=f"Resolution sink: {', '.join(SINKS)}")
    ap.add_argument("--landed", default=None, help="Where the durable fix lives.")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.observe:
        if not args.key:
            print("--observe requires --key"); return 2
        return do_observe(repo, args.observe, args.key, args.kind, args.where)
    if args.promote:
        return do_promote(repo, args.promote, args.sink or "", args.landed or "")
    if args.ripe:
        return do_status(repo, ripe_only=True)
    if args.status:
        return do_status(repo, ripe_only=False)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

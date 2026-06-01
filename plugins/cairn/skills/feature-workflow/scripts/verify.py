#!/usr/bin/env python3
"""The verify gate (STAGE 1.5). Manufacture trust BEFORE ship.

Structural twin of plan_check.py: plan_check gates code on a complete plan; this
gates ship on a passing build. It closes the inner feedback loop the whole
harness rests on — generate, run, READ THE ERROR, fix — by running the project's
verification checks and refusing to green-light a ship until the gating ones
pass. Failures route back to STAGE 1 (build), never forward to ship.

This is a generic check RUNNER. It does not know your stack; the checks live in
config so any project can plug in its own typecheck / test / lint / perf / scan
commands. The mechanism (run, aggregate, gate, surface errors) is general.

Two principles baked in:
  - Fail closed. A check that cannot run (command not found, timeout) is a gate
    FAILURE, not a pass. "Couldn't verify" is not "safe to ship".
  - Gating vs report-only. `must_pass` checks (typecheck, tests) gate the ship.
    Report-only checks (e.g. the boundary scan, which surfaces candidates for
    judgment) run and print but never block on their own.

Config: boundary.config.json -> "verify": [ {name, cmd, must_pass?, timeout?} ].
If absent, a minimal TS default set is used and clearly flagged.

Usage:
    python verify.py                 # run all checks in ./boundary.config.json
    python verify.py --repo ../app
    python verify.py --only typecheck tests
    python verify.py --json

Exit codes: 0 = gate passed (all must_pass checks green), 1 = gate failed,
2 = usage/config error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_CHECKS = [
    {"name": "typecheck", "cmd": "npx --no-install tsc --noEmit", "must_pass": True},
    {"name": "tests", "cmd": "npm test --silent", "must_pass": True},
]
DEFAULT_TIMEOUT = 300
MAX_OUTPUT_LINES = 40  # truncation for the failure report the agent reads


def load_checks(repo: Path, path: str | None) -> tuple[list[dict], bool]:
    cfg_path = Path(path) if path else repo / "boundary.config.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            checks = data.get("verify")
            if checks:
                return checks, False
        except (json.JSONDecodeError, OSError) as e:
            print(f"warning: ignoring unreadable config {cfg_path}: {e}", file=sys.stderr)
    return list(DEFAULT_CHECKS), True


def run_check(check: dict, repo: Path) -> dict:
    name = check.get("name", check.get("cmd", "unnamed"))
    cmd = check.get("cmd")
    must_pass = bool(check.get("must_pass", True))
    timeout = int(check.get("timeout", DEFAULT_TIMEOUT))
    if not cmd:
        return {"name": name, "status": "ERROR", "must_pass": must_pass,
                "detail": "check has no 'cmd'", "output": "", "seconds": 0.0}

    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, shell=True, cwd=str(repo), capture_output=True,
                              text=True, timeout=timeout)
        secs = round(time.monotonic() - start, 1)
        output = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0:
            status = "PASS"
        elif proc.returncode == 127:
            status = "ERROR"  # command not found -> fail closed
        else:
            status = "FAIL"
        return {"name": name, "status": status, "must_pass": must_pass,
                "rc": proc.returncode, "output": output, "seconds": secs,
                "detail": "command not found (rc 127) — configure this check"
                          if status == "ERROR" else ""}
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "ERROR", "must_pass": must_pass,
                "detail": f"timed out after {timeout}s", "output": "",
                "seconds": round(time.monotonic() - start, 1)}
    except OSError as e:
        return {"name": name, "status": "ERROR", "must_pass": must_pass,
                "detail": str(e), "output": "", "seconds": 0.0}


def truncate(output: str) -> str:
    lines = output.rstrip().splitlines()
    if len(lines) <= MAX_OUTPUT_LINES:
        return "\n".join(lines)
    head = lines[: MAX_OUTPUT_LINES - 5]
    tail = lines[-5:]
    return "\n".join(head + [f"... ({len(lines) - MAX_OUTPUT_LINES} lines elided) ..."] + tail)


def gate(results: list[dict]) -> bool:
    """Pass iff every must_pass check is PASS. ERROR on a must_pass check fails closed."""
    return all(r["status"] == "PASS" for r in results if r["must_pass"])


def render(results: list[dict], used_defaults: bool) -> str:
    out: list[str] = []
    if used_defaults:
        out.append("(no `verify` config found — using TS defaults; add a `verify` "
                   "array to boundary.config.json for your real checks)\n")
    icon = {"PASS": "PASS ", "FAIL": "FAIL ", "ERROR": "ERROR"}
    for r in results:
        tag = "" if r["must_pass"] else "  (report-only)"
        line = f"  [{icon[r['status']]}] {r['name']}{tag}"
        if r.get("seconds"):
            line += f"  ({r['seconds']}s)"
        if r.get("detail"):
            line += f"  — {r['detail']}"
        out.append(line)

    passed = gate(results)
    out.append("")
    # Show captured output for failing/erroring checks so the loop can act on it.
    actionable = [r for r in results if r["status"] in ("FAIL", "ERROR") and r["must_pass"]]
    for r in actionable:
        if r.get("output", "").strip():
            out.append(f"--- output: {r['name']} ({r['status']}) ---")
            out.append(truncate(r["output"]))
            out.append("")

    if passed:
        out.append("VERIFY GATE PASSED — all gating checks green. Proceed to STAGE 2 (ship & record).")
        report_only_issues = [r for r in results if not r["must_pass"] and r["status"] != "PASS"]
        if report_only_issues:
            out.append("Note: report-only checks flagged items above — judge whether any "
                       "is a real gap before shipping (they did not block the gate).")
    else:
        failed = [r["name"] for r in results if r["must_pass"] and r["status"] != "PASS"]
        out.append(f"VERIFY GATE FAILED — gating check(s) not green: {', '.join(failed)}.")
        out.append("Route back to STAGE 1 (build): fix, then re-run verify. Do not ship.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="The verify gate: run checks, gate the ship.")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--config", default=None, help="Path to boundary.config.json.")
    p.add_argument("--only", nargs="+", default=None, help="Run only these named checks.")
    p.add_argument("--json", action="store_true", help="Emit results as JSON.")
    args = p.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"error: repo {repo} not found", file=sys.stderr)
        return 2

    checks, used_defaults = load_checks(repo, args.config)
    if args.only:
        wanted = set(args.only)
        checks = [c for c in checks if c.get("name") in wanted]
        if not checks:
            print(f"error: none of {sorted(wanted)} matched configured checks", file=sys.stderr)
            return 2

    results = [run_check(c, repo) for c in checks]
    passed = gate(results)

    if args.json:
        print(json.dumps({"passed": passed, "results": results}, indent=2))
    else:
        print(render(results, used_defaults))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

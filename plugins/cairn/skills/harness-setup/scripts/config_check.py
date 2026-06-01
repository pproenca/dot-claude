#!/usr/bin/env python3
"""The doctor. Validate that boundary.config.json actually resolves against THIS repo.

The config is the trust boundary of the whole harness: every script (scan,
shelf_index, promote, verify) reads it and ASSUMES it is correct. A wrong config
fails silently — shelf_index returns empty, the shelf-check ungrounds, and
duplication sneaks back. This is the boot-time parse that turns those silent
wrong answers into a loud, located failure before any stage runs.

Structural twin of plan_check.py / verify.py: it fails closed and reports a
precise punch-list. ERRORs gate (the config won't work); WARNs inform (likely
misconfig, but possibly intentional).

Checks:
  1. config exists and is valid JSON.
  2. include_ext is a non-empty list of extension-like strings.
  3. each layer's globs resolve to >=1 path (a layer matching NOTHING is a WARN).
  4. feature_roots resolve (WARN if none, since promote.py uses them).
  5. verify[] entries are well-formed; any script-file path referenced in a cmd
     exists (ERROR if missing); placeholder paths like /PATH/TO are ERRORs.

Usage:
    python config_check.py                 # checks ./boundary.config.json
    python config_check.py --repo ../app
    python config_check.py --json

Exit: 0 = resolves (no errors), 1 = errors found, 2 = no config / usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXT_RE = re.compile(r"^\.[A-Za-z0-9.]+$")
PLACEHOLDER_RE = re.compile(r"/(?:ABSOLUTE/)?PATH/TO\b|<[^>]+>|/path/to\b", re.IGNORECASE)
SCRIPT_PATH_RE = re.compile(r"(/[^\s\"']+\.(?:py|sh|js|mjs|cjs))")


def add(problems, level, msg):
    problems.append((level, msg))


def check(repo: Path, cfg_path: Path) -> tuple[list[tuple[str, str]], dict | None]:
    problems: list[tuple[str, str]] = []
    if not cfg_path.exists():
        add(problems, "ERROR", f"no config at {cfg_path}. Run config_init.py to scaffold one.")
        return problems, None
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        add(problems, "ERROR", f"config is not valid JSON: {e}")
        return problems, None
    if not isinstance(cfg, dict):
        add(problems, "ERROR", "config must be a JSON object.")
        return problems, None

    # 2. include_ext
    exts = cfg.get("include_ext")
    if not isinstance(exts, list) or not exts:
        add(problems, "WARN", "include_ext missing/empty — scripts will use defaults.")
    else:
        for e in exts:
            if not isinstance(e, str) or not EXT_RE.match(e):
                add(problems, "ERROR", f"include_ext has a non-extension value: {e!r}")

    # 3. layers
    layers = cfg.get("layers") or {}
    if not layers:
        add(problems, "WARN", "no `layers` configured — shelf_index cannot inventory the substrate.")
    for layer, globs in layers.items():
        if not isinstance(globs, list) or not globs:
            add(problems, "ERROR", f"layer '{layer}' has no globs.")
            continue
        matched = 0
        for g in globs:
            try:
                matched += sum(1 for _ in repo.glob(g))
            except (ValueError, OSError):
                add(problems, "ERROR", f"layer '{layer}' has an invalid glob: {g!r}")
        if matched == 0:
            add(problems, "WARN", f"layer '{layer}' matches 0 files — check the globs "
                                  f"({', '.join(globs)}).")

    # 4. feature_roots
    froots = cfg.get("feature_roots") or []
    if not froots:
        add(problems, "WARN", "no `feature_roots` — promote.py leak-detection will be weaker.")
    else:
        if not any(sum(1 for _ in repo.glob(fr)) for fr in froots):
            add(problems, "WARN", f"feature_roots match 0 paths: {', '.join(froots)}.")

    # 5. verify[]
    verify = cfg.get("verify") or []
    if not verify:
        add(problems, "WARN", "no `verify` checks — the STAGE 1.5 gate will fall back to TS defaults.")
    for i, chk in enumerate(verify):
        if not isinstance(chk, dict) or "cmd" not in chk:
            add(problems, "ERROR", f"verify[{i}] is missing a 'cmd'.")
            continue
        cmd = chk["cmd"]
        name = chk.get("name", f"verify[{i}]")
        if PLACEHOLDER_RE.search(cmd):
            add(problems, "ERROR", f"check '{name}' has a placeholder path — fill it in: {cmd}")
        for sp in SCRIPT_PATH_RE.findall(cmd):
            if not Path(sp).exists():
                add(problems, "ERROR", f"check '{name}' references a script that does not exist: {sp}")

    return problems, cfg


def render(problems, cfg, cfg_path) -> str:
    errors = [m for lvl, m in problems if lvl == "ERROR"]
    warns = [m for lvl, m in problems if lvl == "WARN"]
    out = [f"Config doctor: {cfg_path}"]
    if cfg is not None:
        layers = cfg.get("layers") or {}
        out.append(f"  layers: {len(layers)} | verify checks: {len(cfg.get('verify') or [])} | "
                   f"feature_roots: {len(cfg.get('feature_roots') or [])}")
    out.append("")
    for m in errors:
        out.append(f"  [ERROR] {m}")
    for m in warns:
        out.append(f"  [WARN]  {m}")
    out.append("")
    if errors:
        out.append(f"DOCTOR FAILED — {len(errors)} error(s). The harness will not work correctly "
                   f"until these are fixed.")
    elif warns:
        out.append(f"DOCTOR PASSED with {len(warns)} warning(s) — usable, but review the warnings.")
    else:
        out.append("DOCTOR PASSED — config resolves cleanly against the repo.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate boundary.config.json against the repo (the doctor).")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--config", default=None, help="Path to config (default: <repo>/boundary.config.json).")
    p.add_argument("--json", action="store_true", help="Emit results as JSON.")
    args = p.parse_args(argv)

    repo = Path(args.repo).resolve()
    cfg_path = Path(args.config).resolve() if args.config else repo / "boundary.config.json"
    problems, cfg = check(repo, cfg_path)
    errors = [m for lvl, m in problems if lvl == "ERROR"]

    if args.json:
        print(json.dumps({
            "config": str(cfg_path),
            "errors": [m for lvl, m in problems if lvl == "ERROR"],
            "warnings": [m for lvl, m in problems if lvl == "WARN"],
            "passed": not errors,
        }, indent=2))
    else:
        print(render(problems, cfg, cfg_path))

    if cfg is None:
        return 2
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

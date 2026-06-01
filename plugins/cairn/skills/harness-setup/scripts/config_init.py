#!/usr/bin/env python3
"""Detect the repo's stack and layout, then scaffold a DRAFT boundary.config.json.

This handles the mechanical half of setup: read package.json scripts, detect the
package manager, find which conventional directories actually exist, and resolve
the sibling-skill script paths. It writes a best-effort draft and prints a
confidence report flagging what was detected vs guessed vs needs a human.

The JUDGMENT half — confirming the layer->directory mapping encodes the repo's
real architecture — is the harness-setup skill's job (a human/agent ratifies the
draft). Always finish by running config_check.py to prove the result resolves.

Mirrors plan_new.py: it scaffolds; the doctor validates.

Usage:
    python config_init.py --repo .
    python config_init.py --repo ../app --skills-root ~/.claude/skills
    python config_init.py --force            # overwrite an existing config
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Conventional directories to probe per layer, in priority order.
LAYER_PROBES = {
    "atomic":    ["src/ui/tokens", "src/tokens", "src/design-tokens",
                  "src/domain/value-objects", "src/domain/values"],
    "primitive": ["src/ui/components", "src/components", "components", "src/ui/primitives"],
    "seam":      ["src/ports", "src/hooks", "src/providers", "src/adapters"],
    "pattern":   ["src/ui/patterns", "src/patterns", "src/features/_shared"],
    "pipeline":  ["src/usecases", "src/application", "src/use-cases", "src/services"],
    "scaffold":  ["src/layouts", "app", "src/app"],
}
FEATURE_PROBES = ["src/features", "src/modules", "src/domains", "features"]
LOCKFILES = {"pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn", "bun.lockb": "bun",
             "package-lock.json": "npm"}


def detect_pm(repo: Path) -> str:
    for lock, pm in LOCKFILES.items():
        if (repo / lock).exists():
            return pm
    return "npm"


def detect_exts(repo: Path) -> list[str]:
    found = set()
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        if next(repo.rglob(f"*{ext}"), None):
            found.add(ext)
    # prefer ts/tsx if present
    if ".ts" in found or ".tsx" in found:
        return [e for e in (".ts", ".tsx") if e in found]
    return sorted(found) or [".ts", ".tsx"]


def detect_scripts(repo: Path) -> dict:
    pkg = repo / "package.json"
    if not pkg.exists():
        return {}
    try:
        return json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
    except (json.JSONDecodeError, OSError):
        return {}


def run_cmd(pm: str, script: str) -> str:
    return f"{pm} run {script}" if pm != "npm" else f"npm run {script}"


def build_verify(pm: str, scripts: dict, scan_path: str | None) -> tuple[list[dict], list[str]]:
    checks, notes = [], []
    # typecheck
    if "typecheck" in scripts:
        checks.append({"name": "typecheck", "cmd": run_cmd(pm, "typecheck"), "must_pass": True})
    else:
        checks.append({"name": "typecheck", "cmd": "npx --no-install tsc --noEmit", "must_pass": True})
        notes.append("typecheck: no 'typecheck' script found — defaulted to `tsc --noEmit` (verify it exists).")
    # tests
    if "test" in scripts:
        checks.append({"name": "tests", "cmd": run_cmd(pm, "test"), "must_pass": True})
    else:
        notes.append("tests: no 'test' script found — add a tests check manually.")
    # lint
    if "lint" in scripts:
        checks.append({"name": "lint", "cmd": run_cmd(pm, "lint"), "must_pass": True})
    # boundary scan (report-only)
    if scan_path:
        checks.append({"name": "boundary-scan", "cmd": f"python3 {scan_path} src --json", "must_pass": False})
    else:
        checks.append({"name": "boundary-scan",
                       "cmd": "python3 /ABSOLUTE/PATH/TO/boundary-discipline/scripts/scan.py src --json",
                       "must_pass": False})
        notes.append("boundary-scan: pass --skills-root so I can resolve scan.py, or edit the path. "
                     "(placeholder path will fail the doctor until fixed.)")
    return checks, notes


def find_scan(skills_root: str | None) -> str | None:
    if not skills_root:
        return None
    root = Path(skills_root).expanduser()
    hit = next(root.rglob("boundary-discipline/scripts/scan.py"), None)
    return str(hit) if hit else None


def build_config(repo: Path, skills_root: str | None) -> tuple[dict, list[str]]:
    notes: list[str] = []
    pm = detect_pm(repo)
    exts = detect_exts(repo)
    scripts = detect_scripts(repo)

    layers: dict[str, list[str]] = {}
    for layer, probes in LAYER_PROBES.items():
        hits = [p for p in probes if (repo / p).is_dir()]
        if hits:
            layers[layer] = [f"{h}/**/*" for h in hits]
        else:
            layers[layer] = [f"{probes[0]}/**/*"]
            notes.append(f"layer '{layer}': no conventional dir found — guessed {probes[0]} (REVIEW).")

    froots = [f"{p}/**" for p in FEATURE_PROBES if (repo / p).is_dir()]
    if not froots:
        froots = ["src/features/**"]
        notes.append("feature_roots: none found — guessed src/features (REVIEW).")

    scan_path = find_scan(skills_root)
    if skills_root and not scan_path:
        notes.append(f"could not find boundary-discipline/scripts/scan.py under {skills_root}.")
    verify, vnotes = build_verify(pm, scripts, scan_path)
    notes += vnotes

    cfg = {
        "include_ext": exts,
        "exclude_globs": ["**/node_modules/**", "**/dist/**", "**/build/**",
                          "**/.git/**", "**/*.test.*", "**/*.spec.*", "**/*.d.ts"],
        "layers": layers,
        "feature_roots": froots,
        "verify": verify,
    }
    notes.insert(0, f"package manager: {pm} | extensions: {', '.join(exts)} | "
                    f"package.json scripts: {', '.join(scripts) or 'none'}")
    return cfg, notes


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Detect stack + layout and scaffold a draft boundary.config.json.")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--out", default=None, help="Output path (default: <repo>/boundary.config.json).")
    p.add_argument("--skills-root", default=None, help="Where skills are installed (to resolve scan.py).")
    p.add_argument("--force", action="store_true", help="Overwrite an existing config.")
    args = p.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: repo {repo} not found", file=sys.stderr)
        return 2
    out = Path(args.out).resolve() if args.out else repo / "boundary.config.json"
    if out.exists() and not args.force:
        print(f"error: {out} exists. Use --force to overwrite, or edit it directly.", file=sys.stderr)
        return 1

    cfg, notes = build_config(repo, args.skills_root)
    out.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    print(f"drafted {out}\n")
    print("confidence report (review the REVIEW items — they encode your architecture):")
    for n in notes:
        print(f"  - {n}")
    print(f"\nnext: review/edit the draft, then validate it resolves:")
    print(f"      python {Path(__file__).with_name('config_check.py')} --repo {repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

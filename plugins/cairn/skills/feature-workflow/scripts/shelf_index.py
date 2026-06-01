#!/usr/bin/env python3
"""Inventory the reusable substrate ("the shelf") by layer.

This is the anti-duplication ground truth: it converts the PLAN.md section-3
shelf-check from "the agent recalls what exists" into "the agent matches the
bill of materials against a real inventory." You cannot reliably reuse what you
cannot find; this makes finding mechanical.

The MECHANISM is general; the stack-specifics live in config (which directories
map to which substrate layer). See assets/boundary.config.example.json. Without
a `layers` config the script cannot know your conventions, so it prints guidance
and exits non-zero rather than guess.

Stdlib only. Layers mirror references/shelf.md:
    atomic -> primitive -> seam -> pattern -> pipeline -> scaffold

Usage:
    python shelf_index.py                 # human table from ./boundary.config.json
    python shelf_index.py --repo ../app   # index another repo
    python shelf_index.py --json          # machine-readable (used by plan_new prefill)
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

LAYER_ORDER = ["atomic", "primitive", "seam", "pattern", "pipeline", "scaffold"]

EXPORT = re.compile(
    r"^\s*export\s+(?:default\s+)?(?:async\s+)?"
    r"(?:function|const|let|class|type|interface|enum)\s+([A-Za-z_]\w*)",
    re.MULTILINE,
)
EXPORT_LIST = re.compile(r"^\s*export\s*\{([^}]*)\}", re.MULTILINE)

DEFAULT_EXCLUDES = ["node_modules/**", "**/node_modules/**",
                    "dist/**", "**/dist/**",
                    "build/**", "**/build/**",
                    ".git/**", "**/.git/**",
                    "**/*.test.*", "**/*.spec.*", "**/*.d.ts"]


def load_config(repo: Path, path: str | None) -> dict | None:
    cfg_path = Path(path) if path else repo / "boundary.config.json"
    if not cfg_path.exists():
        return None
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"error: cannot read config {cfg_path}: {e}", file=sys.stderr)
        return None
    if not isinstance(cfg, dict):
        print(f"error: config {cfg_path} must be a JSON object", file=sys.stderr)
        return None
    return cfg


def exports_in(f: Path) -> list[str]:
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    names = set(EXPORT.findall(text))
    for grp in EXPORT_LIST.findall(text):
        for part in grp.split(","):
            sym = part.split(" as ")[0].strip()
            if re.fullmatch(r"[A-Za-z_]\w*", sym):
                names.add(sym)
    return sorted(names)


def excluded(rel: str, globs: list[str]) -> bool:
    s = rel.rstrip("/")
    return any(fnmatch.fnmatch(candidate, g) for candidate in (s, f"{s}/") for g in globs)


def build_index(repo: Path, layers: dict[str, list[str]], excludes: list[str]) -> dict:
    index: dict[str, list[dict]] = {}
    for layer, globs in layers.items():
        units: list[dict] = []
        seen: set[str] = set()
        for g in globs:
            for f in repo.glob(g):
                if not f.is_file():
                    continue
                rel = str(f.relative_to(repo))
                if rel in seen or excluded(rel, excludes):
                    continue
                seen.add(rel)
                syms = exports_in(f)
                units.append({"path": rel, "exports": syms or [f.stem]})
        units.sort(key=lambda u: u["path"])
        index[layer] = units
    return index


def render(index: dict) -> str:
    out: list[str] = []
    total = sum(len(v) for v in index.values())
    out.append(f"Shelf inventory: {total} unit(s) across {len([k for k,v in index.items() if v])} populated layer(s).\n")
    for layer in LAYER_ORDER:
        units = index.get(layer, [])
        if layer not in index:
            continue
        out.append(f"[{layer.upper()}] {len(units)} unit(s)")
        for u in units:
            out.append(f"    {', '.join(u['exports'])}  —  {u['path']}")
        out.append("")
    # any extra (non-standard) layers
    for layer, units in index.items():
        if layer in LAYER_ORDER:
            continue
        out.append(f"[{layer.upper()}] {len(units)} unit(s)")
        for u in units:
            out.append(f"    {', '.join(u['exports'])}  —  {u['path']}")
        out.append("")
    out.append("Use this in PLAN.md section 3: match each bill-of-materials item to a unit "
               "above (REUSE), a near-match to generalize (EXTEND), or nothing (BUILD).")
    return "\n".join(out)


GUIDANCE = """\
No `layers` config found. shelf_index cannot guess your repo's conventions.

Create boundary.config.json at your repo root mapping each substrate layer to
the directories that hold it. A starting point is in this skill at
assets/boundary.config.example.json. Minimal example:

{
  "layers": {
    "atomic":    ["src/ui/tokens/**/*", "src/domain/value-objects/**/*"],
    "primitive": ["src/ui/components/**/*"],
    "seam":      ["src/ports/**/*", "src/hooks/**/*"],
    "pattern":   ["src/ui/patterns/**/*"],
    "pipeline":  ["src/usecases/**/*"],
    "scaffold":  ["src/layouts/**/*"]
  }
}
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Inventory the reusable substrate by layer.")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--config", default=None, help="Path to boundary.config.json.")
    p.add_argument("--json", action="store_true", help="Emit inventory as JSON.")
    args = p.parse_args(argv)

    repo = Path(args.repo).resolve()
    cfg = load_config(repo, args.config)
    if not cfg or "layers" not in cfg or not cfg["layers"]:
        print(GUIDANCE, file=sys.stderr)
        return 2

    excludes = cfg.get("exclude_globs", DEFAULT_EXCLUDES)
    index = build_index(repo, cfg["layers"], excludes)

    if args.json:
        print(json.dumps({"layers": index}, indent=2))
    else:
        print(render(index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

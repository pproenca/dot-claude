#!/usr/bin/env python3
"""Scaffold a PLAN.md for a new feature from the skill's template.

The plan is the workflow's trust boundary: it must exist and pass plan_check.py
before any feature code is written. This script only creates the artifact; the
judgment fields are filled by the developer/agent reasoning over the repo and
the references.

Usage:
    python plan_new.py --title "Refund a paid appointment"
    python plan_new.py --title "..." --out plans/refund.md

Extension point (slice 3): once scripts/shelf_index.py exists, pre-fill the
section 3 shelf-check table with REUSE candidates matched from the index, so the
shelf-check is grounded rather than recalled. See PREFILL_HOOK below.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "PLAN.template.md"


def shelf_inventory_block(repo: Path) -> str | None:
    """Run shelf_index against the repo and render an inventory note for section 3.

    The shelf-check is the anti-duplication step; grounding it in the real
    inventory beats recall. Non-fatal: if no config exists or the index can't
    run, returns None and the plan still scaffolds (shelf-check done by hand).
    """
    if not (repo / "boundary.config.json").exists():
        return None
    shelf = HERE / "shelf_index.py"
    if not shelf.exists():
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(shelf), "--repo", str(repo), "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            return None
        data = json.loads(proc.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return None

    lines = ["", "> **Shelf inventory** (from shelf_index — match your BOM against these for REUSE/EXTEND):"]
    any_unit = False
    for layer, units in data.get("layers", {}).items():
        if not units:
            continue
        any_unit = True
        names = []
        for u in units:
            names.append(f"{', '.join(u['exports'])} (`{u['path']}`)")
        lines.append(f">  - _{layer}_: " + "; ".join(names))
    if not any_unit:
        return None
    lines.append("")
    return "\n".join(lines)


def scaffold(title: str, out: Path, repo: Path) -> int:
    if not TEMPLATE.exists():
        print(f"error: template not found at {TEMPLATE}", file=sys.stderr)
        return 2
    if out.exists():
        print(
            f"error: {out} already exists. Refusing to overwrite a plan.\n"
            f"       Edit it directly, or pass --out to a new path.",
            file=sys.stderr,
        )
        return 1

    text = TEMPLATE.read_text(encoding="utf-8")
    # Stamp the title into the first sentinel so the file is self-identifying.
    text = text.replace("((fill: feature name))", title, 1)
    text = text.replace("((fill: short name))", title, 1)

    # PREFILL_HOOK: ground the shelf-check by injecting the real inventory under
    # section 3's heading (before its table). Judgment (the classification) is
    # still left to the filler; this only supplies what's on the shelf.
    block = shelf_inventory_block(repo)
    prefilled = block is not None
    if prefilled:
        anchor = "## 3. Shelf check (REUSE / EXTEND / BUILD)\n"
        text = text.replace(anchor, anchor + block + "\n", 1)

    stamp = _dt.date.today().isoformat()
    header = f"<!-- scaffolded {stamp} by feature-workflow/plan_new.py -->\n"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + text, encoding="utf-8")

    print(f"created {out}")
    if prefilled:
        print("shelf inventory injected into section 3 (grounded shelf-check).")
    else:
        print("note: no boundary.config.json found — shelf-check is by hand. "
              "Copy assets/boundary.config.example.json to your repo root to ground it.")
    print("next: fill sections 0-6, then run:")
    print(f"      python {HERE / 'plan_check.py'} {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scaffold a feature PLAN.md.")
    p.add_argument("--title", required=True, help="Feature name.")
    p.add_argument("--out", default="PLAN.md", type=Path,
                   help="Output path (default: ./PLAN.md).")
    p.add_argument("--repo", default=".", type=Path,
                   help="Repo root for the shelf-index prefill (default: .).")
    args = p.parse_args(argv)
    return scaffold(args.title, args.out, Path(args.repo).resolve())


if __name__ == "__main__":
    raise SystemExit(main())

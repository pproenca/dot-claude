#!/usr/bin/env python3
"""Install the harness's canonical docs (CONSTITUTION.md, HARNESS.md) into a repo.

Part of harness-setup's RECORD step. These two documents describe the harness
*itself* — its principles (CONSTITUTION.md) and its mechanics (HARNESS.md) — and
are identical for every repo, so they are copied verbatim from the installed
harness into the target repo's `.harness/` namespace. There they sit beside the
per-skill script mirror, giving the repo a self-contained copy of the foundations
the generated AGENTS.md points at.

They are harness-OWNED reference docs, not repo content: re-running setup
refreshes them so a repo stays in sync with the installed harness version. Edit
the harness source, never the `.harness/` copy.

Usage:
    python docs_init.py --repo .          # install/refresh .harness/CONSTITUTION.md + HARNESS.md
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

# The canonical docs live at the harness root. This script is at
# <root>/skills/harness-setup/scripts/docs_init.py, so the root is parents[3].
SOURCE_ROOT = Path(__file__).resolve().parents[3]
DOCS = ("CONSTITUTION.md", "HARNESS.md")


def install_docs(repo: Path) -> list[str]:
    dest_dir = repo / ".harness"
    dest_dir.mkdir(parents=True, exist_ok=True)
    report: list[str] = []
    for name in DOCS:
        src = SOURCE_ROOT / name
        if not src.exists():
            report.append(f"SKIP {name} — not found at harness root ({src})")
            continue
        dst = dest_dir / name
        # Guard against copying a file onto itself (setup run on the harness repo).
        if src.resolve() == dst.resolve():
            report.append(f"SKIP {name} — source is the destination")
            continue
        existed = dst.exists()
        shutil.copyfile(src, dst)
        report.append(f"{'refreshed' if existed else 'installed'} .harness/{name}")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Install the harness's canonical docs into a repo (RECORD step)."
    )
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    for line in install_docs(repo):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

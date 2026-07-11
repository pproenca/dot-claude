#!/usr/bin/env python3
"""The gate. Validate that a feature plan is complete enough to start coding.

This is the forcing function that beats momentum: a non-zero exit before code
exists is a hard stop that prose can never be. It reports *exactly* what's
unfilled so the fix is obvious.

Two stages (the same artifact, validated differently — routing by state):
    pre   (default)  sections 0-6 must be complete    -> gate before code
    post             sections 0-7 must be complete    -> record before shipping

Checks performed:
  1. Required sections present (by heading).
  2. No remaining ((fill ...)) sentinels in the in-scope sections.
  3. Section 3 actually classifies at least one item (REUSE/EXTEND/BUILD).
  4. Section 6 labels each touched-code contact COMPOSITION or COUPLING.

Usage:
    python plan_check.py docs/plans/<feature-slug>.md
    python plan_check.py docs/plans/<feature-slug>.md --stage post

Exit codes: 0 = pass, 1 = incomplete/fail, 2 = usage/IO error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SENTINEL = re.compile(r"\(\(fill")
HEADING = re.compile(r"^##\s+(\d+)\.\s+(.*?)\s*$", re.MULTILINE)

REQUIRED = {
    "pre": [0, 1, 2, 3, 4, 5, 6],
    "post": [0, 1, 2, 3, 4, 5, 6, 7],
}

CLASSIFY = re.compile(r"\b(REUSE|EXTEND|VENDOR|BUILD)\b")
CONTACT = re.compile(r"\b(COMPOSITION|COUPLING)\b")


def table_rows(body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        rows.append(cells)
    return rows


def data_rows(body: str) -> list[list[str]]:
    rows = table_rows(body)
    if rows and any("item" in c.lower() or "touched code" in c.lower() for c in rows[0]):
        return rows[1:]
    return rows


def filled(value: str) -> bool:
    return bool(value.strip()) and not SENTINEL.search(value)


def split_sections(text: str) -> dict[int, tuple[str, str]]:
    """Return {section_number: (title, body)}."""
    matches = list(HEADING.finditer(text))
    out: dict[int, tuple[str, str]] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        title = m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[num] = (title, text[start:end])
    return out


def check(path: Path, stage: str) -> int:
    if not path.exists():
        print(f"error: {path} not found. Scaffold one with plan_new.py.", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    required = REQUIRED[stage]
    problems: list[str] = []

    # 1. required sections present
    for n in required:
        if n not in sections:
            problems.append(f"section {n} is missing entirely")

    # 2. no remaining sentinels in in-scope sections
    for n in required:
        if n not in sections:
            continue
        title, body = sections[n]
        for ln, line in enumerate(body.splitlines(), start=1):
            if SENTINEL.search(line):
                problems.append(f"section {n} ({title}): unfilled placeholder -> {line.strip()[:70]}")

    # 3. shelf-check actually classifies something
    if 3 in sections and 3 in required:
        _, body = sections[3]
        classified = False
        for row in data_rows(body):
            if len(row) < 4:
                continue
            item, layer, exists, decision = row[:4]
            if filled(item) and filled(layer) and filled(exists) and CLASSIFY.fullmatch(decision):
                classified = True
                break
        if not classified:
            problems.append("section 3 (Shelf check): no item classified REUSE/EXTEND/BUILD")

    # 4. seam-check labels each contact
    if 6 in sections and 6 in required:
        _, body = sections[6]
        rows = [row for row in data_rows(body) if any(filled(c) for c in row)]
        for row in rows:
            contact = row[1] if len(row) > 1 else ""
            if not CONTACT.fullmatch(contact):
                problems.append("section 6 (Seam check): every touched-code row needs COMPOSITION/COUPLING")
                break

    if problems:
        print(f"GATE FAILED ({stage}): {path} is not ready.\n")
        for p in problems:
            print(f"  - {p}")
        print(f"\n{len(problems)} item(s) to resolve before "
              f"{'writing code' if stage == 'pre' else 'shipping'}.")
        return 1

    print(f"GATE PASSED ({stage}): {path} is complete.")
    if stage == "pre":
        print("You may begin the inner loop. Compose REUSE/EXTEND first; "
              "build BUILD items via boundary-discipline IMPLEMENT mode.")
    else:
        print("Shelf deposits recorded. Feed promotion candidates to the outer-loop ratchet.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate a feature plan (the gate).")
    p.add_argument("plan", type=Path, nargs="?", default=Path("PLAN.md"),
                   help="Path to the plan (default: ./PLAN.md for backward compatibility).")
    p.add_argument("--stage", choices=("pre", "post"), default="pre",
                   help="pre = gate before code (0-6); post = record before ship (0-7).")
    args = p.parse_args(argv)
    return check(args.plan, args.stage)


if __name__ == "__main__":
    raise SystemExit(main())

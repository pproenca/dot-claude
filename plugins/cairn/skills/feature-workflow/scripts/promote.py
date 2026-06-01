#!/usr/bin/env python3
"""Run the outer-loop promotion checklist against a local unit.

The ratchet promotes an earned one-off into the shared shelf. This script
mechanizes the parts that are countable and surfaces the parts that need
judgment, so promotion happens on evidence — not vibes, and not prematurely.

Checks (from references/shelf.md "definition of reusable" + the Rule of Three):
  1. Rule of Three  — count distinct files that use the unit. <3 => WAIT.
  2. One concept    — count exported symbols. >1 => REVIEW (may be two concepts).
  3. Stable interface — flag imports from feature-specific roots leaking through.
  4. Discoverable   — re-exported from a barrel / has an adjacent doc => else REVIEW.

Verdict: BLOCK (not yet 3 uses) / REVIEW (eligible, judgment items to confirm) /
READY (mechanical checks clean). Promotion itself is a behavior-preserving
boundary-discipline REFACTOR — this only tells you whether to start.

Stdlib only.

Usage:
    python promote.py src/features/refund/confirm-dialog.tsx
    python promote.py src/features/refund/refund-policy.ts --symbol isRefundAllowed
    python promote.py <unit> --repo ../app --json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

EXPORT = re.compile(
    r"^\s*export\s+(?:default\s+)?(?:async\s+)?"
    r"(?:function|const|let|class|type|interface|enum)\s+([A-Za-z_]\w*)",
    re.MULTILINE,
)
IMPORT_FROM = re.compile(r"""import\s+[^;]*?from\s+['"]([^'"]+)['"]""")
DEFAULT_EXCLUDES = ["**/node_modules/**", "**/dist/**", "**/build/**", "**/.git/**",
                    "**/*.d.ts"]
CODE_EXT = {".ts", ".tsx", ".js", ".jsx"}


def load_config(repo: Path, path: str | None) -> dict:
    cfg_path = Path(path) if path else repo / "boundary.config.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def excluded(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def count_uses(repo: Path, unit: Path, symbol: str | None, excludes: list[str]) -> list[str]:
    """Files (excluding unit + tests) that import the unit path or reference the symbol."""
    stem = unit.stem
    users: set[str] = set()
    for f in repo.rglob("*"):
        if not f.is_file() or f.suffix not in CODE_EXT or f.resolve() == unit.resolve():
            continue
        rel = str(f.relative_to(repo))
        if excluded(rel, excludes) or "test" in rel or "spec" in rel:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hit = False
        for imp in IMPORT_FROM.findall(text):
            if stem in imp.split("/")[-1]:
                hit = True
                break
        if not hit and symbol and re.search(rf"\b{re.escape(symbol)}\b", text):
            hit = True
        if hit:
            users.add(rel)
    return sorted(users)


def check_one_concept(unit: Path) -> tuple[str, list[str]]:
    syms = sorted(set(EXPORT.findall(unit.read_text(encoding="utf-8", errors="replace"))))
    if len(syms) <= 1:
        return "PASS", syms
    return "REVIEW", syms


def check_leaks(unit: Path, feature_roots: list[str]) -> tuple[str, list[str]]:
    text = unit.read_text(encoding="utf-8", errors="replace")
    leaks = []
    for imp in IMPORT_FROM.findall(text):
        # relative import that climbs into a sibling feature, or matches a feature root
        for fr in feature_roots:
            base = fr.split("/**")[0].strip("/")
            if base and base in imp:
                leaks.append(imp)
        if re.search(r"\.\./\.\./features/", imp):
            leaks.append(imp)
    leaks = sorted(set(leaks))
    return ("REVIEW" if leaks else "PASS"), leaks


def check_discoverable(unit: Path) -> tuple[str, str]:
    d = unit.parent
    for barrel in ("index.ts", "index.tsx", "index.js"):
        bp = d / barrel
        if bp.exists() and unit.stem in bp.read_text(encoding="utf-8", errors="replace"):
            return "PASS", f"re-exported from {barrel}"
    # adjacent doc?
    for doc in (d / "README.md", unit.with_suffix(".md")):
        if doc.exists():
            return "PASS", f"doc present ({doc.name})"
    # leading doc comment in the file?
    head = unit.read_text(encoding="utf-8", errors="replace")[:400]
    if head.lstrip().startswith(("/**", "//")):
        return "REVIEW", "has a header comment but no barrel/doc"
    return "REVIEW", "no barrel re-export or adjacent doc found"


def run(unit: Path, repo: Path, symbol: str | None, cfg: dict) -> dict:
    excludes = cfg.get("exclude_globs", DEFAULT_EXCLUDES)
    feature_roots = cfg.get("feature_roots", ["src/features/**"])

    users = count_uses(repo, unit, symbol, excludes)
    concept_status, syms = check_one_concept(unit)
    leak_status, leaks = check_leaks(unit, feature_roots)
    disc_status, disc_note = check_discoverable(unit)

    rule_of_three = "PASS" if len(users) >= 3 else "BLOCK"
    if rule_of_three == "BLOCK":
        verdict = "BLOCK"
    elif "REVIEW" in (concept_status, leak_status, disc_status):
        verdict = "REVIEW"
    else:
        verdict = "READY"

    return {
        "unit": str(unit), "symbol": symbol, "verdict": verdict,
        "checks": {
            "rule_of_three": {"status": rule_of_three, "uses": len(users), "users": users},
            "one_concept": {"status": concept_status, "exports": syms},
            "stable_interface": {"status": leak_status, "leaking_imports": leaks},
            "discoverable": {"status": disc_status, "note": disc_note},
        },
    }


def render(r: dict) -> str:
    c = r["checks"]
    lines = [f"Promotion check: {r['unit']}" + (f" :: {r['symbol']}" if r["symbol"] else ""),
             f"VERDICT: {r['verdict']}\n"]
    rot = c["rule_of_three"]
    lines.append(f"  [{rot['status']}] Rule of Three — {rot['uses']} use(s)" +
                 ("" if rot["uses"] >= 3 else "  (wait for the 3rd before extracting)"))
    if rot["users"]:
        lines.append("        users: " + ", ".join(rot["users"][:8]) +
                     (f" (+{len(rot['users'])-8})" if len(rot["users"]) > 8 else ""))
    oc = c["one_concept"]
    lines.append(f"  [{oc['status']}] One concept — exports: {', '.join(oc['exports']) or '(none detected)'}")
    si = c["stable_interface"]
    lines.append(f"  [{si['status']}] Stable interface — " +
                 ("no feature-specific imports leaking" if not si["leaking_imports"]
                  else "leaking: " + ", ".join(si["leaking_imports"])))
    ds = c["discoverable"]
    lines.append(f"  [{ds['status']}] Discoverable — {ds['note']}")
    lines.append("")
    if r["verdict"] == "BLOCK":
        lines.append("Not yet. Fewer than 3 uses — extracting now risks the wrong abstraction.")
    elif r["verdict"] == "REVIEW":
        lines.append("Eligible. Resolve the REVIEW items (judgment), then promote via "
                     "boundary-discipline REFACTOR (behavior-preserving).")
    else:
        lines.append("Mechanical checks clean. Promote via boundary-discipline REFACTOR "
                     "(characterize behavior first, move one unit, then re-point users).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Outer-loop promotion checklist for a local unit.")
    p.add_argument("unit", help="Path to the candidate file.")
    p.add_argument("--symbol", default=None, help="Specific exported symbol to count uses for.")
    p.add_argument("--repo", default=".", help="Repo root (default: .).")
    p.add_argument("--config", default=None, help="Path to boundary.config.json.")
    p.add_argument("--json", action="store_true", help="Emit result as JSON.")
    args = p.parse_args(argv)

    unit = Path(args.unit).resolve()
    if not unit.exists():
        print(f"error: unit {unit} not found", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    cfg = load_config(repo, args.config)
    result = run(unit, repo, args.symbol, cfg)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
    # exit code mirrors verdict so it can gate a hook: 0 READY, 1 REVIEW, 2 BLOCK/err
    return {"READY": 0, "REVIEW": 1, "BLOCK": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())

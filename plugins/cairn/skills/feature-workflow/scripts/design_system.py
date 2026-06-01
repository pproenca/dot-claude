#!/usr/bin/env python3
"""Generate the design-system doc from the shelf — derive, don't hand-maintain.

A design system has two halves with two owners:
- the CATALOG (what primitives exist, their prop surface, their token usage,
  how many screens use each) is *derivable from the code* — a projection of the
  shelf, like shelf_index. This script generates it, so it can't drift.
- the CONVENTIONS (props are typed unions; screens are pure with effects at the
  rim; reference token names, never raw hex) are *judgment*, not derivable. They
  live in a ratchet-promoted reference (design-system.conventions.md) and are
  edited only when a convention crosses the Rule of Three.

The output doc is the two composed: a regenerated catalog block + the conventions
verbatim. `--check` regenerates and compares to disk, exiting non-zero on drift,
so a new primitive added without regenerating fails the gate.

Usage:
    design_system.py --repo .                 # (re)generate docs/design-system.md
    design_system.py --repo . --check         # gate: exit 1 if the doc is stale
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CAT_START = "<!-- design-system:catalog:start — generated; do not edit by hand -->"
CAT_END = "<!-- design-system:catalog:end -->"

_FUNC = re.compile(r"export\s+function\s+([A-Z]\w+)")
_IFACE = re.compile(r"export\s+interface\s+(\w+)\s*\{([^}]*)\}", re.DOTALL)
_TYPE = re.compile(r"export\s+type\s+(\w+)")
_TOKEN = re.compile(r"\b(?:clinic|status)-[\w-]+|\b(?:rounded|font)-(?:card|panel|field|serif|sans)\b")


def load_cfg(repo: Path) -> dict:
    p = repo / "boundary.config.json"
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def layer_dir(cfg: dict, layer: str, default: str) -> Path:
    globs = cfg.get("layers", {}).get(layer, [])
    for g in globs:
        # take the directory prefix of the first glob (e.g. src/ui/components/**/* -> src/ui/components)
        base = g.split("*")[0].rstrip("/")
        if base:
            return Path(base)
    return Path(default)


def consumer_files(repo: Path, cfg: dict) -> list[Path]:
    roots = [Path("app")]
    for fr in cfg.get("feature_roots", ["src/features/**"]):
        roots.append(Path(fr.split("*")[0].rstrip("/")))
    roots.append(layer_dir(cfg, "pattern", "src/ui/patterns"))
    out: list[Path] = []
    for r in roots:
        d = repo / r
        if d.exists():
            out += [p for p in d.rglob("*.ts*") if p.is_file()]
    return out


def use_count(symbol: str, consumers: list[Path], own: Path) -> int:
    word = re.compile(rf"\b{re.escape(symbol)}\b")
    n = 0
    for f in consumers:
        if f == own:
            continue
        try:
            if word.search(f.read_text(encoding="utf-8")):
                n += 1
        except OSError:
            continue
    return n


def tokens_section(repo: Path, cfg: dict) -> str:
    tdir = layer_dir(cfg, "atomic", "src/ui/tokens")
    # prefer a tokens.ts anywhere under the atomic dirs
    cand = list((repo).rglob("tokens.ts"))
    if not cand:
        return "_(no tokens.ts found)_"
    text = cand[0].read_text(encoding="utf-8")
    pairs = re.findall(r'(\w+):\s*"(#[0-9A-Fa-f]{3,8})"', text)
    if not pairs:
        return "_(tokens.ts present; no color pairs parsed)_"
    return "\n".join(f"- `{k}` = {v}" for k, v in pairs)


def catalog(repo: Path, cfg: dict) -> str:
    prim_dir = repo / layer_dir(cfg, "primitive", "src/ui/components")
    consumers = consumer_files(repo, cfg)
    lines = [CAT_START, "", "## Tokens (atomic)", "", tokens_section(repo, cfg), "",
             "## Primitives (generated from the shelf)", ""]
    if not prim_dir.exists():
        lines += ["_(no primitive layer found)_", "", CAT_END]
        return "\n".join(lines)
    files = sorted(p for p in prim_dir.glob("*.tsx") if p.name != "index.ts")
    for f in files:
        src = f.read_text(encoding="utf-8")
        comps = _FUNC.findall(src)
        if not comps:
            continue
        name = comps[0]
        ifaces = {n: body for n, body in _IFACE.findall(src)}
        types = _TYPE.findall(src)
        uses = use_count(name, consumers, f)
        lines.append(f"### {name}  ·  uses: {uses}  ·  `{f.name}`")
        exports = comps + list(ifaces.keys()) + types
        lines.append(f"- exports: {', '.join(dict.fromkeys(exports))}")
        props = ifaces.get(f"{name}Props")
        if props:
            fields = []
            for ln in props.splitlines():
                s = ln.strip()
                c = s.find("//")
                if c != -1:
                    s = s[:c].strip()
                s = s.rstrip(";").strip()
                if s:
                    fields.append(s)
            if fields:
                lines.append("- props: " + "; ".join(fields))
        toks = sorted(set(_TOKEN.findall(src)))
        if toks:
            lines.append(f"- tokens: {', '.join(toks)}")
        lines.append("")
    lines.append(CAT_END)
    return "\n".join(lines)


def compose(repo: Path, cfg: dict, conventions: Path) -> str:
    header = ("# Design system\n\n_Catalog generated from the shelf by "
              "`feature-workflow/scripts/design_system.py` — re-run to refresh; do not "
              "hand-edit the catalog block. Conventions below are ratchet-owned judgment._\n\n")
    conv = conventions.read_text(encoding="utf-8").strip() if conventions.exists() else \
        "## Conventions\n\n_(none recorded yet — promote via knowledge-ratchet)_"
    return header + catalog(repo, cfg) + "\n\n" + conv + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate the design-system doc from the shelf.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="docs/design-system.md")
    ap.add_argument("--conventions", default="docs/design-system.conventions.md")
    ap.add_argument("--check", action="store_true", help="Exit 1 if the doc is stale vs the shelf.")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    cfg = load_cfg(repo)
    expected = compose(repo, cfg, repo / args.conventions)
    out = repo / args.out

    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current.strip() != expected.strip():
            print("design-system doc is STALE — the shelf or conventions changed but the doc "
                  "wasn't regenerated. Run design_system.py (no --check) to refresh.")
            return 1
        print("design-system doc is fresh (matches the shelf).")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(expected, encoding="utf-8")
    print(f"generated {args.out} from the shelf.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

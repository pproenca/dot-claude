#!/usr/bin/env python3
"""Derive a feature's skeleton — interfaces + wiring — for review before fleshing.

The cheapest place to catch a conceptual error is the interface stage: concrete
enough to be wrong in checkable ways, abstract enough that fixing it is free.
This extracts, from a feature's files (and the route that mounts it), the public
signatures of each unit and how the units depend on one another — so a reviewer
sees the skeleton at a glance and judges it against the boundary model
(boundary-discipline) before any bodies exist.

It is design_system.py's sibling: derive a reviewable view from code rather than
author a description that drifts. It does not replace reading the stubbed code
(which must typecheck — that is the proof the interfaces compose); it makes the
*shape* reviewable.

Heuristic boundary tags are CANDIDATES (like scan.py): the view surfaces, the
model judges.

Usage:
    skeleton.py --repo . --feature src/features/booking
    skeleton.py --repo . --feature src/features/patients --out docs/skeleton-patients.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _src_exts(cfg: dict) -> list[str]:
    """Source extensions from the config's substrate, not hardcoded TS. Falls
    back to a broad set with a visible signal if absent."""
    exts = cfg.get("include_ext") if isinstance(cfg, dict) else None
    if exts and not any(str(e).startswith("FILL") for e in exts):
        return [e if e.startswith(".") else "." + e for e in exts]
    return []  # unknown: caller must signal it cannot read this substrate

_FUNC = re.compile(r"export\s+(?:async\s+)?function\s+([A-Za-z]\w*)\s*(\([^)]*\))(\s*:\s*[^\{]+)?")
_ARROW = re.compile(r"export\s+const\s+([A-Za-z]\w*)\s*=\s*(async\s+)?(\([^)]*\))(\s*:\s*[^=]+?)?\s*=>")
_IFACE = re.compile(r"export\s+interface\s+(\w+)\s*\{([^}]*)\}", re.DOTALL)
_TYPE = re.compile(r"export\s+type\s+(\w+)\s*=\s*([^;]+);", re.DOTALL)
_IMPORT = re.compile(r'import\s+(?:type\s+)?(?:\{([^}]*)\}|\*\s+as\s+\w+|(\w+))\s+from\s+["\']([^"\']+)["\']')
_ZOBJECT = re.compile(r"z\s*\.object\(\{(.*?)\}\)", re.DOTALL)
_REFINE = re.compile(r'\.refine\(.*?message:\s*["\']([^"\']+)["\']', re.DOTALL)
_INVARIANT = re.compile(r"@invariant:?\s*(.+)")


def load_cfg(repo: Path) -> dict:
    p = repo / "boundary.config.json"
    try:
        cfg = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (json.JSONDecodeError, OSError):
        return {}
    return cfg if isinstance(cfg, dict) else {}


def _glob_re(glob: str) -> re.Pattern:
    g = glob.rstrip("/").replace("**", "\0")
    out = []
    for ch in g:
        if ch == "\0":
            out.append(".*")
        elif ch == "*":
            out.append("[^/]*")
        elif ch in ".+()[]{}^$|\\":
            out.append("\\" + ch)
        else:
            out.append(ch)
    return re.compile("^" + "".join(out) + "(/.*)?$")


def layer_of(path_str: str, cfg: dict) -> str:
    s = path_str.replace("\\", "/")
    best, best_score = None, -1
    for layer, globs in cfg.get("layers", {}).items():
        for g in globs:
            if _glob_re(g).match(s):
                score = len(g.rstrip("/"))  # most specific glob wins, not dict order
                if score > best_score:
                    best, best_score = layer, score
    if best:
        return best
    if "/features/" in s or s.startswith("features/"):
        return "feature"
    return "external"


def classify_import(spec: str) -> str:
    """Where does an import point? (drives the wiring edge label.)"""
    if not spec.startswith("."):
        return "vendor"          # external library
    s = spec
    if "ui/components" in s:
        return "primitive"
    if "ui/hooks" in s or "providers" in s:
        return "seam"
    if "ui/patterns" in s:
        return "pattern"
    if "domain" in s or "tokens" in s:
        return "atomic"
    if "usecases" in s:
        return "pipeline"
    return "feature"


def boundary_tag(name: str, params: str, ret: str, body_hint: str) -> str:
    p = (params or "").lower()
    r = (ret or "").lower()
    tags = []
    if "unknown" in p:
        tags.append("TRUST: unknown -> domain")
    if "promise" in r or "async" in body_hint:
        tags.append("EFFECT")
    return f"  [{' · '.join(tags)}]" if tags else ""


def is_port_interface(body: str) -> bool:
    # an interface that is mostly function-typed fields = injected effects (ports)
    fields = [l for l in body.splitlines() if ":" in l]
    if not fields:
        return False
    fnlike = sum(1 for l in fields if "=>" in l or re.search(r"\bon[A-Z]", l))
    return fnlike >= max(1, len(fields) // 2)


def feature_files(repo: Path, feature: str, cfg: dict) -> list[Path]:
    d = repo / feature
    exts = _src_exts(cfg)
    if not exts:
        print("WARNING: boundary.config.json has no known include_ext (substrate unknown?) — "
              "cannot enumerate source files for this stack. Fill include_ext first.", file=sys.stderr)
    files = [p for p in d.rglob("*") if p.is_file() and p.suffix in exts and not p.name.endswith(".d.ts")] if (d.exists() and exts) else []
    # include any app/** route that imports from this feature
    app = repo / "app"
    feat_token = Path(feature).name
    if app.exists():
        for p in (app.rglob("*") if app.exists() else []):
            if p.suffix not in _src_exts(cfg): continue
            try:
                if feat_token in p.read_text(encoding="utf-8") or feature in p.read_text(encoding="utf-8"):
                    files.append(p)
            except OSError:
                continue
    return sorted(set(files))


def _resolve(from_file: Path, spec: str) -> Path | None:
    """Resolve a relative import spec to a concrete .ts/.tsx file (handles barrels)."""
    base = (from_file.parent / spec).resolve()
    for cand in (base.with_suffix(".ts"), base.with_suffix(".tsx"),
                 base / "index.ts", base / "index.tsx"):
        if cand.exists():
            return cand
    return None


def boundary_neighbors(repo: Path, files: list[Path], cfg: dict) -> list[Path]:
    """One hop out: the seam/domain files this feature imports — its OWN boundaries
    (the trust parse, the ports/hook). Stops there: shelf primitives are stable and
    reviewed, shown as wiring edges only, not expanded."""
    out: list[Path] = []
    for f in files:
        try:
            src = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for braced, dflt, spec in _IMPORT.findall(src):
            if not spec.startswith("."):
                continue
            if classify_import(spec) not in ("seam", "atomic"):
                continue
            tgt = _resolve(f, spec)
            if tgt and tgt not in files and tgt not in out and "tokens" not in str(tgt):
                out.append(tgt)
    return sorted(set(out))


_PY_DEF = re.compile(r"^\s*(async\s+)?def\s+([a-zA-Z_]\w*)\s*(\([^)]*\))\s*(->\s*[^:]+)?:", re.MULTILINE)
_PY_CLASS = re.compile(r"^\s*class\s+(\w+)\s*(\([^)]*\))?:", re.MULTILINE)

# The TS regexes below are one LANGUAGE ADAPTER behind this dispatch. Other
# languages plug in their own extractor; an unsupported language degrades to a
# VISIBLE "unsupported" signal, never a silent empty result (the silent-empty
# was the real failure — it hid every boundary on a non-TS repo while the skill
# claimed to be stack-agnostic). The boundary MODEL is language-agnostic; the
# automated extraction is per-language and must say so when it cannot read a file.
def extract(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix in (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts"):
        return _extract_ts(path)
    if suffix == ".py":
        return _extract_py(path)
    return {"sigs": [("unsupported", f"(skeleton extraction not implemented for {suffix} — "
                      f"the boundary MODEL still applies; add a language adapter)", "")],
            "edges": [], "src": "", "schema": [], "established": [], "proposed": [], "unsupported": True}


def _extract_py(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    sigs = []
    for async_kw, name, params, ret in _PY_DEF.findall(src):
        if name.startswith("_"):
            continue
        ret_s = (ret or "").strip().lstrip("->").strip()
        sigs.append(("fn", f"{name}{params}" + (f" -> {ret_s}" if ret_s else ""),
                     boundary_tag(name, params, ret_s, "async" if async_kw else "")))
    for name, _bases in _PY_CLASS.findall(src):
        sigs.append(("type", f"class {name}", ""))
    # invariants via the same @invariant annotation convention (language-neutral)
    proposed = [m.strip() for m in _INVARIANT.findall(src)]
    return {"sigs": sigs, "edges": [], "src": src, "schema": [],
            "established": [], "proposed": proposed}


def _extract_ts(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    sigs = []
    seen_names = set()
    for name, params, ret in _FUNC.findall(src):
        ret_s = (ret or "").strip().lstrip(":").strip()
        async_hint = "async" if re.search(rf"async\s+function\s+{name}\b", src) else ""
        sigs.append(("fn", f"{name}{params}" + (f": {ret_s}" if ret_s else ""),
                     boundary_tag(name, params, ret_s, async_hint)))
        seen_names.add(name)
    # Arrow-function exports: `export const f = (x: unknown): T => ...` — the
    # modern TS style. Without this, a trust/effect boundary written as a const
    # arrow is INVISIBLE to the review, which is exactly the boundary it must show.
    for name, async_kw, params, ret in _ARROW.findall(src):
        if name in seen_names:
            continue
        ret_s = (ret or "").strip().lstrip(":").strip()
        sigs.append(("fn", f"{name}{params}" + (f": {ret_s}" if ret_s else ""),
                     boundary_tag(name, params, ret_s, "async" if async_kw else "")))
        seen_names.add(name)
    for name, body in _IFACE.findall(src):
        tag = "  [PORTS — effects injected]" if is_port_interface(body) else ""
        fields = "; ".join(l.strip().rstrip(";").strip() for l in body.splitlines() if l.strip() and ":" in l)
        sigs.append(("interface", f"{name} {{ {fields} }}", tag))
    for name, rhs in _TYPE.findall(src):
        rhs1 = re.sub(r"\s+", " ", rhs).strip()
        tag = "  [sum type — illegal states constrained]" if ("|" in rhs1 and ("tag:" in rhs1 or "kind:" in rhs1)) else ""
        sigs.append(("type", f"{name} = {rhs1[:120]}", tag))
    edges = []
    for braced, dflt, spec in _IMPORT.findall(src):
        kind = classify_import(spec)
        syms = braced or dflt
        edges.append((kind, spec, syms.strip()))

    # Schema shapes: the field shape of zod object schemas (the trust boundary's
    # actual contract — where "illegal states unrepresentable" is decided).
    schema = []
    for obj_body in _ZOBJECT.findall(src):
        fields = []
        for ln in obj_body.splitlines():
            m = re.match(r"\s*(\w+)\s*:\s*(z\.[^,]+),?", ln)
            if m:
                fields.append(f"{m.group(1)}: {m.group(2).strip()}")
        if fields:
            schema.append(fields)

    # Invariants. A .refine(...message...) is ENFORCED (established, executable).
    # An `@invariant` annotation with no enforcement is a PROPOSED claim awaiting
    # the human's confirmation — the spec parse-point.
    established = [m.strip() for m in _REFINE.findall(src)]
    proposed = [m.strip() for m in _INVARIANT.findall(src)]
    return {"sigs": sigs, "edges": edges, "src": src,
            "schema": schema, "established": established, "proposed": proposed}


def render(repo: Path, feature: str, cfg: dict) -> str:
    files = feature_files(repo, feature, cfg)
    if not files:
        return f"no files found under {feature}"
    neighbors = boundary_neighbors(repo, files, cfg)
    out = [f"# Skeleton: {feature}", "",
           "_Generated by feature-workflow/scripts/skeleton.py — review the interfaces and "
           "wiring against the boundary model BEFORE fleshing bodies. Boundary tags are "
           "candidates; you judge._", "",
           "## Interfaces (the contracts to review first)", ""]
    nodes = {}
    edges_all = []
    schema_all = []        # (rel, fields)
    rules_all = []         # (rel, status, text)
    rule_boundaries = []   # (rel, has_rule) for decision/trust units — to flag blanks
    for f in list(files) + neighbors:
        rel = f.relative_to(repo)
        layer = layer_of(str(rel), cfg)
        node = f.stem
        nodes[node] = layer
        data = extract(f)
        marker = "  ← composed boundary" if f in neighbors else ""
        out.append(f"### {rel}  ·  _{layer}_{marker}")
        if not data["sigs"]:
            out.append("- (no exported signatures)")
        for kind, sig, tag in data["sigs"]:
            out.append(f"- `{sig}`{tag}")
        out.append("")
        for fields in data["schema"]:
            schema_all.append((str(rel), fields))
        for inv in data["established"]:
            rules_all.append((str(rel), "established", inv))
        for inv in data["proposed"]:
            rules_all.append((str(rel), "proposed", inv))
        # a unit is a rule-bearing boundary if it's seam/atomic/pipeline (decisions/trust)
        if layer in ("seam", "atomic", "pipeline") and data["sigs"]:
            rule_boundaries.append((str(rel), bool(data["established"] or data["proposed"])))
        if f in files:  # only chart edges from the feature's own units
            for ekind, spec, syms in data["edges"]:
                if ekind in ("primitive", "seam", "atomic", "pattern", "pipeline", "feature", "vendor"):
                    edges_all.append((node, ekind, spec, syms))

    # Schema section: the field shapes of the trust-boundary schemas (where
    # illegal-states-unrepresentable is actually decided — review the SHAPE).
    out += ["## Schema (trust-boundary shapes)", ""]
    if schema_all:
        for rel, fields in schema_all:
            out.append(f"- `{rel}`:")
            for fld in fields:
                out.append(f"    - {fld}")
    else:
        out.append("- (no schema definitions found)")
    out.append("")

    # Rules section: invariants on the decision/trust boundaries, classified.
    # established = enforced in code (executable); proposed = a claim awaiting
    # human confirmation (the spec parse-point). A rule-bearing boundary with no
    # invariant is flagged — a blank is itself a review signal.
    out += ["## Rules & invariants (the spec to confirm)", ""]
    if rules_all:
        for rel, status, text in rules_all:
            mark = "✓ established (enforced)" if status == "established" else "◌ PROPOSED — confirm or correct"
            out.append(f"- [{mark}] {text}  · `{rel}`")
    else:
        out.append("- (no invariants declared)")
    blanks = [rel for rel, has in rule_boundaries if not has]
    for rel in dict.fromkeys(blanks):
        out.append(f"- ⚠ no invariant declared on a decision/trust boundary — is that right? · `{rel}`")
    out.append("")

    # Wiring graph (mermaid): who imports whom, edge labelled by what kind of unit.
    out += ["## Wiring (how the units speak)", "", "```mermaid", "graph TD"]
    seen = set()
    for src_node, ekind, spec, syms in edges_all:
        target = Path(spec).name or spec
        if ekind == "vendor":
            target = spec  # external pkg name
        label = "vendor" if ekind == "vendor" else ekind
        line = f'  {src_node}["{src_node}"] -->|{label}| {re.sub(chr(92)+"W","_",target)}["{target}"]'
        if line not in seen:
            seen.add(line); out.append(line)
    out += ["```", "",
            "**Review against the boundary model:** is each boundary's signature its right "
            "kind (trust = unknown→domain, effect injected not returned)? Are effects at the "
            "rim (ports), not in the pure core? Do the types make illegal states "
            "unrepresentable? Does anything couple where it should compose?"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Derive a feature's skeleton (interfaces + wiring) for review.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--feature", required=True, help="Feature dir, e.g. src/features/booking")
    ap.add_argument("--out", default=None, help="Write to a file (default: stdout).")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    doc = render(repo, args.feature, load_cfg(repo))
    if args.out:
        (repo / args.out).parent.mkdir(parents=True, exist_ok=True)
        (repo / args.out).write_text(doc + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Mechanize the boundary-discipline AUDIT fingerprints into triage candidates.

This is a triage aid, not a verdict machine. It surfaces *candidates* — the
places a boundary fingerprint appears — grouped by boundary kind. Whether each
is a real gap is judgment: take this output back to references/audit.md and
classify (undefended / duplicated / leaked / unsized). The script handles the
mechanical, error-prone-by-hand part (running the same patterns identically
everywhere); the model does the reasoning.

Stdlib only — no ripgrep dependency, runs anywhere python3 runs.

Config (optional): ./boundary.config.json at the repo root. Keys used here:
    include_ext     list of file extensions to scan   (default: ts/tsx/js/jsx)
    exclude_globs   list of fnmatch globs to skip      (default: deps/build/tests)
Missing config = built-in defaults, so this runs zero-config.

Usage:
    python scan.py                 # scan ./ , human summary
    python scan.py src/features/x  # scan a subtree
    python scan.py --full          # list every hit, not a capped sample
    python scan.py --json          # machine-readable findings
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

DEFAULTS = {
    # DEFAULTS assume a TS/JS repo. With a boundary.config.json present, the
    # configured include_ext (any substrate) overrides these. Without one, scan
    # only sees TS/JS — run config_init.py first for Go/Rust/Python/etc.
    "include_ext": [".ts", ".tsx", ".js", ".jsx"],
    "exclude_globs": [
        "**/node_modules/**", "**/dist/**", "**/build/**", "**/.git/**",
        "**/*.test.*", "**/*.spec.*", "**/*.d.ts",
    ],
}

_IMPORT_AS = re.compile(r"\bimport\b.*\bas\b")


def _strip_comment(line: str) -> str:
    """Remove a line/trailing // comment and treat block-comment lines as blank.
    Naive (does not parse strings), but enough to stop the scanner reading prose
    'as', namespace imports, and 'as const' as trust casts."""
    s = line.lstrip()
    if s.startswith(("*", "/*", "//")):
        return ""
    i = line.find("//")
    return line[:i] if i != -1 else line


# boundary kind -> list of (label, compiled pattern). Mirrors references/audit.md.
# The boundary KINDS (trust/effect/consistency/containment) are universal and
# constitutional. How each kind MANIFESTS in source — the fingerprints below — is
# NOT universal: it is per-substrate craft that Cairn should derive and own, the same
# way it derives substrate conventions (see harness-setup/investigating-substrate.md).
#
# So these are not law. They are a LABELED SEED for one ecosystem (TS/JS), provided
# only so a fresh TS repo is not blind on day one. Cairn loads its OWN derived
# patterns from boundary-patterns.jsonl (per substrate) and they take precedence;
# what it derives for Go, Rust, Python, or anything else, it writes there and owns.
# A pattern Cairn did not derive is a guess it cannot defend or maintain.
_SEED_PATTERNS_TS: dict[str, list[tuple[str, re.Pattern]]] = {
    "trust": [
        ("cast (as)", re.compile(r"\bas\s+(?!const\b)[A-Za-z_]")),
        ("any", re.compile(r":\s*any\b|<any>|\bany\[\]")),
        ("non-null !", re.compile(r"!\.")),
        ("JSON.parse", re.compile(r"JSON\.parse")),
        ("raw request field", re.compile(r"req\.(body|query|params)")),
        ("inline env read", re.compile(r"process\.env\.")),
    ],
    "effect": [
        ("await/then", re.compile(r"\bawait\b|\.then\(")),
        ("fetch", re.compile(r"\bfetch\(")),
        ("fs", re.compile(r"\bfs\.")),
        ("clock", re.compile(r"Date\.now\(|new Date\(")),
        ("randomness", re.compile(r"Math\.random\(")),
    ],
    "consistency": [
        ("read-before-write", re.compile(r"findUnique|findFirst|\.count\(")),
    ],
    "containment": [
        ("external call", re.compile(r"\bfetch\(|\baxios\b|\bhttp\.|new Pool|createClient")),
    ],
}

_SEED_PATTERNS_PY: dict[str, list[tuple[str, re.Pattern]]] = {
    "trust": [
        ("Any", re.compile(r"\bAny\b")),
        ("cast", re.compile(r"\bcast\(")),
        ("json loads", re.compile(r"\bjson\.loads\(")),
        ("raw env read", re.compile(r"\bos\.environ\b|\bos\.getenv\(")),
        ("raw request field", re.compile(r"\brequest\.(args|form|json|data)\b")),
    ],
    "effect": [
        ("async/await", re.compile(r"\bawait\b|\basync\s+def\b")),
        ("filesystem", re.compile(r"\bopen\(|\bPath\([^)]*\)\.(read|write)_text\(")),
        ("subprocess", re.compile(r"\bsubprocess\.")),
        ("clock", re.compile(r"\bdatetime\.now\(|\btime\.time\(")),
        ("randomness", re.compile(r"\brandom\.")),
    ],
    "consistency": [
        ("read-before-write", re.compile(r"\bget\([^)]*\).*\n.*\b(set|update|append)\(")),
    ],
    "containment": [
        ("external call", re.compile(r"\brequests\.|\bhttpx\.|\burllib\.request")),
    ],
}

BOUNDARY_KINDS = ["trust", "effect", "consistency", "containment"]
PATTERN_STORE = "boundary-patterns.jsonl"


def load_patterns(repo: Path, substrate: str | None, source_exts: set[str] | None = None) -> tuple[dict[str, list[tuple[str, re.Pattern]]], str]:
    """Cairn's OWN derived fingerprints for this substrate, if it has any; else the
    labeled TS seed (with an honest note that they may not fit a non-TS stack).
    Returns (patterns, provenance)."""
    store = repo / PATTERN_STORE
    derived: dict[str, list[tuple[str, re.Pattern]]] = {}
    if store.exists():
        for line in store.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if substrate and r.get("substrate") not in (substrate, None):
                continue
            try:
                derived.setdefault(r["boundary"], []).append((r["label"], re.compile(r["regex"])))
            except (KeyError, re.error):
                pass
    if derived:
        return derived, f"derived (Cairn's own findings for substrate '{substrate or 'any'}')"
    sub = (substrate or "").lower()
    if "python" in sub or (source_exts and ".py" in source_exts and not source_exts.intersection({".ts", ".tsx", ".js", ".jsx"})):
        return _SEED_PATTERNS_PY, "basic Python seed (NOT derived — triage aid; derive + record better patterns for this repo)"
    return _SEED_PATTERNS_TS, "TS/JS seed (NOT derived — only valid for TS/JS; derive + record for other substrates)"


def load_config(repo: Path, path: str | None) -> dict:
    cfg = dict(DEFAULTS)
    cfg_path = Path(path) if path else repo / "boundary.config.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                print(f"warning: ignoring config {cfg_path}: expected a JSON object", file=sys.stderr)
                return cfg
            for k in ("include_ext", "exclude_globs"):
                if k in data:
                    cfg[k] = data[k]
            if "_substrate" in data:
                cfg["_substrate"] = data["_substrate"]
        except (json.JSONDecodeError, OSError) as e:
            print(f"warning: ignoring unreadable config {cfg_path}: {e}", file=sys.stderr)
    return cfg


def excluded(rel: Path, globs: list[str]) -> bool:
    s = str(rel)
    return any(fnmatch.fnmatch(s, g) for g in globs)


def scan(root: Path, cfg: dict, repo: Path | None = None) -> tuple[list[dict], str]:
    findings: list[dict] = []
    exts = set(cfg["include_ext"])
    globs = cfg["exclude_globs"]
    substrate = cfg.get("_substrate")
    patterns, provenance = load_patterns(repo or (root if root.is_dir() else root.parent), substrate, exts)
    base = root if root.is_dir() else root.parent
    files = [root] if root.is_file() else list(root.rglob("*"))
    for f in files:
        if not f.is_file() or f.suffix not in exts:
            continue
        rel = f.relative_to(base) if root.is_dir() else f
        if excluded(rel, globs):
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            code = _strip_comment(line)
            if not code.strip():
                continue  # whole-line comment — not code
            import_as = _IMPORT_AS.search(code) is not None
            for boundary, pats in patterns.items():
                for label, pat in pats:
                    if pat.search(code):
                        if label == "cast (as)" and import_as:
                            continue  # `import * as x` / `import { y as z }` is not a trust cast
                        findings.append({
                            "boundary": boundary, "label": label,
                            "file": str(rel), "line": n,
                            "snippet": line.strip()[:100],
                        })
    return findings, provenance


def summarize(findings: list[dict], full: bool) -> str:
    if not findings:
        return "No boundary fingerprints found. NOTE: scan's pattern library is TS/JS-shaped; on a non-TS substrate a clean result may just mean my fingerprints do not cover this language yet (the boundary CONCEPTS are universal; these regexes are not). Reason about boundaries from references/audit.md directly for this stack."
    out: list[str] = []
    by_boundary: dict[str, list[dict]] = {}
    for f in findings:
        by_boundary.setdefault(f["boundary"], []).append(f)

    order = ["trust", "effect", "consistency", "containment"]
    out.append(f"{len(findings)} candidate(s) across {len({f['file'] for f in findings})} file(s).")
    out.append("These are CANDIDATES, not gaps — classify each against references/audit.md.\n")
    for b in order:
        items = by_boundary.get(b, [])
        if not items:
            continue
        files = {}
        for it in items:
            files[it["file"]] = files.get(it["file"], 0) + 1
        hot = sorted(files.items(), key=lambda kv: -kv[1])[:5]
        out.append(f"[{b.upper()}] {len(items)} hit(s) in {len(files)} file(s)")
        out.append("  hotspots: " + ", ".join(f"{p} (x{c})" for p, c in hot))
        sample = items if full else items[:6]
        for it in sample:
            out.append(f"    {it['file']}:{it['line']}  «{it['label']}»  {it['snippet']}")
        if not full and len(items) > 6:
            out.append(f"    ... +{len(items) - 6} more (use --full)")
        out.append("")
    out.append("Triage tip: trust hits deep in domain logic, or effect hits with no "
               "pure decision upstream, are the likely real gaps.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Boundary fingerprint scanner (audit triage aid).")
    p.add_argument("path", nargs="?", default=".", help="File or directory to scan (default: .).")
    p.add_argument("--config", default=None, help="Path to boundary.config.json.")
    p.add_argument("--full", action="store_true", help="List every hit, not a capped sample.")
    p.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    p.add_argument("--record-pattern", nargs=4, metavar=("SUBSTRATE", "BOUNDARY", "LABEL", "REGEX"),
                   help="Record a fingerprint Cairn DERIVED for a substrate, so it owns it. "
                        "e.g. --record-pattern go effect 'http call' 'http\\.(Get|Post)'")
    args = p.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"error: {root} not found", file=sys.stderr)
        return 2
    repo = root if root.is_dir() else root.parent

    # recording mode: Cairn writes a fingerprint it derived (a pattern it can defend),
    # keyed by substrate, into its own boundary-patterns.jsonl. This is how the smell
    # library grows for Go/Rust/Python/anything — derived and owned, never handed down.
    if args.record_pattern:
        substrate, boundary, label, regex = args.record_pattern
        if boundary not in BOUNDARY_KINDS:
            print(f"error: boundary must be one of {BOUNDARY_KINDS} (the kinds are universal).", file=sys.stderr)
            return 2
        try:
            re.compile(regex)
        except re.error as e:
            print(f"error: invalid regex: {e}", file=sys.stderr); return 2
        store = repo / PATTERN_STORE
        with store.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"substrate": substrate, "boundary": boundary,
                                "label": label, "regex": regex}, ensure_ascii=False) + "\n")
        print(f"recorded {boundary} fingerprint '{label}' for substrate '{substrate}' — Cairn owns it now.")
        return 0

    cfg = load_config(repo, args.config)
    findings, provenance = scan(root, cfg, repo)

    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings), "patterns": provenance}, indent=2))
    else:
        print(f"(patterns: {provenance})")
        print(summarize(findings, args.full))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

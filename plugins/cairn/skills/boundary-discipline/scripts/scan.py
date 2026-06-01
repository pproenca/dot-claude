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
PATTERNS: dict[str, list[tuple[str, re.Pattern]]] = {
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


def load_config(repo: Path, path: str | None) -> dict:
    cfg = dict(DEFAULTS)
    cfg_path = Path(path) if path else repo / "boundary.config.json"
    if cfg_path.exists():
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            for k in ("include_ext", "exclude_globs"):
                if k in data:
                    cfg[k] = data[k]
        except (json.JSONDecodeError, OSError) as e:
            print(f"warning: ignoring unreadable config {cfg_path}: {e}", file=sys.stderr)
    return cfg


def excluded(rel: Path, globs: list[str]) -> bool:
    s = str(rel)
    return any(fnmatch.fnmatch(s, g) for g in globs)


def scan(root: Path, cfg: dict) -> list[dict]:
    findings: list[dict] = []
    exts = set(cfg["include_ext"])
    globs = cfg["exclude_globs"]
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
            for boundary, pats in PATTERNS.items():
                for label, pat in pats:
                    if pat.search(code):
                        if label == "cast (as)" and import_as:
                            continue  # `import * as x` / `import { y as z }` is not a trust cast
                        findings.append({
                            "boundary": boundary, "label": label,
                            "file": str(rel), "line": n,
                            "snippet": line.strip()[:100],
                        })
    return findings


def summarize(findings: list[dict], full: bool) -> str:
    if not findings:
        return "No boundary fingerprints found. (Either very clean, or the scan path/config is too narrow.)"
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
    args = p.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"error: {root} not found", file=sys.stderr)
        return 2
    repo = root if root.is_dir() else root.parent
    cfg = load_config(repo, args.config)
    findings = scan(root, cfg)

    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
    else:
        print(summarize(findings, args.full))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

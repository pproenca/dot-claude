#!/usr/bin/env python3
"""Investigate the repo's substrate and scaffold a DRAFT boundary.config.json.

This tool does NOT carry a table of substrates. A table would be inherited
knowledge Cairn does not own — frozen, unmaintainable when conventions shift, blind
to ecosystems no one listed. Instead it runs the METHOD in
references/investigating-substrate.md: look for the manifest that identifies the
ecosystem, derive the conventions from what is actually found, and CACHE the finding
to library-knowledge so Cairn owns it and recalls its OWN derivation next time.

The first time Cairn meets an ecosystem, it investigates and records what it learned.
The second time, it recalls its own finding (and may re-validate it). The substrate
catalogue builds itself, one owned entry at a time, from real encounters — never
handed down. An unrecognized substrate is reported honestly ("investigated, here is
what I observed, here is what I could not determine"), never defaulted to a familiar
stack.

This composes existing faculties: inquiry (predict→observe→update) is the method,
library-knowledge is where the derived fact lives. Always finish with config_check.py.

Usage:
    python config_init.py --repo .
    python config_init.py --repo ../app --skills-root ~/.claude/skills
    python config_init.py --force
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# The substrate store: Cairn's OWN derived findings, keyed by substrate name. This is
# library-knowledge (facts confirmed against authority, cached, re-validated). It
# starts EMPTY. Nothing here is authored by the tool's maker; every entry is written
# by Cairn after investigating a real repo.
SUBSTRATE_STORE = "substrate-knowledge.jsonl"


def _store_path(repo: Path) -> Path:
    return repo / SUBSTRATE_STORE


def _load_findings(repo: Path) -> dict:
    """Cairn's previously-derived substrate findings (its own, not the maker's)."""
    p = _store_path(repo)
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    r = json.loads(line); out[r["substrate"]] = r
                except (json.JSONDecodeError, KeyError):
                    pass
    return out


def _record_finding(repo: Path, finding: dict) -> None:
    """Cache a derived finding so Cairn owns and recalls it. Library-knowledge home."""
    p = _store_path(repo)
    findings = _load_findings(repo)
    findings[finding["substrate"]] = finding
    p.write_text("".join(json.dumps(findings[k], ensure_ascii=False) + "\n"
                          for k in sorted(findings)), encoding="utf-8")


def mirror_scripts(repo: Path, skills_root: str | None) -> str | None:
    """Copy each skill's scripts into .harness/<skill>/ without flattening names."""
    if not skills_root:
        return None
    root = Path(skills_root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"skills root {root} not found")
    count = 0
    for skill in sorted(p for p in root.iterdir() if p.is_dir()):
        scripts = skill / "scripts"
        if not scripts.is_dir():
            continue
        out = repo / ".harness" / skill.name
        out.mkdir(parents=True, exist_ok=True)
        for src in sorted(scripts.glob("*.py")):
            shutil.copy2(src, out / src.name)
            count += 1
    return f"mirrored {count} script(s) into {repo / '.harness'}"


def find_manifests(repo: Path) -> list[tuple[str, str]]:
    """Step 2 of the method: the cheapest discriminating observation. Find root
    build/manifest files that declare an ecosystem. The tool does not know what each
    MEANS — it surfaces the evidence; the ecosystem is inferred from the manifest's
    name/contents, and that inference becomes an owned finding. This list is the
    SHAPE of evidence to look for (a manifest is a manifest in any ecosystem), not a
    map of which manifest is which language."""
    common_manifest_names = [
        "package.json", "go.mod", "Cargo.toml", "pyproject.toml", "setup.py",
        "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile", "composer.json",
        "mix.exs", "pubspec.yaml", "deno.json", "*.csproj", "*.fsproj", "Package.swift",
        "CMakeLists.txt", "Makefile", "build.sbt", "rebar.config", "dub.json",
    ]
    found = []
    for name in common_manifest_names:
        if "*" in name:
            for hit in repo.glob(name):
                found.append((hit.name, hit.read_text(encoding="utf-8", errors="ignore")[:400]))
        else:
            p = repo / name
            if p.exists():
                found.append((name, p.read_text(encoding="utf-8", errors="ignore")[:400]))
    return found


def observe_layout(repo: Path) -> list[str]:
    """Step 3 evidence: the actual top-level directory layout, so conventions are
    CONFIRMED against the real tree rather than assumed."""
    dirs = []
    for p in sorted(repo.iterdir()):
        if p.is_dir() and not p.name.startswith(".") and p.name not in (
                "node_modules", "vendor", "target", "dist", "build", "__pycache__"):
            dirs.append(p.name)
            # one level deeper for the common "src/<...>" and "internal/<...>" shapes
            for q in sorted(p.iterdir()):
                if q.is_dir() and not q.name.startswith("."):
                    dirs.append(f"{p.name}/{q.name}")
    return dirs[:60]


def build_investigation(repo: Path) -> tuple[dict, list[str]]:
    """Run the method and produce a DRAFT config plus an investigation report. Where
    Cairn has a prior OWN finding for the detected substrate, recall it; otherwise
    present the raw evidence for Cairn to derive from and then record."""
    notes: list[str] = []
    manifests = find_manifests(repo)
    layout = observe_layout(repo)
    findings = _load_findings(repo)

    notes.append("METHOD: investigating substrate (see references/investigating-substrate.md). "
                 "This is a derivation, not a table lookup.")

    if not manifests:
        notes.append("OBSERVED: no recognized root manifest. SUBSTRATE UNKNOWN — refusing to "
                     "assume a stack. Recording what was observed; you derive and fill the rest.")
        notes.append(f"OBSERVED layout (top dirs): {', '.join(layout) or '(none)'}")
        skeleton = {
            "_substrate": "UNKNOWN — investigated, not yet identified",
            "_investigation": {"manifests": [], "layout": layout},
            "include_ext": ["FILL: source extensions you observe in this repo"],
            "exclude_globs": ["**/.git/**", "FILL: this stack's build/vendor dirs"],
            "layers": {k: ["FILL: dir(s) holding this layer, confirmed against the tree"]
                       for k in ["atomic", "primitive", "seam", "pattern", "pipeline", "scaffold"]},
            "feature_roots": ["FILL: where features/modules live"],
            "verify": [{"name": "FILL", "cmd": "FILL: how THIS repo builds/tests", "must_pass": True}],
        }
        return skeleton, notes

    # Surface the manifest evidence. The ecosystem NAME is Cairn's to infer — the tool
    # reports the evidence and, if Cairn has investigated this manifest-shape before,
    # recalls the owned finding.
    mnames = [m[0] for m in manifests]
    notes.append(f"OBSERVED manifest(s): {', '.join(mnames)}")
    if len(manifests) > 1:
        notes.append("MULTIPLE manifests => likely polyglot/monorepo. Investigate per workspace; "
                     "this draft covers the repo root only.")
    notes.append(f"OBSERVED layout: {', '.join(layout) or '(none)'}")

    # Does Cairn already own a finding that matches this evidence? (recall, not lookup)
    primary_manifest = mnames[0]
    recalled = None
    for sub, f in findings.items():
        if f.get("marker") in mnames:
            recalled = f; break

    if recalled:
        notes.append(f"RECALLED own prior finding for substrate '{recalled['substrate']}' "
                     f"(derived {recalled.get('derived_on','?')}). Re-validate it against this repo's "
                     f"actual layout before trusting — conventions drift.")
        cfg = dict(recalled.get("config_template", {}))
        cfg["_substrate"] = recalled["substrate"]
        cfg["_investigation"] = {"manifests": mnames, "layout": layout, "source": "recalled own finding"}
        return cfg, notes

    # No prior finding: present the evidence as a DERIVATION TASK. The tool writes a
    # scaffold with the observed evidence and explicit DERIVE markers; Cairn fills the
    # conventions from the evidence (that is the act of owning it), then records the
    # finding so next time it is recalled.
    notes.append(f"NO prior finding for manifest '{primary_manifest}'. This is a NEW substrate to "
                 f"investigate: derive its conventions from the manifest contents + observed layout "
                 f"above, fill the DERIVE fields, then record the finding so you own and recall it.")
    notes.append("manifest contents (first 400 chars each):")
    for name, content in manifests:
        notes.append(f"  [{name}] {content.strip()[:200].replace(chr(10),' ')}")

    scaffold = {
        "_substrate": f"DERIVE: name the ecosystem from manifest '{primary_manifest}'",
        "_investigation": {"manifests": mnames, "layout": layout, "source": "new — derive then record"},
        "_record_hint": "after deriving, write this finding to substrate-knowledge.jsonl via "
                        "_record_finding so you recall your OWN derivation next time",
        "include_ext": ["DERIVE: source extensions for this ecosystem, confirmed in the tree"],
        "exclude_globs": ["**/.git/**", "DERIVE: build/vendor/cache dirs for this ecosystem"],
        "layers": {
            "atomic":    ["DERIVE: where domain types/value-objects live (confirm in layout above)"],
            "primitive": ["DERIVE: where basic reusable units live"],
            "seam":      ["DERIVE: where ports/adapters/boundaries live"],
            "pattern":   ["DERIVE: where recurring compositions live"],
            "pipeline":  ["DERIVE: where use-cases/services live"],
            "scaffold":  ["DERIVE: entry points / app shell"],
        },
        "feature_roots": ["DERIVE: where features/modules live"],
        "verify": [{"name": "DERIVE", "cmd": "DERIVE: this repo's build/test command (from the manifest)",
                    "must_pass": True}],
    }
    return scaffold, notes


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Investigate substrate (method, not table) + scaffold a draft config.")
    p.add_argument("--repo", default=".")
    p.add_argument("--out", default=None)
    p.add_argument("--skills-root", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--record", default=None,
                   help="Path to a JSON finding to record into substrate-knowledge.jsonl (after deriving).")
    args = p.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: repo {repo} not found", file=sys.stderr); return 2

    # recording mode: Cairn writes a finding it derived, so it owns + recalls it
    if args.record:
        try:
            finding = json.loads(Path(args.record).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"error: cannot read finding json {args.record}: {e}", file=sys.stderr); return 2
        if not isinstance(finding, dict):
            print("error: finding json must be an object", file=sys.stderr); return 2
        if "substrate" not in finding:
            print("error: a finding must have a 'substrate' name", file=sys.stderr); return 2
        finding.setdefault("derived_on", __import__("datetime").date.today().isoformat())
        _record_finding(repo, finding)
        print(f"recorded finding for substrate '{finding['substrate']}' — Cairn now owns and will recall it.")
        return 0

    out = Path(args.out).resolve() if args.out else repo / "boundary.config.json"
    if out.exists() and not args.force:
        print(f"error: {out} exists. Use --force to overwrite, or edit it directly.", file=sys.stderr); return 1

    cfg, notes = build_investigation(repo)
    out.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    try:
        mirror_msg = mirror_scripts(repo, args.skills_root)
    except OSError as e:
        print(f"error: cannot mirror harness scripts: {e}", file=sys.stderr); return 2

    sub = cfg.get("_substrate", "")
    flag = ""
    if sub.startswith("UNKNOWN"): flag = "  [UNKNOWN — investigated, not identified]"
    elif sub.startswith("DERIVE"): flag = "  [NEW substrate — derive the DERIVE fields, then record]"
    print(f"drafted {out}{flag}\n")
    if mirror_msg:
        print(mirror_msg)
        print("")
    print("investigation report (this is a derivation — confirm/derive against the real repo):")
    for n in notes:
        print(f"  - {n}")
    print(f"\nnext: derive/confirm the fields, (if new) record your finding with --record,")
    print(f"      then validate it resolves: python {Path(__file__).with_name('config_check.py')} --repo {repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

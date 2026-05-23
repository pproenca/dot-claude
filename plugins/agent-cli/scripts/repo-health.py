#!/usr/bin/env python3
"""repo-health: diagnose an agent-CLI repo the way the OpenClaw projects evolve.

Derived from analysis of openclaw/clawpatch, openclaw/crabbox, openclaw/clawsweeper.
Prints the signals that tell you HOW a repo is being built and where to invest:

  - commit-type distribution + feat:fix ratio (hardening pressure)
  - feat:fix ratio per scope (which subsystems are fragile)
  - churn concentration ("where the real spec lives")
  - deletion bursts (refactor cadence)
  - maintainer days (high commits / low churn = merge+changelog days)
  - bot vs human split (autonomous-loop detection)

Usage:
  python3 repo-health.py <repo_path> [--bots-separate] [--emit-csv DIR]
"""
import argparse
import csv
import os
import re
import subprocess
from collections import Counter, defaultdict

TYPE_RE = re.compile(r"^([a-z]+)(?:\(([^)]*)\))?(!)?:")
SENTINEL = "@@C@@"


def classify(subject):
    if subject.startswith("Merge "):
        return "merge", ""
    m = TYPE_RE.match(subject)
    if m:
        return m.group(1), (m.group(2) or "")
    return "other", ""


def is_bot(author):
    a = author.lower()
    return "bot]" in a or a.endswith("[bot]") or "github-actions" in a


def load(repo):
    fmt = SENTINEL + "\t%h\t%ad\t%an\t%P\t%s"
    out = subprocess.run(
        ["git", "-C", repo, "log", "--reverse", "--numstat",
         "--date=short", f"--format={fmt}"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    commits, cur = [], None
    for line in out:
        if line.startswith(SENTINEL):
            if cur:
                commits.append(cur)
            _, h, date, author, parents, subject = line.split("\t", 5)
            t, scope = classify(subject)
            cur = {"hash": h, "date": date, "author": author, "type": t,
                   "scope": scope, "is_merge": len(parents.split()) > 1,
                   "is_bot": is_bot(author), "subject": subject,
                   "files": [], "ins": 0, "dele": 0}
        elif line.strip() and cur is not None:
            p = line.split("\t")
            if len(p) >= 3:
                a = 0 if p[0] == "-" else int(p[0])
                d = 0 if p[1] == "-" else int(p[1])
                path = "\t".join(p[2:])
                cur["files"].append(path)
                cur["ins"] += a
                cur["dele"] += d
    if cur:
        commits.append(cur)
    return commits


def bar(frac, width=24):
    n = int(round(frac * width))
    return "█" * n + "·" * (width - n)


def report(commits, label):
    n = len(commits)
    if n == 0:
        print(f"  ({label}: no commits)")
        return
    types = Counter(c["type"] for c in commits)
    feat = types.get("feat", 0)
    fix = types.get("fix", 0)
    ratio = f"1:{fix/feat:.1f}" if feat else "n/a"
    print(f"\n## {label}  ({n} commits)")
    print(f"  feat:fix ratio = {ratio}   (feat={feat}, fix={fix})")
    print("  type distribution:")
    for t, c in types.most_common():
        print(f"    {t:10s} {c:6d}  {c/n*100:5.1f}%  {bar(c/n)}")

    # feat:fix per scope
    scope_feat = Counter(c["scope"] for c in commits if c["type"] == "feat" and c["scope"])
    scope_fix = Counter(c["scope"] for c in commits if c["type"] == "fix" and c["scope"])
    scopes = sorted(set(scope_feat) | set(scope_fix),
                    key=lambda s: scope_feat[s] + scope_fix[s], reverse=True)[:8]
    if scopes:
        print("  feat:fix by scope (fragility — high fix-per-feat = needs a test sweep):")
        for s in scopes:
            f, x = scope_feat[s], scope_fix[s]
            r = f"1:{x/f:.1f}" if f else f"0:{x}"
            print(f"    {s:14s} feat={f:3d} fix={x:3d}  ratio {r}")

    # churn concentration
    touches = Counter()
    for c in commits:
        for p in set(c["files"]):
            touches[p] += 1
    if touches:
        print("  churn concentration (the real spec lives in the top files):")
        for p, c in touches.most_common(8):
            print(f"    {c:5d}  {p}")

    # deletion / refactor cadence
    by_day_del = defaultdict(int)
    by_day_n = Counter()
    by_day_ins = defaultdict(int)
    for c in commits:
        by_day_del[c["date"]] += c["dele"]
        by_day_ins[c["date"]] += c["ins"]
        by_day_n[c["date"]] += 1
    total_del = sum(by_day_del.values()) or 1
    top_del = sorted(by_day_del.items(), key=lambda kv: kv[1], reverse=True)[:3]
    print("  deletion bursts (refactor days — should be spiky, never flat-zero):")
    for d, dele in top_del:
        print(f"    {d}: -{dele:<6d} ({dele/total_del*100:.0f}% of all deletions, {by_day_n[d]} commits)")

    # maintainer days
    maint = [(d, by_day_n[d], by_day_ins[d] + by_day_del[d])
             for d in by_day_n if by_day_n[d] >= 8]
    maint = [m for m in maint if m[2] < 600]
    if maint:
        print("  maintainer days (many commits, little code = merge/changelog sessions):")
        for d, cn, churn in sorted(maint, key=lambda m: m[1], reverse=True)[:3]:
            print(f"    {d}: {cn} commits, only {churn} lines changed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--bots-separate", action="store_true",
                    help="split human vs bot commits (autonomous-loop repos)")
    ap.add_argument("--emit-csv", metavar="DIR",
                    help="also write per-commit + per-file CSVs to DIR")
    args = ap.parse_args()

    commits = load(args.repo)
    bots = [c for c in commits if c["is_bot"]]
    print(f"# repo-health: {os.path.abspath(args.repo)}")
    print(f"  total commits: {len(commits)}   "
          f"range: {commits[0]['date']} → {commits[-1]['date']}   "
          f"bot commits: {len(bots)} ({len(bots)/len(commits)*100:.0f}%)")

    if args.bots_separate:
        report([c for c in commits if not c["is_bot"]], "HUMAN commits")
        report(bots, "BOT commits")
    else:
        report(commits, "ALL commits")

    if args.emit_csv:
        os.makedirs(args.emit_csv, exist_ok=True)
        with open(os.path.join(args.emit_csv, "commits.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["hash", "date", "author", "type", "scope",
                        "is_merge", "is_bot", "files", "ins", "del", "subject"])
            for c in commits:
                w.writerow([c["hash"], c["date"], c["author"], c["type"], c["scope"],
                            int(c["is_merge"]), int(c["is_bot"]), len(c["files"]),
                            c["ins"], c["dele"], c["subject"]])
        print(f"\n  wrote {os.path.join(args.emit_csv, 'commits.csv')}")


if __name__ == "__main__":
    main()

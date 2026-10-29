#!/usr/bin/env python3
"""The translator's work list: French files missing, untracked, stale or orphaned against fr/translated_from.json.

The manifest maps each English source path (relative to the repository root) to the commit it was translated from.
Usage: python3 _book/stale.py   -> report on stdout, exit 1 if anything is listed. Not run in CI (see FRENCH-SPEC.md).
"""
import json, pathlib, subprocess, sys

import build, hexo
from build import ROOT

MANIFEST = "translated_from.json"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def contains(commit, other):
    """True when `other` is an ancestor of (or equal to) `commit`."""
    return subprocess.run(["git", "merge-base", "--is-ancestor", other, commit], cwd=ROOT, capture_output=True).returncode == 0


def english_sources():
    """Relative paths in translator order: index.html, every include (first seen), then the pages in walk order. Never LICENSE."""
    pages, includes = [], []
    for p in hexo.guide_pages():
        if p.url == "/license":
            continue
        for src in hexo.sources(p):
            rel = src.relative_to(ROOT)
            (includes if rel.parts[0] == "_includes" else pages).append(rel)
    return list(dict.fromkeys([pathlib.Path("index.html"), *includes, *pages]))


def current_sha(rel):
    """Full sha of the last commit touching rel; "" when it was never committed."""
    return git("log", "-1", "--format=%H", "--", str(rel))


def report(out=print):
    fr = build.FR
    try:
        manifest = json.loads((fr / MANIFEST).read_text())
    except (OSError, ValueError):
        manifest = {}
    sources = english_sources()
    listed = 0
    for rel in sources:
        if not (fr / rel).exists():
            out(f"MISSING {rel}")
        elif str(rel) not in manifest:
            out(f"UNTRACKED {rel}")
        else:
            recorded, current = str(manifest[str(rel)]), current_sha(rel)
            known = git("rev-parse", "--verify", "--quiet", f"{recorded}^{{commit}}")
            if known and current and contains(known, current):  # translated at or after the file's last change
                continue
            out(f"STALE {rel}: {recorded[:7]} -> {current[:7]}")
            if known:
                for line in git("log", "--oneline", f"{known}..{current}", "--", str(rel)).splitlines():
                    out("  " + line)
            else:
                out("  (recorded commit unknown)")
        listed += 1
    known_sources = set(sources)
    for f in sorted(fr.rglob("*")) if fr.is_dir() else []:
        rel = f.relative_to(fr)
        if f.is_file() and rel.name != MANIFEST and rel not in known_sources:
            out(f"ORPHAN fr/{rel}")
            listed += 1
    if not listed:
        out("all French files up to date")
    return 1 if listed else 0


if __name__ == "__main__":
    sys.exit(report())

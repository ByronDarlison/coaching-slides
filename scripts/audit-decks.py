#!/usr/bin/env python3
"""audit-decks.py — source-level integrity checks for the M3-M13 decks.

Three checks, each reporting per-month deltas:

  1. TABLE CONSISTENCY
     Every (deliverable, month) cell in
     ~/ai-config/darlison/coaching-deliverables.md (Monthly View)
     matches a D() entry in MEETINGS[N] in build_slideshows.py with the
     same symbol, and vice versa. Catches "deck drifted from the table"
     of which the May-2026 reconciliation surfaced 171 instances.

  2. BUILD ROUND-TRIP
     For each MEETINGS[N], render via build_html() into memory and diff
     against the checked-in monthly/m{N}/index.html. Catches hand-edits
     to HTML that aren't reflected in the build script (the May-2026
     "live deploy doesn't match my edits" failure mode).

  3. CANONICAL ORDERING
     When KFFM, FOC, and FAC all appear in a month, they appear in that
     order. Catches the M3 "FAC before FOC" slip from May-2026.

Per-deck checks (time-chain, image URLs, structure, style, cohort-generic)
are handled by scripts/slide-test.py and run separately.

Usage:
    python3 scripts/audit-decks.py [--repo PATH] [--table PATH]

Exit code:
    0  PASS — every month clean on every check
    1  FAIL — at least one check reported issues; details on stdout
    2  Bad input (missing file, parse failure, etc.)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


# ─── 1. TABLE CONSISTENCY ─────────────────────────────────────────────

# The deck and the table use slightly different display names for the
# same deliverable. Normalize the deck name to the table name before
# comparing. Keep this list narrow — every alias is a place where the
# deck and the source-of-truth use different strings on purpose.
DECK_TO_TABLE_ALIAS = {
    "Org Function Chart": "Functional Organization Chart (FOC)",
    "Functional Organization Chart (FOC)": "Functional Organization Chart (FOC)",
    "Functional Accountability Chart": "Functional Accountability Chart",
    "Functional Accountability Chart (FAC)": "Functional Accountability Chart",
    "Key Function Flow Map (KFFM)": "KFFM",
    "KFFM": "KFFM",
    "QHAG + Sprint Lanes": "QHAG + 13-Week Sprint Lanes",
    "QHAG + 13-Week Sprint Lanes": "QHAG + 13-Week Sprint Lanes",
    "1HAG": "1HAG",
    "1-Year Highly Achievable Goal (1HAG)": "1HAG",
    "3HAG": "3HAG",
    "3-Year Highly Achievable Goal (3HAG)": "3HAG",
    "Activity Fit Map": "Activity Fit Map (Differentiators)",
    "Activity Fit Map (Differentiators)": "Activity Fit Map (Differentiators)",
}


def canon(name: str) -> str:
    return DECK_TO_TABLE_ALIAS.get(name, name)


def parse_table(table_path: Path) -> dict[tuple[str, int], str]:
    """Return {(deliverable_name, month_num): symbol} for the Monthly View."""
    text = table_path.read_text()
    m = re.search(r"## Monthly View\s*\n(.+?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        sys.exit(f"audit-decks: 'Monthly View' section not found in {table_path}")
    block = m.group(1)
    lines = [l for l in block.splitlines() if l.strip().startswith("|")]
    if len(lines) < 3:
        sys.exit(f"audit-decks: Monthly View table has too few rows in {table_path}")
    header = [c.strip() for c in lines[0].split("|")[1:-1]]
    month_cols = [(i, int(c[1:])) for i, c in enumerate(header) if re.match(r"^M\d+$", c)]

    out: dict[tuple[str, int], str] = {}
    for row in lines[2:]:  # row 1 is the alignment row
        cells = [c.strip() for c in row.split("|")[1:-1]]
        if len(cells) != len(header):
            continue
        deliverable = cells[0]
        for col_idx, n in month_cols:
            sym = cells[col_idx]
            if sym:
                out[(deliverable, n)] = sym
    return out


def parse_meetings(build_src: str) -> dict[int, list[tuple[str, str]]]:
    """Extract per-month [(name, symbol), ...] from MEETINGS[N] = {...} blocks."""
    out: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for blk in re.finditer(r"MEETINGS\[(\d+)\]\s*=\s*\{(.+?)\n\}\s*\n", build_src, re.DOTALL):
        n = int(blk.group(1))
        body = blk.group(2)
        for d in re.finditer(r'D\(\s*"([^"]+)"\s*,\s*"([^"]+)"', body):
            out[n].append((d.group(1), d.group(2)))
    return out


def check_table_consistency(table_cells, deck_meetings) -> list[str]:
    """Per-month diff between table and deck. Returns list of issue lines."""
    issues: list[str] = []
    for n in sorted(deck_meetings.keys()):
        deck_names = {canon(name): sym for name, sym in deck_meetings[n]}
        table_names = {d: s for (d, m), s in table_cells.items() if m == n}

        for d, s in table_names.items():
            if d not in deck_names:
                issues.append(f"M{n}: MISSING (in table, not in deck): {d} ({s})")
            elif deck_names[d] != s:
                issues.append(f"M{n}: WRONG SYMBOL: {d}: table={s} deck={deck_names[d]}")
        for d, s in deck_names.items():
            if d not in table_names:
                issues.append(f"M{n}: EXTRA (in deck, not in table): {d} ({s})")
    return issues


# ─── 2. BUILD ROUND-TRIP ──────────────────────────────────────────────

def check_build_roundtrip(repo: Path) -> list[str]:
    """Render each MEETINGS[N] in memory and diff vs. checked-in HTML."""
    issues: list[str] = []
    # Import the build module from the repo. Override BASE_DIR so any
    # path-relative logic stays self-contained, then call build_html()
    # for each meeting and compare to the checked-in file.
    sys.path.insert(0, str(repo))
    try:
        import importlib
        if "build_slideshows" in sys.modules:
            del sys.modules["build_slideshows"]
        bs = importlib.import_module("build_slideshows")
    except Exception as e:
        return [f"build-roundtrip: failed to import build_slideshows.py: {e}"]
    finally:
        sys.path.pop(0)

    bs.BASE_DIR = str(repo)
    bs.MONTHLY_DIR = str(repo / "monthly")

    for n, meeting in sorted(bs.MEETINGS.items()):
        rendered = bs.build_html(meeting)
        out_path = repo / "monthly" / f"m{n}" / "index.html"
        if not out_path.exists():
            issues.append(f"M{n}: round-trip: {out_path.relative_to(repo)} missing")
            continue
        on_disk = out_path.read_text(encoding="utf-8")
        if rendered != on_disk:
            issues.append(
                f"M{n}: round-trip: rendered build_html(MEETINGS[{n}]) differs from "
                f"checked-in {out_path.relative_to(repo)} "
                f"(rendered={len(rendered)} chars, on-disk={len(on_disk)} chars). "
                "Re-run the build or revert hand-edits."
            )
    return issues


# ─── 3. CANONICAL ORDERING ────────────────────────────────────────────

def check_canonical_ordering(deck_meetings) -> list[str]:
    """When KFFM, FOC, and FAC all appear in a month, they must appear in
    that order. Catches the May-2026 "FAC before FOC" slip."""
    issues: list[str] = []
    for n in sorted(deck_meetings.keys()):
        positions: dict[str, int] = {}
        for i, (name, _sym) in enumerate(deck_meetings[n]):
            cn = canon(name)
            if cn in ("KFFM", "Functional Organization Chart (FOC)",
                      "Functional Accountability Chart") and cn not in positions:
                positions[cn] = i
        kffm = positions.get("KFFM")
        foc = positions.get("Functional Organization Chart (FOC)")
        fac = positions.get("Functional Accountability Chart")
        if kffm is not None and foc is not None and kffm > foc:
            issues.append(f"M{n}: ORDERING: KFFM (pos {kffm}) must come before FOC (pos {foc})")
        if foc is not None and fac is not None and foc > fac:
            issues.append(f"M{n}: ORDERING: FOC (pos {foc}) must come before FAC (pos {fac})")
        if kffm is not None and fac is not None and kffm > fac:
            issues.append(f"M{n}: ORDERING: KFFM (pos {kffm}) must come before FAC (pos {fac})")
    return issues


# ─── runner ───────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--repo", default=".",
                   help="Path to the coaching-slides repo (default: cwd)")
    p.add_argument("--table", default=None,
                   help="Path to the deliverables table markdown. Defaults to "
                        "tests/deliverables-snapshot.md (in-repo, used by CI) if "
                        "present, else ~/ai-config/darlison/coaching-deliverables.md "
                        "(canonical, local).")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    build_path = repo / "build_slideshows.py"
    if args.table:
        table_path = Path(args.table).expanduser()
    else:
        snapshot = repo / "tests" / "deliverables-snapshot.md"
        canonical = Path("~/ai-config/darlison/coaching-deliverables.md").expanduser()
        table_path = snapshot if snapshot.exists() else canonical

    if not build_path.exists():
        print(f"audit-decks: missing {build_path}", file=sys.stderr)
        return 2
    if not table_path.exists():
        print(f"audit-decks: missing {table_path}", file=sys.stderr)
        return 2

    table_cells = parse_table(table_path)
    deck_meetings = parse_meetings(build_path.read_text())

    sections: list[tuple[str, list[str]]] = [
        ("TABLE CONSISTENCY", check_table_consistency(table_cells, deck_meetings)),
        ("BUILD ROUND-TRIP", check_build_roundtrip(repo)),
        ("CANONICAL ORDERING", check_canonical_ordering(deck_meetings)),
    ]

    total = sum(len(v) for _, v in sections)
    print(f"=== audit-decks — repo={repo}")
    print(f"    table={table_path}")
    print()
    for label, issues in sections:
        if not issues:
            print(f"  [{label}] PASS")
            continue
        print(f"  [{label}] FAIL — {len(issues)} issue(s)")
        for line in issues:
            print(f"      {line}")
    print()
    if total == 0:
        print(f"PASS: all {len(deck_meetings)} months clean on all 3 checks.")
        return 0
    print(f"FAIL: {total} issue(s) total across {len(deck_meetings)} months.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

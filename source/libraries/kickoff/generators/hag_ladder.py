#!/usr/bin/env python3
"""Draw the planning cascade used beside the "pass?" check slides. Names only, large enough to read in the side panel.
Run from this folder: python3 generators/hag_ladder.py"""
import re, pathlib
HERE = pathlib.Path(__file__).resolve().parent.parent / "assets"
STYLE = re.search(r"<style>.*?</style>", (HERE / "q1-path-status.svg").read_text(), flags=re.S).group(0)
LEVELS = ["BHAG", "3HAG", "1HAG", "QHAG", "Priorities"]
W, H, BW, BH, GAP, TOP = 300, 680, 276, 104, 30, 20
FILES = {"hag-ladder-checked-3hag.svg": 1, "hag-ladder-checked-1hag.svg": 2, "hag-ladder-checked-qhag.svg": 3, "hag-ladder-checked.svg": 4}

def draw(checked_to):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{STYLE}<rect width="{W}" height="{H}" fill="white"/>']
    x = (W - BW) / 2
    for i, name in enumerate(LEVELS):
        y = TOP + i * (BH + GAP); cy = y + BH / 2
        checked = 1 <= i <= checked_to
        if i < len(LEVELS) - 1:
            col = "#318549" if (checked and i + 1 <= checked_to) else "#9aa3ab"
            out.append(f'<line x1="{W/2}" y1="{y+BH}" x2="{W/2}" y2="{y+BH+GAP-9}" stroke="{col}" stroke-width="5"/>'
                       f'<path d="M{W/2-10},{y+BH+GAP-13} L{W/2},{y+BH+GAP-1} L{W/2+10},{y+BH+GAP-13} Z" fill="{col}"/>')
        if checked:
            out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="16" fill="#e7f2ea" stroke="#318549" stroke-width="4"/>')
            out.append(f'<text x="{x+26}" y="{cy+14}" font-size="37" font-weight="700" fill="#20282f">{name}</text>')
            out.append(f'<text x="{x+BW-26}" y="{cy+15}" font-size="42" font-weight="700" fill="#318549" text-anchor="end">✓</text>')
        elif i == 0:
            out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="16" fill="white" stroke="#326ab6" stroke-width="4"/>')
            out.append(f'<text x="{x+26}" y="{cy+14}" font-size="37" font-weight="700" fill="#326ab6">{name}</text>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="16" fill="white" stroke="#9aa3ab" stroke-width="3"/>')
            out.append(f'<text x="{x+26}" y="{cy+14}" font-size="37" font-weight="600" fill="#5b6670">{name}</text>')
    out.append("</svg>")
    return "".join(out)

for f, n in FILES.items():
    (HERE / f).write_text(draw(n))
print("wrote", len(FILES), "cascades")

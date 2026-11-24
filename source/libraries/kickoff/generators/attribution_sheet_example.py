#!/usr/bin/env python3
"""Draw the Attribution Map sheet's score table for the example company, from the scores in the example graph.
Column names match the real Google Sheet. Run from this folder: python3 generators/attribution_sheet_example.py"""
import re, pathlib
A = pathlib.Path(__file__).resolve().parent.parent / "assets"
STYLE = re.search(r"<style>.*?</style>", (A / "q1-path-status.svg").read_text(), flags=re.S).group(0)
graph = re.sub(r"<style>.*?</style>", "", (A / "attribution-example.svg").read_text(), flags=re.S)
lines = [[float(p.split(",")[1]) for p in m.group(1).split()] for m in re.finditer(r'<polyline points="([^"]+)"', graph)]
score = lambda y: round(5 - (y - 112) / 90)
NAMES = ["Speed of setup", "Ease of use", "Price predictability", "Reliability", "Billing simplicity", "Support from a person",
         "Security", "Integrations", "Reporting", "Feature breadth", "Customization", "Partner network"]
COLS = ["Your Company\nToday", "Competitor 1", "Competitor 2", "Competitor 3", "3HAG Line"]
W, H = 1440, 760
X0, CW0, CW, Y0, HH, RH = 60, 420, 180, 132, 78, 44
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{STYLE}<rect width="{W}" height="{H}" fill="white"/>',
       f'<text x="{X0}" y="52" font-size="34" font-weight="700" fill="#20282f">Attribution Map</text>',
       f'<text x="{X0}" y="96" font-size="26" font-weight="500" fill="#5b6670">Score 1 to 5, in any order. The chart sorts itself.</text>',
       f'<rect x="{X0}" y="{Y0}" width="{CW0+CW*len(COLS)}" height="{HH}" fill="#c9d7ef"/>',
       f'<text x="{X0+16}" y="{Y0+48}" font-size="26" font-weight="700" fill="#20282f">Attribute</text>']
for c, name in enumerate(COLS):
    cx = X0 + CW0 + c * CW + CW / 2
    parts = name.split("\n")
    for k, t in enumerate(parts):
        y = Y0 + (34 if len(parts) == 2 else 48) + k * 30
        out.append(f'<text x="{cx}" y="{y}" font-size="24" font-weight="700" fill="#20282f" text-anchor="middle">{t}</text>')
for r, name in enumerate(NAMES):
    y = Y0 + HH + r * RH
    if r % 2: out.append(f'<rect x="{X0}" y="{y}" width="{CW0+CW*len(COLS)}" height="{RH}" fill="#f6f4ef"/>')
    out.append(f'<text x="{X0+16}" y="{y+31}" font-size="26" font-weight="500" fill="#20282f">{name}</text>')
    for c in range(4):
        cx = X0 + CW0 + c * CW + CW / 2
        out.append(f'<text x="{cx}" y="{y+31}" font-size="27" font-weight="700" fill="{"#326ab6" if c == 0 else "#20282f"}" text-anchor="middle">{score(lines[c][r])}</text>')
bottom = Y0 + HH + len(NAMES) * RH
for c in range(len(COLS) + 1):
    x = X0 + CW0 + c * CW
    out.append(f'<line x1="{x}" y1="{Y0}" x2="{x}" y2="{bottom}" stroke="#d5d9dd" stroke-width="2"/>')
out.append(f'<rect x="{X0}" y="{Y0}" width="{CW0+CW*len(COLS)}" height="{bottom-Y0}" fill="none" stroke="#9aa3ab" stroke-width="2"/>')
out.append(f'<text x="{X0+CW0+4*CW+CW/2}" y="{Y0+HH+6*RH+8}" font-size="22" font-weight="500" fill="#9aa3ab" text-anchor="middle" transform="rotate(-90 {X0+CW0+4*CW+CW/2} {Y0+HH+6*RH})">filled in later</text>')
out.append("</svg>")
(A / "attribution-sheet-example.svg").write_text("".join(out))
print("wrote attribution-sheet-example.svg", [[score(v) for v in l] for l in lines[:4]])

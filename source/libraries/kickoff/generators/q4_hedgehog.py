#!/usr/bin/env python3
"""Draw the Hedgehog: three overlapping circles with the BHAG where they meet.
Run from the library folder: python3 generators/q4_hedgehog.py"""
from q4_common import svg, write, text, BLUE, DGREEN, INK
W, H = 1440, 830
R, DX, TOPY, LOWY, CX = 262, 170, 274, 556, 720
TEAL = "#438f93"
CIRCLES = [("Core Purpose", ["Why does the", "company exist?"], CX, TOPY, BLUE, CX, 112),
           ("Core Business", ["What is the company's", "core business?"], CX - DX, LOWY, DGREEN, CX - DX - 80, 632),
           ("Economic Engine", ["What is the company's", "Profit per X?"], CX + DX, LOWY, TEAL, CX + DX + 80, 632)]
REGIONS = {}
out = []
for _, _, x, y, colour, _, _ in CIRCLES:
    out.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{colour}" fill-opacity=".13"/>')
for _, _, x, y, colour, _, _ in CIRCLES:
    out.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="none" stroke="{colour}" stroke-width="5"/>')
for name, question, _, _, colour, tx, ty in CIRCLES:
    out.append(text(tx, ty, name, 34, 700, INK))
    for k, t in enumerate(question):
        out.append(text(tx, ty + 44 + k * 32, t, 25, 500, INK))
    REGIONS[name] = [tx - 150, ty - 40, 300, 130]
BX, BY, BR = CX, TOPY + (LOWY - TOPY) * 2 / 3, 128
out.append(f'<circle cx="{BX}" cy="{BY:g}" r="{BR}" fill="{BLUE}" stroke="white" stroke-width="5"/>')
out.append(text(BX, BY - 14, "BHAG", 48, 700, "white"))
out.append(text(BX, BY + 28, "10 to 30 year goal", 23, 600, "white"))
out.append(text(BX, BY + 60, "No numbers", 23, 600, "white"))
REGIONS["BHAG"] = [BX - BR, round(BY - BR), 2 * BR, 2 * BR]
write("q4-hedgehog.svg", svg(W, H, "".join(out)))
print("wrote q4-hedgehog.svg")

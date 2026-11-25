#!/usr/bin/env python3
"""Draw the five-level team pyramid with its score key.
Run from the library folder: python3 generators/q4_five_dysfunctions.py"""
from q4_common import svg, write, text, SEQ, INK, GREY, LINE
W, H = 1440, 730
LEVELS = ["Trust", "Conflict", "Commitment", "Accountability", "Results"]  # bottom to top
CX, TOP, BOT, HALF_TOP, HALF_BOT, GAP = 580, 40, 640, 130, 480, 6
BAND = (BOT - TOP) / 5
half = lambda y: HALF_TOP + (y - TOP) / (BOT - TOP) * (HALF_BOT - HALF_TOP)
REGIONS = {}
out = []
for i, name in enumerate(LEVELS):
    y2 = BOT - i * BAND; y1 = y2 - BAND + GAP
    out.append(f'<path d="M{CX-half(y1):g},{y1:g} L{CX+half(y1):g},{y1:g} L{CX+half(y2):g},{y2:g} L{CX-half(y2):g},{y2:g} Z" fill="{SEQ[i]}"/>')
    out.append(text(CX, (y1 + y2) / 2 + 14, name, 40, 700, INK if i < 3 else "white"))  # ink on the green bands, white on the blue
    REGIONS[name] = [round(CX - half(y2)), round(y1), round(2 * half(y2)), round(y2 - y1)]
out.append(text(CX, 692, "Start at the bottom.", 26, 500, GREY))
KX = 1110
out.append(f'<line x1="{KX-24}" y1="236" x2="{KX-24}" y2="444" stroke="{LINE}" stroke-width="4"/>')
out.append(text(KX, 270, "Team score", 32, 700, INK, "start"))
for k, t in enumerate(["High: 4 and above", "Medium: 3 to 3.99", "Low: under 3"]):
    out.append(text(KX, 330 + k * 50, t, 27, 500, INK, "start"))
write("q4-five-dysfunctions.svg", svg(W, H, "".join(out)))
print("wrote q4-five-dysfunctions.svg")

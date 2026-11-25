#!/usr/bin/env python3
"""Draw the parts of the 3HAG, names only, for a narrow side panel: one part at full strength, the rest dimmed
(slide standard rules 9 and 38). The order is the order the deck works in: the differentiators go in last. Run from the library folder:
python3 generators/q4_3hag_focus.py"""
from q4_common import svg, write, text, BLUE, INK, LINE, CANVAS, MID
W, H, X, BW, BH, GAP, TOP = 900, 830, 120, 660, 116, 22, 128
PARTS = [("date", "End date"), ("numbers", "Numbers"), ("statement", "Statement"),
         ("known-for", "Known for"), ("differentiators", "Differentiators")]

def draw(focus):
    out = [text(X, 84, "3HAG", 44, 700, MID, "start", ' letter-spacing="2"')]
    for k, (key, name) in enumerate(PARTS):
        y, on = TOP + k * (BH + GAP), key == focus
        dim = "" if on else ' opacity=".3"'
        fill, stroke, ink = (BLUE, BLUE, "white") if on else (CANVAS, LINE, INK)
        out.append(f'<g{dim}><rect x="{X}" y="{y}" width="{BW}" height="{BH}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
                   + text(X + BW / 2, y + BH / 2 + 16, name, 46, 700, ink) + "</g>")
    return svg(W, H, "".join(out))

for key in ("numbers", "statement", "known-for", "differentiators"):
    write(f"q4-3hag-focus-{key}.svg", draw(key))
print("wrote four 3HAG focus variants")

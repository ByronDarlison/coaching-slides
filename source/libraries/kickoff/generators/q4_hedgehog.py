#!/usr/bin/env python3
"""Draw the Hedgehog: three overlapping circles with the BHAG where they meet.
Writes the full drawing, and three names-only focus variants for a narrow side panel, each with one part
at full strength and the rest dimmed. Run from the library folder: python3 generators/q4_hedgehog.py"""
from q4_common import svg, write, text, block, BLUE, DGREEN, INK
R, DX, TOPY, LOWY = 262, 170, 274, 556
TEAL = "#438f93"
BY, BR = TOPY + (LOWY - TOPY) * 2 / 3, 140
# name, question, centre x offset, centre y, colour, label x offset, label y, name wrapped for the focus variants
CIRCLES = [("Core Purpose", ["Why does the", "company exist?"], 0, TOPY, BLUE, 0, 112, ["Core Purpose"]),
           ("Core business", ["What is the company's", "core business?"], -DX, LOWY, DGREEN, -DX - 80, 632, ["Core", "business"]),
           ("Economic engine", ["What is the company's", "Profit per X?"], DX, LOWY, TEAL, DX + 80, 632, ["Economic", "engine"])]
REGIONS = {}

def draw(w, h, focus=None):
    """focus None: the full drawing with questions. Otherwise names only, with that part bright and the rest dimmed."""
    cx, full = w / 2, focus is None
    out = []
    for name, question, ox, y, colour, tx, ty, short in CIRCLES:
        dim = "" if full or focus == name else ' opacity=".3"'
        out.append(f'<g{dim}><circle cx="{cx+ox:g}" cy="{y}" r="{R}" fill="{colour}" fill-opacity=".13"/>'
                   f'<circle cx="{cx+ox:g}" cy="{y}" r="{R}" fill="none" stroke="{colour}" stroke-width="5"/>')
        if full:
            out.append(text(cx + tx, ty, name, 34, 700, INK))
            out += [text(cx + tx, ty + 44 + k * 32, t, 25, 500, INK) for k, t in enumerate(question)]
            REGIONS[name] = [round(cx + tx - 150), ty - 40, 300, 130]
        else:
            out.append(block(cx + tx, ty + (26 if len(short) == 1 else 22), short, 40, 46, weight=700, fill=INK))
        out.append("</g>")
    dim = "" if full or focus == "BHAG" else ' opacity=".3"'
    out.append(f'<g{dim}><circle cx="{cx:g}" cy="{BY:g}" r="{BR}" fill="{BLUE}" stroke="white" stroke-width="5"/>')
    if full:
        out.append(text(cx, BY - 16, "BHAG", 50, 700, "white"))
        out.append(text(cx, BY + 30, "10 to 30 year goal", 25, 600, "white"))
        out.append(text(cx, BY + 64, "No numbers", 25, 600, "white"))
        REGIONS["BHAG"] = [round(cx - BR), round(BY - BR), 2 * BR, 2 * BR]
    else:
        out.append(text(cx, BY + 20, "BHAG", 56, 700, "white"))
    out.append("</g>")
    return svg(w, h, "".join(out))

write("q4-hedgehog.svg", draw(1440, 830))
for key, part in (("business", "Core business"), ("engine", "Economic engine"), ("goal", "BHAG")):
    write(f"q4-hedgehog-focus-{key}.svg", draw(900, 830, part))
print("wrote q4-hedgehog.svg and three focus variants")

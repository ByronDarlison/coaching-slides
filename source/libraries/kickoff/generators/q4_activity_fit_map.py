#!/usr/bin/env python3
"""Draw the example Activity Fit Map the way Shannon Susko's book and the strategy site draw it (Porter's
activity system). Level 1: the differentiators as large circles, with a line between two that depend on each
other. Level 2: the supporting activities as small circles around each differentiator. The centre stays empty:
the One-Phrase Strategy goes there later. Run from the library folder: python3 generators/q4_activity_fit_map.py"""
import math
from q4_common import svg, write, text, block, BLUE, CORNER
HUB_FILL, HUB_TEXT = "#E9F0FA", "#1F3F6E"
NODE_FILL, NODE_STROKE, NODE_TEXT, SPOKE = "#F4F6F8", "#8997A5", "#263746", "#B7C0C9"
# name lines, corner, activities (line breaks set by hand)
MAP = [(["A Named", "Person for", "90 Days"], "TL", [["One contact", "from sign-up"], ["A call in", "week one"], ["Answers in", "one business", "day"]]),
       (["Live in", "a Day"], "TR", [["Guided", "setup"], ["Ready-made", "templates"], ["Automatic", "data import"]]),
       (["One Flat", "Price"], "BL", [["One plan"], ["No add-ons"], ["Automatic", "billing"]]),
       (["Standard,", "Not Custom"], "BR", [["One product", "for everyone"], ["No custom", "work"], ["A short,", "fixed", "report set"]])]
# A Named Person for 90 Days depends on Live in a Day. Live in a Day and One Flat Price both depend on Standard, Not Custom.
LINKS = [("TL", "TR"), ("TR", "BR"), ("BL", "BR")]

def link(a, b, r, width):
    (x1, y1), (x2, y2) = a, b
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return f'<line x1="{x1 + ux * r:g}" y1="{y1 + uy * r:g}" x2="{x2 - ux * r:g}" y2="{y2 - uy * r:g}" stroke="{BLUE}" stroke-width="{width}" stroke-linecap="round"/>'

# Where the three activities sit around a top-left differentiator. The other corners mirror this.
SPREAD = [(-170, -95), (-195, 60), (140, -100)]
FLIP = {"TL": (1, 1), "TR": (-1, 1), "BL": (1, -1), "BR": (-1, -1)}

def draw(w, h, at, r, size, activities=None):
    """activities: (small radius, type size), or None for Level 1 only."""
    out = [text(40, 52, "Example", 28, 700, CORNER, "start", ' letter-spacing="2"')]
    out += [link(at[a], at[b], r, 7) for a, b in LINKS]
    for name, corner, notes in MAP:
        cx, cy = at[corner]
        if activities:
            nr, nsize = activities
            fx, fy = FLIP[corner]
            for lines, (dx, dy) in zip(notes, SPREAD):
                nx, ny = cx + fx * dx, cy + fy * dy
                out.append(f'<line x1="{cx:g}" y1="{cy:g}" x2="{nx:g}" y2="{ny:g}" stroke="{SPOKE}" stroke-width="3"/>')
                out.append(f'<circle cx="{nx:g}" cy="{ny:g}" r="{nr}" fill="{NODE_FILL}" stroke="{NODE_STROKE}" stroke-width="2.5"/>')
                out.append(block(nx, ny, lines, nsize, round(nsize * 1.2), weight=600, fill=NODE_TEXT))
        out.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r}" fill="{HUB_FILL}" stroke="{BLUE}" stroke-width="5"/>')
        out.append(block(cx, cy, name, size, round(size * 1.2), weight=700, fill=HUB_TEXT))
    return svg(w, h, "".join(out))

# Level 1 and 2: the differentiators, their lines and the activities behind each one.
write("q4-activity-fit-map-example.svg",
      draw(1440, 640, {"TL": (420, 175), "TR": (1020, 175), "BL": (420, 465), "BR": (1020, 465)}, 85, 25, activities=(72, 20)))
# Level 1 only, for a narrow side panel: the differentiators and their lines.
write("q4-activity-fit-map-groups.svg",
      draw(900, 690, {"TL": (230, 215), "TR": (670, 215), "BL": (230, 505), "BR": (670, 505)}, 122, 34))
print("wrote q4-activity-fit-map-example.svg and q4-activity-fit-map-groups.svg")

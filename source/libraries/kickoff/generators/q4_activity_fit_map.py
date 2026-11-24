#!/usr/bin/env python3
"""Draw the example Activity Fit Map: four groups of activities and what each depends on.
Run from the library folder: python3 generators/q4_activity_fit_map.py"""
from q4_common import svg, write, text, block, BLUE, INK, GREY, MID, LINE, CANVAS, NOTE, NOTE_EDGE
W, H = 1440, 700
PW, PH, LX, RX, TY, BY = 630, 232, 40, 770, 86, 436
# name, x, y, activities (line breaks set by hand)
GROUPS = [("A Named Person for 90 Days", LX, TY, [["One contact", "from sign-up"], ["A call in", "week one"], ["Answers in", "one business", "day"]]),
          ("Live in a Day", RX, TY, [["Guided", "setup"], ["Ready-made", "templates"], ["Automatic", "data import"]]),
          ("One Flat Price", LX, BY, [["One plan"], ["No add-ons"], ["Automatic", "billing"]]),
          ("Standard, Not Custom", RX, BY, [["One product", "for everyone"], ["No custom", "work"], ["A short, fixed", "report set"]])]
NW, NH, PAD, NGAP = 188, 132, 16, 17
REGIONS = {}
defs = f'<defs><marker id="dep" markerUnits="userSpaceOnUse" markerWidth="30" markerHeight="30" refX="26" refY="15" orient="auto"><path d="M0,0 L30,15 L0,30 Z" fill="{BLUE}"/></marker></defs>'
out = [text(40, 52, "Example", 28, 700, MID, "start", ' letter-spacing="2"')]
for name, x, y, notes in GROUPS:
    out.append(f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="16" fill="{CANVAS}" stroke="{LINE}" stroke-width="2"/>')
    out.append(text(x + PW / 2, y + 50, name, 32, 700, BLUE))
    for k, lines in enumerate(notes):
        nx, ny = x + PAD + k * (NW + NGAP), y + 80
        out.append(f'<rect x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="8" fill="{NOTE}" stroke="{NOTE_EDGE}" stroke-width="2"/>')
        out.append(block(nx + NW / 2, ny + NH / 2, lines, 24, 30, weight=600, fill=INK))
    REGIONS[name] = [x, y, PW, PH]
arrow = lambda x1, y1, x2, y2: f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{BLUE}" stroke-width="5" marker-end="url(#dep)"/>'
out.append(arrow(LX + PW + 8, TY + PH / 2, RX - 12, TY + PH / 2))          # A Named Person for 90 Days depends on Live in a Day
out.append(arrow(RX + PW / 2, TY + PH + 8, RX + PW / 2, BY - 12))          # Live in a Day depends on Standard, Not Custom
out.append(arrow(LX + PW + 8, BY + PH / 2, RX - 12, BY + PH / 2))          # One Flat Price depends on Standard, Not Custom
out.append(arrow(1120, 43, 1200, 43))
out.append(text(1220, 52, "depends on", 26, 600, GREY, "start"))
write("q4-activity-fit-map-example.svg", svg(W, H, "".join(out), defs))
print("wrote q4-activity-fit-map-example.svg")

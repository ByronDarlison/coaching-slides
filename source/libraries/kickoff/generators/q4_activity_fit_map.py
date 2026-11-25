#!/usr/bin/env python3
"""Draw the example Activity Fit Map: four groups of activities and what each depends on.
Run from the library folder: python3 generators/q4_activity_fit_map.py"""
from q4_common import svg, write, text, block, BLUE, INK, GREY, MID, CORNER, LINE, CANVAS, NOTE, NOTE_EDGE
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
out = [text(40, 52, "Example", 28, 700, CORNER, "start", ' letter-spacing="2"')]
for name, x, y, notes in GROUPS:
    out.append(f'<rect x="{x}" y="{y}" width="{PW}" height="{PH}" rx="16" fill="{CANVAS}" stroke="{LINE}" stroke-width="2"/>')
    out.append(text(x + PW / 2, y + 50, name, 32, 700, BLUE))
    for k, lines in enumerate(notes):
        nx, ny = x + PAD + k * (NW + NGAP), y + 80
        out.append(f'<rect x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="8" fill="{NOTE}" stroke="{NOTE_EDGE}" stroke-width="2"/>')
        out.append(block(nx + NW / 2, ny + NH / 2, lines, 24, 30, weight=600, fill=INK))
    REGIONS[name] = [x, y, PW, PH]
def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{BLUE}" stroke-width="5" marker-end="url(#dep)"/>'
out.append(arrow(LX + PW + 8, TY + PH / 2, RX - 12, TY + PH / 2))          # A Named Person for 90 Days depends on Live in a Day
out.append(arrow(RX + PW / 2, TY + PH + 8, RX + PW / 2, BY - 12))          # Live in a Day depends on Standard, Not Custom
out.append(arrow(LX + PW + 8, BY + PH / 2, RX - 12, BY + PH / 2))          # One Flat Price depends on Standard, Not Custom
out.append(arrow(1120, 43, 1200, 43))
out.append(text(1220, 52, "depends on", 26, 600, GREY, "start"))
write("q4-activity-fit-map-example.svg", svg(W, H, "".join(out), defs))
print("wrote q4-activity-fit-map-example.svg")

# The four group names only, for a narrow side panel: same layout, arrows and legend, no activities
W2, H2, PW2, PH2, LX2, RX2, TY2, BY2 = 900, 690, 370, 220, 30, 500, 96, 436
NAMES = {"A Named Person for 90 Days": ["A Named Person", "for 90 Days"], "Standard, Not Custom": ["Standard,", "Not Custom"]}
out = [text(LX2, 56, "Example", 30, 700, CORNER, "start", ' letter-spacing="2"')]
for (name, x, y, _) in GROUPS:
    x, y = (LX2 if x == LX else RX2), (TY2 if y == TY else BY2)
    out.append(f'<rect x="{x}" y="{y}" width="{PW2}" height="{PH2}" rx="18" fill="{CANVAS}" stroke="{LINE}" stroke-width="3"/>')
    out.append(block(x + PW2 / 2, y + PH2 / 2, NAMES.get(name, [name]), 36, 46, weight=700, fill=BLUE))
out.append(arrow(LX2 + PW2 + 10, TY2 + PH2 / 2, RX2 - 12, TY2 + PH2 / 2))
out.append(arrow(RX2 + PW2 / 2, TY2 + PH2 + 10, RX2 + PW2 / 2, BY2 - 12))
out.append(arrow(LX2 + PW2 + 10, BY2 + PH2 / 2, RX2 - 12, BY2 + PH2 / 2))
out.append(arrow(600, 46, 680, 46))
out.append(text(698, 56, "depends on", 30, 600, GREY, "start"))
write("q4-activity-fit-map-groups.svg", svg(W2, H2, "".join(out), defs))
print("wrote q4-activity-fit-map-groups.svg")

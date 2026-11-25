#!/usr/bin/env python3
"""Draw the example swim lanes: the outcomes table, and the full twelve-quarter map.
Run from the library folder: python3 generators/q4_swim_lanes.py"""
from q4_common import svg, write, text, block, wrap, BLUE, INK, GREY, MID, LINE, CANVAS, NOTE, NOTE_EDGE, SEQ
W = 1440
OUTCOME = {12: BLUE, 8: SEQ[2], 4: SEQ[0]}
TINT = {12: "#e3ebf6", 8: "#e2eef0", 4: "#e7f2ea"}
HAG = {12: "3HAG", 8: "2HAG", 4: "1HAG"}
# lane, name as wrapped in the wide and the narrow name column, outcomes by quarter, milestones by quarter.
# Each milestone says what is true by that quarter, not the activity (Byron, 26-Sep-2026); wording from the Q4 brief.
LANES = [("Live in a Day", ["Live in a Day"], ["Live in", "a Day"],
          {12: "Every new customer can activate in 1 day without our help", 8: "Every new customer active in 1 day", 4: "Most new customers active in 1 day"},
          {2: ["Guided", "setup", "replaces", "the call"], 6: ["Data", "import is", "automatic"], 10: ["Setup", "checks", "itself"]}),
         ("One Flat Price", ["One Flat Price"], ["One Flat", "Price"],
          {12: "Customers can predict each invoice from the flat monthly price", 8: "Every customer on the flat plan", 4: "One published plan for new customers"},
          {1: ["Add-ons", "closed", "to new", "customers"], 5: ["Old plans", "moved", "over"], 9: ["Annual", "prepay", "offered"]}),
         ("A Named Person for 90 Days", ["A Named Person", "for 90 Days"], ["A Named", "Person", "for 90", "Days"],
          {12: "Every new customer can name and reach their contact for 90 days", 8: "Contacts answer in one business day", 4: "Every new customer has a named contact"},
          {3: ["Contact", "assigned", "at sign-up"], 7: ["Week-one", "call is", "standard"], 11: ["Contact", "team", "sized to", "demand"]}),
         ("Standard, Not Custom", ["Standard,", "Not Custom"], ["Standard,", "Not", "Custom"],
          {12: "One product, one setup, for everyone", 8: "Existing custom work retired", 4: "No new custom work sold"},
          {1: ["Custom", "work off", "the price", "list"], 4: ["Reporting", "cut to the", "fixed set"], 8: ["Last", "custom", "build", "retired"]})]
corner = lambda x: text(x, 44, "Example", 28, 700, MID, "start", ' letter-spacing="2"')
HEAD = {12: BLUE, 8: "#2f7377", 4: "#318549"}  # darker than the sequence colours, so type on or in them reads

# 1. The outcomes table
REGIONS_OUTCOMES = {}
X0, NAMEW, CW, HY, HH, RH = 20, 290, 370, 64, 64, 128
H1 = HY + HH + 4 * RH + 20
out = [corner(X0 + 20)]
for c, q in enumerate([12, 8, 4]):
    x = X0 + NAMEW + c * CW
    out.append(f'<rect x="{x+4}" y="{HY}" width="{CW-8}" height="{HH-8}" rx="10" fill="{HEAD[q]}"/>')
    out.append(text(x + CW / 2, HY + 38, f"{HAG[q]} outcome (Q{q})", 27, 700, "white"))
for r, (name, wide, _, outcomes, _) in enumerate(LANES):
    y = HY + HH + r * RH
    out.append(f'<rect x="{X0}" y="{y}" width="{W-2*X0}" height="{RH-8}" rx="12" fill="{CANVAS}"/>')
    out.append(block(X0 + 20, y + (RH - 8) / 2, wide, 28, 35, weight=700, fill=BLUE, anchor="start"))
    REGIONS_OUTCOMES[name] = [X0, y, W - 2 * X0, RH - 8]
    for c, q in enumerate([12, 8, 4]):
        x = X0 + NAMEW + c * CW
        out.append(f'<rect x="{x+4}" y="{y+8}" width="{CW-8}" height="{RH-24}" rx="10" fill="white" stroke="{OUTCOME[q]}" stroke-width="3"/>')
        out.append(block(x + CW / 2, y + (RH - 8) / 2, wrap(outcomes[q], 25, CW - 44), 25, 31, weight=500, fill=INK))
        REGIONS_OUTCOMES[f"{name}: {HAG[q]} outcome (Q{q})"] = [x + 4, y + 8, CW - 8, RH - 24]
write("q4-swim-lanes-outcomes.svg", svg(W, H1, "".join(out)))

# 2. The full map: lane name, then each outcome marker followed by its four quarters, Q12 down to Q1
REGIONS_MAP = {}
# A slightly wider canvas and narrower name and marker columns give each quarter about 7 more units,
# so the sticky words do not run edge to edge.
WM, X0, NAMEW, MW, HY, HH, RH = 1464, 2, 100, 30, 62, 62, 116
QW = (WM - 2 * X0 - NAMEW - 3 * MW) / 12
H2 = HY + HH + 4 * RH + 12
cols, x = [], X0 + NAMEW  # (kind, quarter, x, width)
for q in range(12, 0, -1):
    if q in HAG:
        cols.append(("marker", q, x, MW)); x += MW
    cols.append(("quarter", q, x, QW)); x += QW
out = [corner(X0 + 8)]
for kind, q, x, w in cols:
    if kind == "marker":
        out.append(text(x + w / 2, HY + 22, HAG[q], 18, 700, HEAD[q]))
        out.append(text(x + w / 2, HY + 46, f"(Q{q})", 18, 700, HEAD[q]))
    else:
        out.append(text(x + w / 2, HY + 36, f"Q{q}", 22, 700, GREY))
for r, (name, _, narrow, _, stickies) in enumerate(LANES):
    y = HY + HH + r * RH
    out.append(f'<rect x="{X0}" y="{y}" width="{WM-2*X0}" height="{RH-8}" rx="10" fill="{CANVAS}"/>')
    out.append(block(X0 + 8, y + (RH - 8) / 2, narrow, 18, 23, weight=700, fill=BLUE, anchor="start"))
    REGIONS_MAP[name] = [X0, y, WM - 2 * X0, RH - 8]
    for kind, q, x, w in cols:
        if kind == "marker":
            out.append(f'<rect x="{x+w/2-13:g}" y="{y+(RH-8)/2-20:g}" width="26" height="40" rx="8" fill="{OUTCOME[q]}"/>')
            REGIONS_MAP[f"{name}: {HAG[q]} outcome (Q{q})"] = [round(x + w / 2 - 13), round(y + (RH - 8) / 2 - 20), 26, 40]
            continue
        out.append(f'<rect x="{x+1:g}" y="{y+4}" width="{w-2:g}" height="{RH-16}" rx="7" fill="white" stroke="{LINE}" stroke-width="1.5"/>')
        if q in stickies:
            out.append(f'<rect x="{x+1:g}" y="{y+4}" width="{w-2:g}" height="{RH-16}" rx="7" fill="{NOTE}" stroke="{NOTE_EDGE}" stroke-width="2"/>')
            out.append(block(x + w / 2, y + (RH - 8) / 2, stickies[q], 18, 22, weight=600, fill=INK))
            REGIONS_MAP[f"{name}: Q{q} {' '.join(stickies[q])}"] = [round(x + 1), y + 4, round(w - 2), RH - 16]
write("q4-swim-lanes-example.svg", svg(WM, H2, "".join(out)))
print("wrote q4-swim-lanes-outcomes.svg and q4-swim-lanes-example.svg")

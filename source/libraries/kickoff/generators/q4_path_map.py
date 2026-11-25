#!/usr/bin/env python3
"""Draw the Q4 Annual path maps, one SVG per stage, in the style of the Q3 path map.
Day 1: ten stages in two rows of five (slide standard rule 21). Day 2: six stages in one row.
Run from the library folder: python3 generators/q4_path_map.py"""
from q4_common import svg, write, CORNER
DAY1 = [("team", ["Team"]), ("functions", ["Functions"]), ("kffm", ["KFFM"]), ("people", ["A-Player", "Team"]),
        ("culture", ["Purpose", "and Values"]), ("hedgehog", ["Hedgehog", "and BHAG"]),
        ("market", ["Market, Customer,", "Attribution"]), ("threehag", ["New", "3HAG"]),
        ("differentiators", ["Differentiators"]), ("lanes", ["Swim", "Lanes"])]
DAY2 = [("status", ["Status"]), ("forecast", ["Forecast"]), ("annual", ["New", "1HAG"]), ("quarter", ["New", "QHAG"]),
        ("sprint", ["Sprint", "Lanes"]), ("close", ["Meetings", "and close"])]
W, BH, GAP = 1440, 150, 22
GREEN, GREY, BLUE = "#318549", "#d5d9dd", "#326ab6"

def draw(stages, current, corner, per_row, bw, rowy, h):
    left = (W - per_row * bw - (per_row - 1) * GAP) / 2
    def pos(i):
        return left + (i % per_row) * (bw + GAP), rowy[i // per_row]
    out = [f'<text x="40" y="52" font-size="28" font-weight="700" fill="{CORNER}" text-anchor="start" letter-spacing="2">{corner}</text>']
    for i, (_, label) in enumerate(stages):
        x, y = pos(i); cx, cy = x + bw / 2, y + BH / 2
        done, now = i < current, i == current
        line = GREEN if done else GREY
        if i % per_row == per_row - 1 and i < len(stages) - 1:
            x2, y2 = pos(i + 1)
            out.append(f'<polyline points="{x+bw},{cy} {x+bw+18},{cy} {x+bw+18},{y+BH+25} {x2-20},{y+BH+25} {x2-20},{y2+BH/2} {x2},{y2+BH/2}" fill="none" stroke="{line}" stroke-width="5" stroke-linejoin="round"/>')
        elif i < len(stages) - 1:
            out.append(f'<line x1="{x+bw}" y1="{cy}" x2="{x+bw+GAP}" y2="{cy}" stroke="{line}" stroke-width="5"/>')
        if now:
            out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{BH}" rx="18" fill="{BLUE}"/>')
            fill, weight, size, top = "white", 700, 25, cy
        elif done:
            out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{BH}" rx="18" fill="#e7f2ea" stroke="{GREEN}" stroke-width="3"/>')
            fill, weight, size, top = "#20282f", 700, 24, cy - 28
            out.append(f'<text x="{cx}" y="{y+122}" font-size="23" font-weight="700" fill="{GREEN}" text-anchor="middle">✓ Done</text>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{BH}" rx="18" fill="white" stroke="{GREY}" stroke-width="3"/>')
            fill, weight, size, top = "#5b6670", 600, 25, cy
        lh = 33
        y0 = top - (len(label) - 1) * lh / 2 + 10
        for k, t in enumerate(label):
            out.append(f'<text x="{cx}" y="{y0+k*lh}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="middle">{t}</text>')
    return svg(W, h, "".join(out))

for i, (name, _) in enumerate(DAY1):
    write(f"q4-day1-path-{name}.svg", draw(DAY1, i, "Q4 · Day 1", 5, 250, [84, 284], 464))
for i, (name, _) in enumerate(DAY2):
    write(f"q4-day2-path-{name}.svg", draw(DAY2, i, "Q4 · Day 2", 6, 208, [84], 264))
print("wrote", len(DAY1) + len(DAY2), "path maps")

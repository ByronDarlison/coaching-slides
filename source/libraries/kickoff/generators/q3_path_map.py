#!/usr/bin/env python3
"""Draw the Q3 path map, one SVG per stage. Run from this folder: python3 generators/q3_path_map.py
Fourteen stages in two rows of seven. Every stop names what the team works on (slide standard rule 41)."""
import re, pathlib
HERE = pathlib.Path(__file__).resolve().parent.parent / "assets"
STAGES = [("status", ["Status"]), ("functions", ["Functions"]), ("scorecards", ["Scorecards"]), ("kffm", ["KFFM"]),
          ("values", ["Core", "Values"]), ("people", ["A-Player", "Team"]), ("attribution", ["Attribution", "Framework"]),
          ("strategy", ["3HAG"]), ("annual", ["1HAG"]), ("plan", ["QHAG"]), ("lanes", ["Sprint", "Lanes"]), ("priorities", ["Individual", "Priorities"]),
          ("forecast", ["Forecast"]), ("close", ["Meetings", "and close"])]
TOP = 7
W, H, BW, BH, GAP, LEFT = 1440, 464, 176, 150, 22, 38
ROWY = [84, 284]
GREEN, GREY, BLUE = "#318549", "#d5d9dd", "#326ab6"
STYLE = re.search(r"<style>.*?</style>", (HERE / "q1-path-status.svg").read_text(), flags=re.S).group(0)

def pos(i):
    row, col = (0, i) if i < TOP else (1, i - TOP)
    return LEFT + col * (BW + GAP), ROWY[row]

def draw(current):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{STYLE}',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           '<text x="40" y="52" font-size="28" font-weight="700" fill="#6b7780" text-anchor="start" letter-spacing="2">Q3</text>']
    for i, (_, label) in enumerate(STAGES):
        x, y = pos(i); cx, cy = x + BW / 2, y + BH / 2
        done, now = i < current, i == current
        line = GREEN if done else GREY
        if i == TOP - 1:
            x2, y2 = pos(TOP)
            out.append(f'<polyline points="{x+BW},{cy} {x+BW+18},{cy} {x+BW+18},{y+BH+25} {x2-20},{y+BH+25} {x2-20},{y2+BH/2} {x2},{y2+BH/2}" fill="none" stroke="{line}" stroke-width="5" stroke-linejoin="round"/>')
        elif i < len(STAGES) - 1:
            out.append(f'<line x1="{x+BW}" y1="{cy}" x2="{x+BW+GAP}" y2="{cy}" stroke="{line}" stroke-width="5"/>')
        if now:
            out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="18" fill="{BLUE}"/>')
            fill, weight, size, top = "white", 700, 25, cy
        elif done:
            out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="18" fill="#e7f2ea" stroke="{GREEN}" stroke-width="3"/>')
            fill, weight, size, top = "#20282f", 700, 24, cy - 28
            out.append(f'<text x="{cx}" y="{y+122}" font-size="23" font-weight="700" fill="{GREEN}" text-anchor="middle">✓ Done</text>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="18" fill="white" stroke="{GREY}" stroke-width="3"/>')
            fill, weight, size, top = "#5b6670", 600, 25, cy
        lh = 33
        y0 = top - (len(label) - 1) * lh / 2 + 10
        for k, t in enumerate(label):
            out.append(f'<text x="{cx}" y="{y0+k*lh}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="middle">{t}</text>')
    out.append("</svg>")
    return "".join(out)

for i, (name, _) in enumerate(STAGES):
    (HERE / f"q3-path-{name}.svg").write_text(draw(i))
print("wrote", len(STAGES), "path maps")

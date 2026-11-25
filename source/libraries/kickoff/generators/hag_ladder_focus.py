#!/usr/bin/env python3
"""Draw the cascade with one level in focus, for the side panel of a definition slide.

Writes hag-ladder-at-3hag, -1hag, -qhag and -priorities into the Kick Off library, and the four
hag-ladder-sprint-at-* drawings into the EOA library (its last level is the 13-week sprint lanes).
Each level steps 150 units to the right (the full-width cascade steps 190), so the drawing is
narrower and its smallest label, 21 units, shows at 13.8 pixels in the side panel at 1280 by 720
(visual standard, rule 32). Run from this folder: python3 generators/hag_ladder_focus.py"""
import re, pathlib
KICKOFF = pathlib.Path(__file__).resolve().parent.parent / "assets"
EOA = KICKOFF.parent.parent / "eoa" / "assets"
STYLE = re.search(r"<style>.*?</style>", (KICKOFF / "q1-path-status.svg").read_text(), flags=re.S).group(0)
BLUE, GREEN, INK, MUTE = "#326ab6", "#318549", "#20282f", "#5b6670"
STEP, BW, BH, RISE, SMALL = 150, 420, 92, 112, 21
TOP = [("BHAG", "Big Hairy Audacious Goal", "10 to 30 years"), ("3HAG", "3 Year Highly Achievable Goal", "3 years"),
       ("1HAG", "1 Year Highly Achievable Goal", "This year"), ("QHAG", "Quarterly Highly Achievable Goal", "This quarter")]
LAST = {"priorities": ("Priorities", "Individual Quarterly Priorities", "This quarter"),
        "sprint": ("Sprint Lanes", "13-Week Sprint Lanes", "Week by week")}
CAPTION = "Each level is built from the one above it and directs the one below."


def level(i, row, last):
    name, long, when = row
    x, y = 20 + i * STEP, 20 + i * RISE
    fill, edge = ("#e7f2ea", GREEN) if last else ("#f6f4ef", BLUE)
    return (f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="12" fill="{fill}" stroke="{edge}" stroke-width="3"/>'
            f'<text x="{x + 22}" y="{y + 42}" font-size="32" font-weight="700" fill="{edge}" text-anchor="start">{name}</text>'
            f'<text x="{x + 22}" y="{y + 74}" font-size="{SMALL}" font-weight="500" fill="{INK}" text-anchor="start">{long}</text>'
            f'<text x="{x + BW - 20}" y="{y + 42}" font-size="22" font-weight="700" fill="{MUTE}" text-anchor="end">{when}</text>')


def draw(kind, focus, caption):
    rows = TOP + [LAST[kind]]
    width = 40 + 4 * STEP + BW + 40
    height = 660 if caption else 600
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="-20 -10 {width} {height}" role="img">{STYLE}'
           f'<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{BLUE}"/></marker></defs>'
           f'<rect x="-20" y="-10" width="{width}" height="{height}" fill="white"/>']
    for i, row in enumerate(rows):
        out.append(level(i, row, i == 4))
        if i < 4:
            x, y = 20 + i * STEP + 120, 20 + i * RISE + BH
            out.append(f'<path d="M{x},{y} L{x},{y + 66} L{20 + (i + 1) * STEP - 8},{y + 66}" fill="none" stroke="{BLUE}" stroke-width="3" marker-end="url(#a)"/>')
    if caption:
        out.append(f'<text x="{(width - 40) / 2:g}" y="612" font-size="22" font-weight="600" fill="{INK}" text-anchor="middle">{CAPTION}</text>')
    # everything fades except the level in focus (rule 9)
    out.append(f'<rect x="-20" y="-10" width="{width}" height="{height}" fill="white" opacity=".6"/>')
    out.append(level(focus, rows[focus], focus == 4))
    x, y = 20 + focus * STEP, 20 + focus * RISE
    out.append(f'<rect x="{x - 6}" y="{y - 6}" width="{BW + 12}" height="{BH + 12}" rx="16" fill="none" stroke="{BLUE}" stroke-width="5"/></svg>')
    return "".join(out)


for name, focus in (("3hag", 1), ("1hag", 2), ("qhag", 3), ("priorities", 4)):
    (KICKOFF / f"hag-ladder-at-{name}.svg").write_text(draw("priorities", focus, True), encoding="utf-8")
for name, focus in (("3hag", 1), ("1hag", 2), ("qhag", 3), ("sprint", 4)):
    (EOA / f"hag-ladder-sprint-at-{name}.svg").write_text(draw("sprint", focus, False), encoding="utf-8")
print("wrote 8 focus cascades")

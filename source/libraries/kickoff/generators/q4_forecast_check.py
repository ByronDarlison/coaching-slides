#!/usr/bin/env python3
"""Draw the Q4 picture of the forecast check (Q4 slide "Next year's forecast gives you your annual targets.").

Step 2 on that slide: check the year against the new 3HAG. The picture follows one widget of the example
subscription company, new subscriptions. Twelve months add up to the year. The year then sits between this
year and the 3HAG, under a straight line from one to the other. The space under that line is the gap.

This year's 1,000 and the 3HAG's 2,000 are the numbers on the example 1HAG and 3HAG pages. The monthly
numbers and the 1,100 they add up to are invented for this picture. The straight line is a guide only:
the team decides what on track means.
Run from the library folder: python3 generators/q4_forecast_check.py"""
from q4_common import svg, write, text, BLUE, ORANGE, INK, GREY, MID, LINE, CORNER

MONTHS = "JFMAMJJASOND"
SUBS = [70, 75, 80, 85, 90, 90, 95, 95, 100, 105, 105, 110]  # invented; adds up to FORECAST
THIS_YEAR, FORECAST, HAG = 1000, sum(SUBS), 2000
assert FORECAST == 1100
GREEN = "#318549"  # the 3HAG green of the white-space picture
W, H = 1000, 800
HALO = ' stroke="white" stroke-width="8" paint-order="stroke" stroke-linejoin="round"'

o = [text(24, 46, "Example", 26, 700, CORNER, "start", ' letter-spacing="2"')]

# Top: the twelve months of one widget, and what they add up to.
o.append(text(40, 104, "New subscriptions, month by month", 30, 600, INK, "start"))
BASE = 284
for i, n in enumerate(SUBS):
    x, h = 40 + i * 55, n * 1.2
    o.append(f'<rect x="{x}" y="{BASE - h:g}" width="40" height="{h:g}" rx="3" fill="{BLUE}"/>')
    o.append(text(x + 20, BASE + 30, MONTHS[i], 22, 600, GREY))
o.append(text(850, 176, "add up to", 26, 600, GREY))
o.append(text(850, 240, f"{FORECAST:,}", 62, 700, BLUE))
o.append(text(850, 280, "for the year", 26, 600, GREY))
o.append(f'<line x1="40" y1="352" x2="960" y2="352" stroke="{LINE}" stroke-width="2"/>')

# Bottom: the year against the 3HAG.
o.append(text(40, 402, "Is the year on track for your new 3HAG?", 30, 600, INK, "start"))
FLOOR, SCALE = 736, 0.15
COLS = [140, 380, 620, 860]
def top(n): return FLOOR - n * SCALE
o.append(f'<line x1="40" y1="{FLOOR}" x2="960" y2="{FLOOR}" stroke="{MID}" stroke-width="2"/>')
for cx, n, fill in [(COLS[0], THIS_YEAR, GREY), (COLS[1], FORECAST, BLUE), (COLS[3], HAG, GREEN)]:
    o.append(f'<rect x="{cx - 60}" y="{top(n):g}" width="120" height="{n * SCALE:g}" rx="4" fill="{fill}"/>')
    o.append(text(cx, top(n) + 40, f"{n:,}", 30, 700, "white"))  # inside the bar, clear of the dashed line
for cx, name, ink in zip(COLS, ["This year", "Next year", "Year 2", "3HAG"], [GREY, INK, GREY, INK]):
    o.append(text(cx, FLOOR + 38, name, 26, 600, ink))
# The straight line from this year to the 3HAG, and the gap under it next year.
on_track = THIS_YEAR + (HAG - THIS_YEAR) / 3
o.append(f'<line x1="{COLS[0] + 60}" y1="{top(THIS_YEAR):g}" x2="{COLS[3] - 60}" y2="{top(HAG):g}" stroke="{GREEN}" stroke-width="4" stroke-dasharray="14 8"/>')
o.append(text(COLS[2], top(THIS_YEAR + (HAG - THIS_YEAR) * 2 / 3) - 22, "On track", 28, 700, GREEN, "middle", HALO))
gx = COLS[1] + 84
o.append(f'<path d="M{gx - 12} {top(on_track):g}H{gx}V{top(FORECAST):g}H{gx - 12}" fill="none" stroke="{ORANGE}" stroke-width="5"/>')
o.append(text(gx + 14, (top(on_track) + top(FORECAST)) / 2 + 10, "Gap", 28, 700, ORANGE, "start", HALO))

write("q4-forecast-check.svg", svg(W, H, "".join(str(p) for p in o)))
print("wrote q4-forecast-check.svg; forecast", FORECAST, "on track", round(on_track))

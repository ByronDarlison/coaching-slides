#!/usr/bin/env python3
"""Draw the Q4 picture of the 3HAG line: the white space it opens (Q4 slide "Does your 3HAG line give you
enough white space?").

One rule (Byron, 26-Nov-2026): white is the gap between the 3HAG line and the best competitor, wherever the two
lines separate. Above the competitor line the company invests to lead. Below it the company gives things up, and does not
compete there. What it gives up pays for what it invests in. Where the two lines touch there is no white: that is head-on competition.

The scores are read from the Q3 drawing (assets/attribution-3hag.svg), so the example stays the one the team
already knows. The three competitor lines become one line, the best competitor score on each attribute.
Run from the library folder: python3 generators/q4_attribution_line.py"""
import re
from q4_common import ASSETS, svg, write, text, INK, GREY, LINE, CORNER

NAMES = [["Speed of", "setup"], ["Ease of", "use"], ["Price", "predictability"], ["Reliability"],
         ["Billing", "simplicity"], ["Support from", "a person"], ["Security"], ["Integrations"], ["Reporting"],
         ["Feature", "breadth"], ["Customization"], ["Partner", "network"]]
src = (ASSETS / "attribution-3hag.svg").read_text()
lines = [[round((562 - float(p.split(",")[1])) / 90) for p in pts.split()]
         for pts in re.findall(r'<polyline points="([^"]+)"', src)]
assert len(lines) == 5 and all(len(l) == 12 for l in lines), "the Q3 drawing no longer has its five lines of twelve"
TODAY, A, B, C, HAG = lines
BEST = [max(s) for s in zip(A, B, C)]
assert src.count(">3HAG line<") == 1 and HAG[0] == 5, "the last line in the Q3 drawing is no longer the 3HAG line"

W, H = 1440, 664
LEFT, RIGHT, TOP, BOTTOM = 102, 1392, 86, 502
GROUND, GREEN, RIVAL, BLUE = "#e6e9ec", "#318549", "#5b6670", "#326ab6"
def x(i): return 130 + i * 1250 / 11
def y(score): return 584 - 96 * score
def pts(scores): return " ".join(f"{x(i):.1f},{y(s):.1f}" for i, s in enumerate(scores))
def dots(scores, r, fill): return "".join(f'<circle cx="{x(i):.1f}" cy="{y(s):.1f}" r="{r}" fill="{fill}"/>' for i, s in enumerate(scores))
def halo(cx, cy, words, size=27): return text(cx, cy, words, size, 700, INK, "middle", ' stroke="white" stroke-width="7" paint-order="stroke" stroke-linejoin="round"')

o = [f'<rect x="{LEFT}" y="{TOP}" width="{RIGHT - LEFT}" height="{BOTTOM - TOP}" fill="{GROUND}"/>']
# The white space: everything between the 3HAG line and the best competitor line, on either side of it.
back = " ".join(f"{x(i):.1f},{y(s):.1f}" for i, s in reversed(list(enumerate(BEST))))
o.append(f'<polygon points="{pts(HAG)} {back}" fill="white" fill-rule="nonzero"/>')
for s in range(1, 6):
    o.append(text(LEFT - 16, y(s) + 9, s, 26, 600, GREY, "end"))
for i, name in enumerate(NAMES):
    low = i % 2
    moved = HAG[i] != TODAY[i]
    o.append(f'<line x1="{x(i):.1f}" y1="{BOTTOM}" x2="{x(i):.1f}" y2="{BOTTOM + (88 if low else 16)}" stroke="{LINE}" stroke-width="2"/>')
    o += [text(x(i), BOTTOM + (114 if low else 42) + k * 28, t, 24, 600, INK if moved else GREY) for k, t in enumerate(name)]
o.append(f'<polyline points="{pts(TODAY)}" fill="none" stroke="{BLUE}" stroke-opacity="0.3" stroke-width="6" stroke-linejoin="round"/>')
o.append(f'<polyline points="{pts(BEST)}" fill="none" stroke="{RIVAL}" stroke-width="4" stroke-linejoin="round" stroke-dasharray="14 8"/>' + dots(BEST, 5, RIVAL))
o.append(f'<polyline points="{pts(HAG)}" fill="none" stroke="{GREEN}" stroke-width="7" stroke-linejoin="round"/>' + dots(HAG, 8, GREEN))
# Name each side of the white once.
o.append(halo(x(2), y(4) + 10, "Invest"))
o.append(halo((x(9) + x(10)) / 2 + 20, y(3.45), "Give up"))
# Legend.
o.append(text(24, 50, "Example", 26, 700, CORNER, "start", ' letter-spacing="2"'))
def key(x0, sample, words, ink=INK): return sample + text(x0 + 70, 50, words, 25, 600, ink, "start")
o.append(key(300, f'<line x1="300" y1="41" x2="356" y2="41" stroke="{GREEN}" stroke-width="7"/>', "3HAG line"))
o.append(key(540, f'<line x1="540" y1="41" x2="596" y2="41" stroke="{RIVAL}" stroke-width="4" stroke-dasharray="14 8"/>', "Best competitor"))
o.append(key(850, f'<line x1="850" y1="41" x2="906" y2="41" stroke="{BLUE}" stroke-opacity="0.3" stroke-width="6"/>', "Us today", GREY))
o.append(key(1090, f'<rect x="1090" y="27" width="56" height="28" fill="white" stroke="{GREY}" stroke-width="2"/>', "White space"))
write("q4-attribution-3hag.svg", svg(W, H, "".join(str(p) for p in o)))
print("wrote q4-attribution-3hag.svg; best competitor", BEST)

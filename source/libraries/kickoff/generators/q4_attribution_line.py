#!/usr/bin/env python3
"""Make the Q4 copy of the Q3 3HAG line drawing (assets/attribution-3hag.svg).
Three changes, nothing else:
1. The callout's question. At Q3 it asks what the team could afford not to be as good at. At the annual the line
   is agreed, and the question is what makes it true (slide standard rule 36).
2. Readable words. The Q3 drawing dims the axis labels, the legend and the end labels with the competitor lines.
   Here the twelve axis labels, the legend words and the A, B, C end labels are drawn at full strength in gray
   #5b6670, and the five attributes the 3HAG line leads on or drops are in ink #20282f. The competitor lines stay dimmed.
3. The white space is white. Where the 3HAG line rises above today and where it drops below today are both
   painted white on the gray ground. "Do more" and "Do less" name the two. The Q3 white band
   above the competitors is removed, so white means one thing: the company's own white space.
Run from the library folder: python3 generators/q4_attribution_line.py"""
import re
from q4_common import ASSETS, write
OLD, NEW = "Ask: what could we afford not to be as good at?", "Ask: what will make this whole line true?"
KEY = {"Speed of setup", "Price predictability", "Support from a person", "Reporting", "Customization"}
INK, SOFT = "#20282f", "#5b6670"
src = (ASSETS / "attribution-3hag.svg").read_text()
assert src.count(OLD) == 1, "the Q3 drawing no longer carries the callout this script replaces"
src = src.replace(OLD, NEW)
seen = {"axis": 0, "legend": 0, "end": 0}

def group(m):
    opacity, inner = m.group(1), m.group(2)
    words = " ".join(re.findall(r">([^<]+)</text>", inner))
    if opacity == "0.35":                                   # an axis label with its tick
        seen["axis"] += 1
        fill = INK if words in KEY else SOFT
        return "<g>" + inner.replace(f'fill="{INK}"', f'fill="{fill}"') + "</g>"
    if opacity == "0.3":                                    # a legend entry: dim the sample line, not the word
        seen["legend"] += 1
        inner = re.sub(r"<line ", f'<line opacity="{opacity}" ', inner, count=1)
        return "<g>" + inner.replace(f'fill="{INK}"', f'fill="{SOFT}"') + "</g>"
    labels = re.findall(r"<text[^>]*>[ABC]</text>", inner)  # a competitor line: keep it dim, lift its end label out
    for label in labels:
        seen["end"] += 1
        inner = inner.replace(label, "")
    return f'<g opacity="{opacity}">{inner}</g>' + "".join(l.replace('fill="#7a858e"', f'fill="{SOFT}"') for l in labels)

out = re.sub(r'<g opacity="([\d.]+)">(.*?)</g>', group, src)
assert seen == {"axis": 12, "legend": 4, "end": 3}, seen

# 3. The white space. The Q3 drawing shades green where the 3HAG line rises above today. The line also makes white
#    space where it drops below today. Both are painted white. Each kind is named once, on the drawing.
TODAY = [4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2]
HAG = [5, 4, 5, 4, 4, 5, 3, 3, 2, 2, 1, 2]
GREEN, AMBER = "#bfe3c9", "#f6dfa8"
def x(i): return 130 + i * 1250 / 11
def y(score): return 562 - 90 * score
drawn = [[tuple(round(float(n), 1) for n in pt.split(",")) for pt in pts.split()]
         for pts in re.findall(r'<polyline points="([^"]+)"', out)]
for name, line in (("Us today", TODAY), ("3HAG line", HAG)):
    assert [(round(x(i), 1), float(y(s))) for i, s in enumerate(line)] in drawn, f"the {name} line in the Q3 drawing has moved"
down = [i for i in range(12) if HAG[i] < TODAY[i]]
assert down == [8, 10], down
EDGE = 'fill="white" stroke="#326ab6" stroke-width="3" stroke-dasharray="10 8" stroke-linejoin="round"/>'
# White means one thing here: the company's own white space. The Q3 band above the competitors goes back to gray.
band = re.findall(r'<polygon points="[^"]+" ' + re.escape(EDGE), out)
assert len(band) == 1, len(band)
out = out.replace(band[0], "")
EDGE = 'fill="white"/>'  # the gray ground and the 3HAG line give the white its edge
less = "".join('<polygon points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in (
    [(x(k), y(TODAY[k])) for k in (i - 1, i, i + 1)] + [(x(i), y(HAG[i]))])) + '" ' + EDGE for i in down)
assert out.count(f'fill="{GREEN}"/>') == 1
out = out.replace(f'fill="{GREEN}"/>', EDGE + less)
def label(cx, cy, words, ink, ground):
    return (f'<text x="{cx:.1f}" y="{cy}" font-size="23" font-weight="700" fill="{ink}" text-anchor="middle" '
            f'stroke="{ground}" stroke-width="6" paint-order="stroke" stroke-linejoin="round">{words}</text>')
labels = label((x(4) + x(5)) / 2 + 6, 258, "Do more", "#1d5c31", "white") + label(x(8), 345, "Do less", "#6D4B08", "white")
WHY = "Why: a real position means trade-offs."
assert out.count(WHY) == 1
out = out.replace(WHY, "Your white space: where you do more and where you do less.")
box = '<rect x="290" y="664"'
assert out.count(box) == 1
out = out.replace(box, labels + box)
write("q4-attribution-3hag.svg", out)
print("wrote q4-attribution-3hag.svg")

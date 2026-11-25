#!/usr/bin/env python3
"""Make the Q4 copy of the Q3 3HAG line drawing (assets/attribution-3hag.svg).
Two changes, nothing else:
1. The callout's question. At Q3 it asks what the team could afford not to be as good at. At the annual the line
   is agreed, and the question is what makes it true (slide standard rule 36).
2. Readable words. The Q3 drawing dims the axis labels, the legend and the end labels with the competitor lines.
   Here the twelve axis labels, the legend words and the A, B, C end labels are drawn at full strength in gray
   #5b6670, and the five attributes the 3HAG line leads on or drops are in ink #20282f. The competitor lines stay dimmed.
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
write("q4-attribution-3hag.svg", out)
print("wrote q4-attribution-3hag.svg")

"""Crop the QHAG example to one block, so its words are readable when projected.

Writes qhag-numbers-crop.svg (block 1, Numbers), qhag-p1-crop.svg and
qhag-priorities-crop.svg (block 2, Priorities) into libraries/kickoff/assets,
from the same drawings the full page uses (rule 9: point at the example).
Run after any change to the qhag-map SVGs:

    python3 source/artwork/kickoff/drawings/qhag_crops.py
"""
from pathlib import Path
import re

A = Path(__file__).resolve().parents[3] / "libraries" / "kickoff" / "assets"
CROPS = [("qhag-map-numbers.svg", "qhag-numbers-crop.svg", (10, 80, 920, 790)),
         ("qhag-map-p1.svg", "qhag-p1-crop.svg", (936, 86, 490, 780)),
         ("qhag-map-priorities.svg", "qhag-priorities-crop.svg", (936, 86, 490, 780))]

for src, dst, (x, y, w, h) in CROPS:
    s = (A / src).read_text(encoding="utf-8")
    head = re.match(r"<svg[^>]*>", s).group(0)
    new = re.sub(r'width="[^"]*"', f'width="{w}"', head, count=1)
    new = re.sub(r'height="[^"]*"', f'height="{h}"', new, count=1)
    new = re.sub(r'viewBox="[^"]*"', f'viewBox="{x} {y} {w} {h}"', new, count=1)
    (A / dst).write_text(new + s[len(head):], encoding="utf-8")
print("wrote", len(CROPS), "QHAG crops")

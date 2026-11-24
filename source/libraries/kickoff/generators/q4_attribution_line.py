#!/usr/bin/env python3
"""Make the Q4 copy of the Q3 3HAG line drawing (assets/attribution-3hag.svg) with the callout's question changed.
At Q3 the callout asks what the team could afford not to be as good at. At the annual the line is agreed, and the
question is what makes it true (slide standard rule 36). Nothing else in the drawing changes.
Run from the library folder: python3 generators/q4_attribution_line.py"""
from q4_common import ASSETS, write
OLD, NEW = "Ask: what could we afford not to be as good at?", "Ask: what will make this whole line true?"
src = (ASSETS / "attribution-3hag.svg").read_text()
assert src.count(OLD) == 1, "the Q3 drawing no longer carries the callout this script replaces"
write("q4-attribution-3hag.svg", src.replace(OLD, NEW))
print("wrote q4-attribution-3hag.svg")

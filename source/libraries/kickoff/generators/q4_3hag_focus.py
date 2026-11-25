#!/usr/bin/env python3
"""Draw the Q4 3HAG page from the Kick Off 3HAG page, so the team sees the page they already know
(slide standard rule 43). Each Q4 picture is the matching Kick Off picture with one change: block 3 is
"Differentiators (3 to 5)" in place of the key capabilities, and the end date is one year later. Block 3 is empty until the team builds the
differentiators, then it lists the four from the Activity Fit Map example. Run from the library folder:
python3 generators/q4_3hag_focus.py"""
import re
from q4_common import ASSETS

# Q4 picture -> the Kick Off picture with the same block highlighted.
SOURCES = {"numbers": "3hag-map-1.svg", "statement": "3hag-map-2.svg",
           "differentiators": "3hag-map-3.svg", "known-for": "3hag-map-4.svg"}
# The four differentiators in q4-activity-fit-map-example.svg.
BUILT = ["A Named Person for 90 Days", "Live in a Day", "One Flat Price", "Standard, Not Custom"]
BULLET = re.compile(r'(<text x="980" y="(?:428|480|532|584)"[^>]*>)•  [^<]*(</text>)')

def draw(key):
    """The highlighted Kick Off picture draws its lit block twice, so block 3 may appear more than once."""
    page = (ASSETS / SOURCES[key]).read_text()
    if "Key capabilities (3 to 5)" not in page:
        raise SystemExit(f"{SOURCES[key]} no longer has a 'Key capabilities (3 to 5)' heading")
    page = page.replace("Key capabilities (3 to 5)", "Differentiators (3 to 5)")
    # The new 3HAG is one year further out than the Kick Off example.
    if "December 31, 2029" not in page:
        raise SystemExit(f"{SOURCES[key]} no longer shows 'December 31, 2029'")
    page = page.replace("December 31, 2029", "December 31, 2030")
    seen = [0]
    def swap(match):
        name = BUILT[seen[0] % 4] if key == "differentiators" else None
        seen[0] += 1
        return f"{match.group(1)}•  {name}{match.group(2)}" if name else ""
    page = BULLET.sub(swap, page)
    if seen[0] == 0 or seen[0] % 4:
        raise SystemExit(f"{SOURCES[key]}: expected capability lines in fours; found {seen[0]}")
    return page

for key in SOURCES:
    (ASSETS / f"q4-3hag-focus-{key}.svg").write_text(draw(key))
print("wrote four Q4 3HAG page variants")

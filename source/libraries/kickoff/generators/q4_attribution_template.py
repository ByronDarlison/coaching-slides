#!/usr/bin/env python3
"""Draw the Q4 card for the Attribution Map template from the Q3 card (Q4 slide "The Attribution Map template,
if you need it."). At Q3 the team copies the sheet and scores in it. At Q4 the team's map is in Metronome, and
the sheet is only the template to fall back on (Byron, 27-Nov-2026). So the card is the Q3 card with one change:
it is named a template and says when to use it. The QR code is the same.
Run from the library folder: python3 generators/q4_attribution_template.py"""
from q4_common import ASSETS

SWAPS = {">Attribution Map sheet<": ">Attribution Map template<",
         ">Make a copy, then enter your scores.<": ">Only if you need to rebuild your map.<"}
card = (ASSETS / "attribution-sheet.svg").read_text()
for old, new in SWAPS.items():
    if card.count(old) != 1:
        raise SystemExit(f"attribution-sheet.svg no longer has exactly one {old!r}")
    card = card.replace(old, new)
(ASSETS / "q4-attribution-template.svg").write_text(card)
print("wrote q4-attribution-template.svg")

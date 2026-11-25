#!/usr/bin/env python3
"""Draw the Q4 purpose sticky: the Q3 sticky with new words. Reads q3-sticky-purpose.svg and replaces only its text.
Run from the library folder: python3 generators/q4_sticky.py"""
import re
from q4_common import ASSETS, write
LINES = ["Strategy", "mapped out.", "New 3HAG."]
SIZE, LH, CX, CY = 92, 115, 838, 470
src = (ASSETS / "q3-sticky-purpose.svg").read_text()
y0 = CY - (len(LINES) - 1) * LH / 2 + 32
words = "".join(f'<text x="{CX}" y="{y0+k*LH:g}" font-size="{SIZE}" font-weight="700" fill="#20282f" text-anchor="middle">{t}</text>'
                for k, t in enumerate(LINES))
out, n = re.subn(r"(?:<text[^>]*>[^<]*</text>)+(?=</g></svg>)", words, src)
assert n == 1, "the Q3 sticky no longer ends with its text lines"
write("q4-sticky-purpose.svg", out)
print("wrote q4-sticky-purpose.svg")

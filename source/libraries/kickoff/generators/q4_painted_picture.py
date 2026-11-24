#!/usr/bin/env python3
"""Draw the painted picture prompt sheet: the question, then twelve numbered prompts.
Run from the library folder: python3 generators/q4_painted_picture.py"""
from q4_common import svg, write, text, block, wrap, BLUE, INK, LINE
W, H = 1440, 590
CHIPS = ["What you see", "What you hear", "What clients say", "What the media writes", "What the team says",
         "The buzz in your community", "Your marketing", "The day to day", "The financials", "How you are funded",
         "Core Values in action", "Your impact on the world"]
X0, CW, CH, GX, GY, Y0 = 30, 330, 100, 20, 18, 222
out = [f'<rect x="{X0}" y="30" width="{W-2*X0}" height="164" rx="18" fill="{BLUE}"/>',
       text(W / 2, 104, "10 to 30 years from now", 50, 700, "white"),
       text(W / 2, 156, "What do you see, hear and feel?", 30, 500, "white")]
for i, label in enumerate(CHIPS):
    x, y = X0 + (i % 4) * (CW + GX), Y0 + (i // 4) * (CH + GY)
    out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="12" fill="white" stroke="{LINE}" stroke-width="2"/>')
    out.append(f'<circle cx="{x+46}" cy="{y+CH/2}" r="26" fill="{BLUE}"/>')
    out.append(text(x + 46, y + CH / 2 + 9, i + 1, 25, 700, "white"))
    out.append(block(x + 86, y + CH / 2, wrap(label, 25, CW - 86 - 12), 25, 31, weight=600, fill=INK, anchor="start"))
write("q4-painted-picture.svg", svg(W, H, "".join(out)))
print("wrote q4-painted-picture.svg")

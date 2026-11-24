#!/usr/bin/env python3
"""Draw the three rings: Why at the centre, How, then What, each joined to its question.
Run from the library folder: python3 generators/q4_golden_circle.py"""
from q4_common import svg, write, text, BLUE, INK, GREY
W, H = 1440, 760
CX, CY, R = 384, 380, [340, 225, 110]
TX = 800
out = [f'<circle cx="{CX}" cy="{CY}" r="{R[0]}" fill="#dde7f5" stroke="{BLUE}" stroke-width="5"/>',
       f'<circle cx="{CX}" cy="{CY}" r="{R[1]}" fill="#a9c1e4" stroke="{BLUE}" stroke-width="5"/>',
       f'<circle cx="{CX}" cy="{CY}" r="{R[2]}" fill="{BLUE}"/>',
       text(CX, CY - (R[0] + R[1]) / 2 + 14, "What", 44, 700, INK),
       text(CX, CY - (R[1] + R[2]) / 2 + 14, "How", 44, 700, INK),
       text(CX, CY + 16, "Why", 50, 700, "white")]
d = 199
leaders = [((CX + d, CY - d), CY - d, "What does the company do?"),
           ((CX + (R[1] + R[2]) / 2, CY), CY, "How does the company do it?"),
           ((CX + 74, CY + 74), CY + d, "Why does the company do it?")]
for (x, y), ty, words in leaders:
    mid = f" L{x + (ty - y):g},{ty:g}" if ty != y else ""
    out.append(f'<path d="M{x:g},{y:g}{mid} L{TX-22},{ty:g}" fill="none" stroke="{GREY}" stroke-width="3" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{x:g}" cy="{y:g}" r="9" fill="{GREY}" stroke="white" stroke-width="3"/>')
    out.append(text(TX, ty + 13, words, 38, 600, INK, "start"))
write("q4-golden-circle.svg", svg(W, H, "".join(out)))
print("wrote q4-golden-circle.svg")

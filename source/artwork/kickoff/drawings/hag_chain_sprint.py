#!/usr/bin/env python3
"""The planning chain with Sprint Lanes, for decks from Q2 on.

From Q2 the session goes QHAG, then 13-week sprint lanes, then individual priorities.
The Kick Off and Q1 chain (hag-ladder-checked-*.svg) has no Sprint Lanes box, so its
"next" box after the QHAG is Priorities. That is wrong from Q2 (Byron, review of the Q2
deck, 25-Nov-2026). These drawings add the Sprint Lanes box between QHAG and Priorities.

Same canvas as the Kick Off chain (300 x 680), so a slide's layout does not change.
Fonts come from the embedded <style> in hag-ladder.svg. Run from anywhere:
    python3 source/artwork/kickoff/drawings/hag_chain_sprint.py
"""
import pathlib
import re

ASSETS = pathlib.Path(__file__).resolve().parents[3] / "libraries" / "kickoff" / "assets"
STYLE = re.search(r"<style>.*?</style>", (ASSETS / "hag-ladder.svg").read_text(), re.S).group(0)

BOXES = ["BHAG", "3HAG", "1HAG", "QHAG", "Sprint Lanes", "Priorities"]
W, H = 300, 680
BOX_H, GAP, TOP, X, BOX_W = 88, 22, 21, 12.0, 276
GREEN, GREY, BLUE, INK, MUTED = "#318549", "#9aa3ab", "#326ab6", "#20282f", "#5b6670"


def draw(checked):
    """checked: the names carrying a green check. BHAG is never checked: it is the fixed top."""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">{STYLE}',
           f'<rect width="{W}" height="{H}" fill="white"/>']
    for i, name in enumerate(BOXES):
        y = TOP + i * (BOX_H + GAP)
        done = name in checked
        nxt = BOXES[i + 1] if i + 1 < len(BOXES) else None
        if nxt:
            # The connector is green when both ends are checked, as on the Kick Off chain.
            c = GREEN if (done and nxt in checked) else GREY
            y1, y2 = y + BOX_H, y + BOX_H + GAP - 9
            out.append(f'<line x1="150.0" y1="{y1}" x2="150.0" y2="{y2 - 1}" stroke="{c}" stroke-width="5"/>')
            out.append(f'<path d="M140.0,{y2 - 3} L150.0,{y2 + 8} L160.0,{y2 - 3} Z" fill="{c}"/>')
        ty = y + BOX_H / 2 + 12
        if name == "BHAG":
            out.append(f'<rect x="{X}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="16" fill="white" stroke="{BLUE}" stroke-width="4"/>')
            out.append(f'<text x="38.0" y="{ty}" font-size="33" font-weight="700" fill="{BLUE}">{name}</text>')
        elif done:
            out.append(f'<rect x="{X}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="16" fill="#e7f2ea" stroke="{GREEN}" stroke-width="4"/>')
            out.append(f'<text x="38.0" y="{ty}" font-size="33" font-weight="700" fill="{INK}">{name}</text>')
            out.append(f'<text x="262.0" y="{ty + 1}" font-size="38" font-weight="700" fill="{GREEN}" text-anchor="end">✓</text>')
        else:
            out.append(f'<rect x="{X}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="16" fill="white" stroke="{GREY}" stroke-width="3"/>')
            out.append(f'<text x="38.0" y="{ty}" font-size="33" font-weight="600" fill="{MUTED}">{name}</text>')
    out.append("</svg>")
    return "".join(out)


FILES = {
    "hag-chain-sprint-checked-3hag.svg": ["3HAG"],
    "hag-chain-sprint-checked-1hag.svg": ["3HAG", "1HAG"],
    "hag-chain-sprint-checked-qhag.svg": ["3HAG", "1HAG", "QHAG"],
    "hag-chain-sprint-checked.svg": ["3HAG", "1HAG", "QHAG", "Sprint Lanes", "Priorities"],
}

if __name__ == "__main__":
    for name, checked in FILES.items():
        (ASSETS / name).write_text(draw(checked))
        print("wrote", name)

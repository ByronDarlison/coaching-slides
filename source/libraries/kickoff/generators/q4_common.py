"""Shared helpers for the Q4 drawing generators (q4_*.py). Not a drawing itself.
Lifts the embedded Geist font from an existing drawing so every Q4 drawing renders in the same type."""
import re, pathlib
ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
STYLE = re.search(r"<style>.*?</style>", (ASSETS / "q1-path-status.svg").read_text(), flags=re.S).group(0)
BLUE, GREEN, DGREEN, ORANGE = "#326ab6", "#54b570", "#318549", "#a94f1f"
SEQ = ["#54b570", "#4ca282", "#438f93", "#3b7da5", "#326ab6"]  # ordered things run green to blue
INK, GREY, MID, LINE, CANVAS = "#20282f", "#5b6670", "#9aa3ab", "#d5d9dd", "#f6f4ef"
CORNER = "#6b7780"  # corner labels ("Example", "Q4 · Day 1"): 4.5:1 on white
NOTE, NOTE_EDGE = "#fbec9d", "#c9a227"  # sticky note, as in kffm-levers.svg

def text(x, y, s, size=24, weight=500, fill=INK, anchor="middle", extra=""):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{s}</text>'

def wrap(s, size, maxw, k=0.56):
    """Greedy wrap using the 0.56 x size per character estimate for Geist."""
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and len(trial) * size * k > maxw:
            lines.append(cur); cur = word
        else:
            cur = trial
    return lines + [cur]

def block(x, cy, lines, size=24, lh=None, **kw):
    """Lines of text centred vertically on cy."""
    lh = lh or round(size * 1.25)
    y0 = cy - (len(lines) - 1) * lh / 2 + size * 0.35
    return "".join(text(x, y0 + k * lh, t, size, **kw) for k, t in enumerate(lines))

def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">{STYLE}'
            f'{defs}<rect width="{w}" height="{h}" fill="white"/>{body}</svg>')

def write(name, s):
    (ASSETS / name).write_text(s)

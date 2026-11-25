#!/usr/bin/env python3
"""Q3 deck drawings, generated so they stay consistent and editable.

- q3-path-<stage>.svg: the day's stage map, one per stage (rule 8: show where we are).
- mars-steps.svg: the five steps of Mission to Mars, in the words of the master board's
  "Core Values, Q3: Mission to Mars" area.
- a-player-grid.svg, a-player-placed.svg, a-player-zones.svg, a-player-plans.svg: the A-Player
  Team Assessment in the board's layout: the empty grid, Jen's team placed, the A, B and C
  zones revealed, and the plans for everyone below A.
- attribution-example.svg and attribution-<part>.svg: the worked Attribution Framework for the
  same subscription company, then one callout per part (rule 9: point at the example).
- values-links.svg, a-player-links.svg, attribution-sheet.svg, cash-12-month.svg: QR codes.
- q3-sticky.jpg and q3-sticky-checked.svg: the purpose note, from the Kick Off's sticky image.

The example's people, values, placements and scores are Byron's rulings of 17 November 2026
(records/q3/brief.md, rulings 6, 7 and 9). Edit here, then run:

    /usr/bin/python3 source/artwork/q3/drawings/q3_drawings.py
"""
from pathlib import Path
import base64
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "libraries" / "kickoff" / "assets"
STYLE = re.search(r"<style>.*?</style>", (OUT / "hag-ladder.svg").read_text(), re.S).group(0)
sys.path.insert(0, str(ROOT / "tools"))
import qr_svg  # noqa: E402

B = "#326ab6"; G = "#318549"; INK = "#20282f"; MUTE = "#5b6670"; GREY = "#9aa3ab"; LINE = "#d5d9dd"
GFILL = "#e7f2ea"; BFILL = "#e8eef8"; CARD = "#f6f4ef"; ORANGE = "#a94f1f"; OFILL = "#f8ebe3"
YELLOW = "#fdf3b8"; YLINE = "#d9c75a"
SEQ = ["#54b570", "#4ca282", "#438f93", "#3b7da5", "#326ab6"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size, weight=500, fill=INK, anchor="middle", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'


def lines(x, y, rows, size, lh, weight=500, fill=INK, anchor="middle"):
    return "".join(t(x, y + i * lh, r, size, weight, fill, anchor) for i, r in enumerate(rows))


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">{STYLE}'
            f'<rect width="{w}" height="{h}" fill="white"/>{body}</svg>')


def callout(x, y, w, title, rows):
    h = 62 + 34 * len(rows)
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="white" stroke="{B}" stroke-width="4"/>',
         t(x + 24, y + 42, title, 26, 700, B, "start")]
    o += [t(x + 24, y + 80 + 34 * i, r, 22, 500, INK, "start") for i, r in enumerate(rows)]
    return "".join(o)


def write(name, text):
    (OUT / name).write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- stage maps
STAGES = [("status", "Status"), ("functions", "Functions"), ("scorecards", "Scorecards"), ("kffm", "KFFM"),
          ("values", "Core|Values"), ("people", "A-Player|Team"),
          ("attribution", "Attribution|Framework"), ("strategy", "3HAG"), ("annual", "1HAG"), ("plan", "QHAG"),
          ("lanes", "Sprint|Lanes"), ("priorities", "Individual|Priorities"), ("forecast", "Forecast"), ("close", "Meetings|and close")]
PER_ROW = 7


def path_svg(current):
    """Two rows of seven, so the labels read from the back of the room. Every stop names what the team works on (Byron, review 25-Nov-2026)."""
    W, H = 1440, 464
    o = [t(40, 52, "Q3", 28, 700, "#6b7780", "start", ' letter-spacing="2"')]
    gap, w, h, x0 = 20, 176, 150, 42
    rows = [84, 284]
    for i, (key, label) in enumerate(STAGES):
        done, now = i < current, i == current
        col, y = i % PER_ROW, rows[i // PER_ROW]
        x = x0 + col * (w + gap)
        mid = y + h / 2
        stroke = G if done else LINE
        if col < PER_ROW - 1:
            o.append(f'<line x1="{x + w}" y1="{mid}" x2="{x + w + gap}" y2="{mid}" stroke="{stroke}" stroke-width="5"/>')
        elif i < len(STAGES) - 1:
            between = (rows[0] + h + rows[1]) / 2
            nxt = rows[1] + h / 2
            o.append(f'<polyline points="{x + w},{mid} {x + w + 18},{mid} {x + w + 18},{between} {x0 - 20},{between} {x0 - 20},{nxt} {x0},{nxt}" '
                     f'fill="none" stroke="{stroke}" stroke-width="5" stroke-linejoin="round"/>')
        cx = x + w / 2
        two = label.split("|")
        top = y + (58 if len(two) == 1 else 44)
        if now:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{B}"/>')
            o.append(lines(cx, y + (86 if len(two) == 1 else 68), two, 28, 34, 700, "white"))
        elif done:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{GFILL}" stroke="{G}" stroke-width="3"/>')
            o.append(lines(cx, top, two, 27, 34, 700, INK))
            o.append(t(cx, y + 122, "✓ Done", 24, 700, G))
        else:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="white" stroke="{LINE}" stroke-width="3"/>')
            o.append(lines(cx, y + (86 if len(two) == 1 else 68), two, 27, 34, 600, MUTE))
    return svg(W, H, "".join(o))


for i, (key, _) in enumerate(STAGES):
    write(f"q3-path-{key}.svg", path_svg(i))


# ---------------------------------------------------------------- Mission to Mars
# Step names and wording follow the master board's Mission to Mars area.
# Step 1 has no "not in the room"; step 2 has each person share (Byron, 25-Nov-2026).
MARS = [("Pick three|people", ["Each person", "picks three", "people.", "Name the value", "each one lives."]),
        ("Share and|cluster", ["Each person says", "who they picked", "and why. Move", "similar values", "together. Name", "each cluster."]),
        ("Vote", ["Three votes each,", "on the clusters", "that best show", "your values."]),
        ("Test the|top three", ["Test each one.", "Talk about", "anything", "left out."]),
        ("Agree on the|Core Values", ["Name each value.", "Write the", "behavior", "it means."])]


def mars_steps():
    W, H = 1440, 520
    o = []
    w, gap, x0, y, h = 252, 30, 30, 20, 480
    for i, (name, rows) in enumerate(MARS):
        x = x0 + i * (w + gap)
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white" stroke="{LINE}" stroke-width="3"/>')
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="8" fill="{SEQ[i]}"/>')
        o.append(f'<circle cx="{x + 48}" cy="{y + 68}" r="28" fill="{B}"/>')
        o.append(t(x + 48, y + 79, str(i + 1), 31, 700, "white"))
        o.append(lines(x + 22, y + 152, name.split("|"), 33, 40, 700, INK, "start"))
        o.append(lines(x + 22, y + 266, rows, 26, 36, 500, MUTE, "start"))
        if i < len(MARS) - 1:
            ax = x + w + 4
            o.append(f'<path d="M{ax},{y + 68} l{gap - 9},0 m-10,-9 l10,9 l-10,9" fill="none" stroke="{B}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(W, H, "".join(o))


write("mars-steps.svg", mars_steps())


# ---------------------------------------------------------------- A-Player Team Assessment
# Axis labels and explanations are the master board's "A-Player Team Assessment" area
# (Shannon's ABC Team Assessment, Updated Guidance, November 2025). "Being Carried": Byron, 17-Nov-2026.
# Row descriptions: Byron, 25-Nov-2026. One value never lived puts a person in the bottom row.
VALUE_ROWS = [("Most of the time", ["Every Core Value", "is lived most", "of the time."]),
              ("Some of the time", ["The lowest-rated", "Core Value is lived", "some of the time."]),
              ("None of the time", ["At least one", "Core Value is lived", "none of the time."])]
PERF_COLS = [("Being Carried", ["Not meeting most", "of the scorecard"]),
             ("Behind", ["Meets most", "of the scorecard"]),
             ("Ahead", ["Meets or exceeds all", "of the scorecard"])]
# person: (row, col, slot)
TEAM = {"Maya": (0, 2, 0), "Omar": (0, 2, 1), "Priya": (0, 2, 2), "Leo": (0, 1, 0), "Ravi": (1, 2, 0), "Nora": (0, 0, 0)}
GX, GY, CW, CH = 312, 60, 368, 142


def cell_xy(r, c):
    return GX + c * CW, GY + r * CH


def zone_of(r, c):
    return "A" if (r, c) == (0, 2) else "B" if (r, c) == (0, 1) else "C"


def grid(people=False, zones=False, dim=None, note=None):
    """dim: a set of names to keep bright; everyone else fades (rule 9)."""
    W, H = 1440, 660
    o = []
    o.append(t(24, 42, "Core Values", 30, 700, B, "start"))
    for r, (name, rows) in enumerate(VALUE_ROWS):
        x, y = cell_xy(r, 0)
        o.append(t(24, y + 44, name, 28, 700, INK, "start"))
        o.append(lines(24, y + 78, rows, 23, 27, 500, MUTE, "start"))
    for r in range(3):
        for c in range(3):
            x, y = cell_xy(r, c)
            fill, stroke = "white", LINE
            if zones:
                z = zone_of(r, c)
                fill = GFILL if z == "A" else YELLOW if z == "B" else OFILL
                stroke = G if z == "A" else YLINE if z == "B" else ORANGE
            o.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
            if zones:
                o.append(t(x + CW - 20, y + 40, z, 36, 700, G if z == "A" else "#8a7a12" if z == "B" else ORANGE, "end"))
    for c, (name, hint) in enumerate(PERF_COLS):
        x, y = cell_xy(3, c)
        o.append(t(x + CW / 2, y + 40, name, 28, 700, INK))
        o.append(lines(x + CW / 2, y + 72, hint, 23, 27, 500, MUTE))
    o.append(t(GX + 1.5 * CW, GY + 3 * CH + 150, "Performance Expectations", 30, 700, B))
    if people:
        for name, (r, c, slot) in TEAM.items():
            x, y = cell_xy(r, c)
            sx, sy = x + 14 + slot * 114, y + 48
            op = "" if dim is None or name in dim else ' opacity="0.28"'
            o.append(f'<g{op}><rect x="{sx}" y="{sy}" width="104" height="80" fill="white" stroke="{MUTE}" stroke-width="2"/>'
                     + t(sx + 52, sy + 50, name, 27, 600, INK) + "</g>")
        o.append(t(GX + 3 * CW, 42, "Jen’s direct reports", 24, 600, MUTE, "end"))
    if note:
        # the callout fills the empty box beside the person it points at
        nx, ny, nw, title, rows, (px, py) = note
        o.append(f'<line x1="{nx + nw}" y1="{ny + 66}" x2="{px}" y2="{py}" stroke="{B}" stroke-width="4"/>')
        o.append(callout(nx, ny, nw, title, rows))
    return svg(W, H, "".join(o))


write("a-player-grid.svg", grid())
write("a-player-placed.svg", grid(people=True))
write("a-player-zones.svg", grid(people=True, zones=True))
write("a-player-ravi.svg", grid(people=True, zones=True, dim={"Ravi"}, note=(
    GX + CW + 8, GY + CH + 6, CW - 34, "Still a C", ["A high performer who", "breaks a Core Value."], (GX + 2 * CW + 14, GY + CH + 88))))

PLANS = [("Leo", "B", ["Close the gap to Ahead", "on the scorecard."], "Jen", "Weekly 1:1", "Within 90 days"),
         ("Ravi", "C", ["Name the value and the behavior.", "Decide: does Ravi fit?"], "Jen", "Weekly 1:1", "Within 30 days"),
         ("Nora", "C", ["Set the scorecard standard.", "Decide: improve or move on."], "Jen", "Weekly 1:1", "Within 30 days")]


def plans():
    W, H = 1440, 520
    cols = [("Person", 24, 190), ("Plan", 214, 540), ("Accountable|leader", 754, 210),
            ("Next|check-in", 964, 200), ("Decision or|completion date", 1164, 262)]
    o = []
    for name, x, w in cols:
        rows = name.split("|")
        o.append(lines(x + 14, 78 if len(rows) == 1 else 50, rows, 24, 28, 700, MUTE, "start"))
    for i, (person, zone, plan, leader, check, date) in enumerate(PLANS):
        y = 104 + i * 134
        fill, stroke = (YELLOW, YLINE) if zone == "B" else (OFILL, ORANGE)
        for (name, x, w), val in zip(cols, [None, plan, [leader], [check], [date]]):
            o.append(f'<rect x="{x}" y="{y}" width="{w - 10}" height="120" rx="8" fill="{fill if val is None else "white"}" '
                     f'stroke="{stroke if val is None else LINE}" stroke-width="2"/>')
            if val is None:
                o.append(t(x + 16, y + 70, person, 31, 700, INK, "start"))
                o.append(t(x + w - 28, y + 72, zone, 34, 700, "#8a7a12" if zone == "B" else ORANGE, "end"))
            else:
                o.append(lines(x + 16, y + 69 - (len(val) - 1) * 17, val, 26, 34, 500, INK, "start"))
    return svg(W, H, "".join(o))


write("a-player-plans.svg", plans())


# ---------------------------------------------------------------- Attribution Framework
# Twelve market attributes, scored 1 to 5, ordered best to worst for the company (ruling 9).
ATTRS = [("Speed of|setup", 4, 3, 1, 3, 5), ("Ease of|use", 4, 4, 2, 3, 4), ("Price|predictability", 4, 2, 2, 3, 5),
         ("Reliability", 4, 4, 4, 2, 4), ("Billing|simplicity", 3, 3, 2, 3, 4), ("Support from|a person", 3, 1, 4, 1, 5),
         ("Security", 3, 4, 4, 2, 3), ("Integrations", 3, 5, 3, 1, 3), ("Reporting", 3, 3, 4, 1, 2),
         ("Feature|breadth", 2, 4, 5, 1, 2), ("Customization", 2, 2, 5, 1, 1), ("Partner|network", 2, 3, 5, 1, 2)]
SERIES = [("Us today", 1, B, 7, ""), ("Competitor A", 2, "#7a858e", 4, ' stroke-dasharray="14 8"'),
          ("Competitor B", 3, "#7a858e", 4, ' stroke-dasharray="3 9" stroke-linecap="round"'),
          ("Competitor C", 4, "#7a858e", 4, ' stroke-dasharray="22 8 4 8"'), ("3HAG line", 5, G, 7, "")]
AX0, AX1, AY5, AY1 = 130, 1380, 112, 472


def ax(i):
    return AX0 + (AX1 - AX0) * i / (len(ATTRS) - 1)


def ay(v):
    return AY1 - (AY1 - AY5) * (v - 1) / 4


def attribution(show=("Us today", "Competitor A", "Competitor B", "Competitor C", "3HAG line"), bright=None,
                white_space=False, labels_bright=True, note=None):
    """show: the lines drawn. bright: the lines kept at full strength; the rest fade (rule 9)."""
    W, H = 1440, 770
    o = []
    for v in range(1, 6):
        o.append(f'<line x1="{AX0 - 28}" y1="{ay(v)}" x2="{AX1 + 12}" y2="{ay(v)}" stroke="{LINE}" stroke-width="2"/>')
        o.append(t(AX0 - 44, ay(v) + 9, str(v), 26, 600, MUTE, "end"))
    o.append(t(24, 48, "Score", 24, 700, MUTE, "start"))
    lop = "" if labels_bright else ' opacity="0.35"'
    for i, row in enumerate(ATTRS):
        ly = 522 + (i % 2) * 74
        o.append(f'<g{lop}><line x1="{ax(i)}" y1="{AY1 + 8}" x2="{ax(i)}" y2="{ly - 26}" stroke="{LINE}" stroke-width="2"/>'
                 + lines(ax(i), ly, row[0].split("|"), 24, 28, 600, INK) + "</g>")
    if white_space:
        top = [max(r[1:5]) for r in ATTRS]
        pts = [f"{AX0 - 28},{AY5 - 12}"] + [f"{AX1 + 12},{AY5 - 12}"]
        pts += [f"{AX1 + 12},{ay(top[-1]) - 14}"] + [f"{ax(i)},{ay(top[i]) - 14}" for i in range(len(ATTRS) - 1, -1, -1)]
        pts += [f"{AX0 - 28},{ay(top[0]) - 14}"]
        o.append(f'<polygon points="{" ".join(pts)}" fill="{GFILL}" stroke="{G}" stroke-width="2" stroke-dasharray="6 6"/>')
    for name, col, colour, width, dash in SERIES:
        if name not in show:
            continue
        op = "" if bright is None or name in bright else ' opacity="0.22"'
        pts = " ".join(f"{ax(i)},{ay(r[col])}" for i, r in enumerate(ATTRS))
        dots = "".join(f'<circle cx="{ax(i)}" cy="{ay(r[col])}" r="{7 if width > 4 else 5}" fill="{colour}"/>' for i, r in enumerate(ATTRS))
        end = t(AX1 + 22, ay(ATTRS[-1][col]) + 9, name[-1], 25, 700, colour, "start") if name.startswith("Competitor") else ""
        o.append(f'<g{op}><polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round"{dash}/>{dots}{end}</g>')
    # legend, in the sheet's column order
    lx = 150
    for name, col, colour, width, dash in SERIES:
        if name not in show:
            continue
        op = "" if bright is None or name in bright else ' opacity="0.3"'
        o.append(f'<g{op}><line x1="{lx}" y1="40" x2="{lx + 56}" y2="40" stroke="{colour}" stroke-width="{width}"{dash}/>'
                 + t(lx + 68, 49, name, 25, 600, INK, "start") + "</g>")
        lx += 68 + len(name) * 14 + 48
    if note:
        nx, ny, nw, title, rows = note
        o.append(callout(nx, ny, nw, title, rows))
    return svg(W, H, "".join(o))


write("attribution-example.svg", attribution())
write("attribution-attributes.svg", attribution(bright=(), note=(
    330, 220, 780, "Why: the market sets the attributes, not our product.", ["Ask: what describes the whole market?"])))
write("attribution-us.svg", attribution(bright=("Us today",), note=(
    290, 664, 860, "Why: an honest score shows where we stand today.", ["Ask: how well do we serve each attribute, 1 to 5?"])))
write("attribution-competitors.svg", attribution(bright=("Competitor A", "Competitor B", "Competitor C"), labels_bright=False, note=(
    290, 664, 860, "Why: the lines show where everyone competes.", ["Ask: how would each competitor score?"])))
write("attribution-white-space.svg", attribution(bright=(), white_space=True, labels_bright=False, note=(
    290, 664, 860, "Why: white space is a position with no rivals.", ["Ask: where on the graph is nothing drawn?"])))
write("attribution-3hag.svg", attribution(bright=("3HAG line",), labels_bright=False, note=(
    290, 664, 860, "Why: a real position means trade-offs.", ["Ask: what could we afford not to be as good at?"])))


# ---------------------------------------------------------------- QR codes
def qr_block(x, y, size, url):
    m = qr_svg.encode(url)
    n = len(m) + 8
    cell = size / n
    d = "".join(f"M{x + (c + 4) * cell:.2f},{y + (r + 4) * cell:.2f}h{cell:.2f}v{cell:.2f}h-{cell:.2f}z"
                for r, row in enumerate(m) for c, on in enumerate(row) if on)
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="white"/><path d="{d}" fill="{INK}"/>'


def links(items):
    """One to three QR cards, in the layout of the Q1 forecast examples and the Q2 Core Customer links."""
    n = len(items)
    W, H = (660 if n == 1 else 1440), 640
    size = 380 if n < 3 else 330
    half = 290 if n < 3 else 222
    centres = {1: [330], 2: [380, 1060], 3: [240, 720, 1200]}[n]
    o = []
    for i, (title, sub, url, caption) in enumerate(items):
        cx = centres[i]
        colour = G if i == 0 else B
        o.append(f'<rect x="{cx - half}" y="20" width="{2 * half}" height="600" rx="8" fill="white" stroke="{LINE}" stroke-width="3"/>')
        o.append(f'<rect x="{cx - half}" y="20" width="{2 * half}" height="8" fill="{colour}"/>')
        o.append(t(cx, 92, title, 34, 700, INK))
        subs = sub.split("|")
        o.append(lines(cx, 134 if len(subs) == 1 else 128, subs, 24 if n < 3 else 23, 28, 500, MUTE))
        o.append(qr_block(cx - size / 2, 160 if n < 3 else 196, size, url))
        o.append(t(cx, 590, caption, 22 if n < 3 else 21, 600, colour))
    return svg(W, H, "".join(o))


DAR = "https://www.darlison.com/"
write("values-links.svg", links([
    ("Read the article", "Values: How Not To|Chase Your Tail", DAR + "values-how-not-to-chase-your-tail/", "darlison.com"),
    ("Read the article", "How to Discover Your|Company’s Values Using AI", DAR + "how-to-discover-your-companys-values-using-ai/", "darlison.com"),
    ("Run the prompt", "Values Discovery", DAR + "values-discovery-prompt/", "darlison.com")]))
write("a-player-links.svg", links([
    ("Read the article", "Who On Your Team Is An A-Player?", DAR + "a-player-team-assessment/", "darlison.com/a-player-team-assessment"),
    ("Run the prompt", "A-Player Team Assessment Prep", DAR + "a-player-team-assessment-prompt/", "darlison.com/a-player-team-assessment-prompt")]))
write("attribution-sheet.svg", links([
    ("Attribution Map sheet", "Make a copy, then enter your scores.",
     "https://docs.google.com/spreadsheets/d/1U7ezTJPoIBdC1HR5Z2H_XcRE0TcOxMHL4_XNJET0j3A/edit", "Google Sheets: File, then Make a copy")]))
write("cash-12-month.svg", links([
    ("12-month forecast", "The finance leader builds next year in this.",
     "https://docs.google.com/spreadsheets/d/1Gopb6QtY_HixT8lOjo7Tu4HZ-2Yy2M02jxbSptdoSJM/edit#gid=1174451209", "Google Sheets: File, then Make a copy")]))


# ---------------------------------------------------------------- purpose note
def sticky():
    """The Kick Off's sticky with its handwriting replaced (Pillow, Chalkboard font), as at Q1 and Q2."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    src = Image.open(OUT / "two-days-sticky.jpg").convert("RGB")
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).polygon([(400, 300), (1055, 262), (1075, 520), (1010, 548), (985, 612), (415, 640)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    pts = [(450, 255), (640, 250), (960, 300), (430, 660), (700, 660), (380, 420)]
    colour = tuple(sum(src.getpixel(q)[c] for q in pts) // len(pts) for c in range(3))
    patch = Image.new("RGBA", src.size, colour + (255,))
    patch.putalpha(mask)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Chalkboard.ttc", 96)
    text = Image.new("RGBA", (660, 330), (0, 0, 0, 0))
    td = ImageDraw.Draw(text)
    for i, row in enumerate(["3HAG", "validation"]):
        w = td.textlength(row, font=font)
        td.text(((660 - w) / 2, 40 + i * 118), row, font=font, fill=(38, 42, 44, 255))
    text = text.rotate(3.5, expand=True, resample=Image.BICUBIC)
    patch.alpha_composite(text, (405, 262))
    out = Image.alpha_composite(src.convert("RGBA"), patch).convert("RGB")
    out.save(OUT / "q3-sticky.jpg", quality=90)
    b64 = base64.b64encode((OUT / "q3-sticky.jpg").read_bytes()).decode()
    write("q3-sticky-checked.svg",
          '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1672" height="940" '
          f'viewBox="0 0 1672 940" role="img"><image width="1672" height="940" href="data:image/jpeg;base64,{b64}"/>'
          '<path d="M70,560 C105,595 140,640 175,690 C235,560 300,440 400,330" fill="none" stroke="#54b570" '
          'stroke-width="42" stroke-linecap="round" stroke-linejoin="round"/></svg>')


# Pillow draws the handwriting a little differently from one version to the next,
# so keep the approved image. Delete q3-sticky.jpg to redraw it.
if not (OUT / "q3-sticky.jpg").exists():
    sticky()
print("wrote the Q3 drawings to", OUT)

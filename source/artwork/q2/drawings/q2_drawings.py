#!/usr/bin/env python3
"""Q2 deck drawings, generated so they stay consistent and editable.

- q2-path-<stage>.svg: the day's stage map, one per stage (rule 8: show where we are).
- core-customer-example.svg: the worked Core Customer for the same subscription company,
  in the layout of the master board's Core Customer area (Agreed Core Customers).
- sprint-lanes-example.svg, sprint-lanes-widgets.svg and sprint-lanes-lanes.svg: the worked
  13-Week Sprint Lanes in the board's layout as an overview, then each block on its own with
  one callout, so its type is large enough to read on a projector (as the QHAG blocks are at Q1).
- sprint-lane-one.svg: lane #1 on its own, large enough to read each weekly step.
- weekly-number.svg: one month's number shared across its weeks.
- q2-sticky.jpg and q2-sticky-checked.svg: the purpose note, from the Kick Off's sticky image.

The example's numbers come from the Kick Off QHAG page (qhag-map.svg): the quarter's widgets by
month, the three priorities, their owners and done-by dates. The Core Customer comes from the
Q1 Market Map example (small businesses, 55% of revenue). Edit here, then run:

    /usr/bin/python3 source/artwork/q2/drawings/q2_drawings.py
"""
from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "libraries" / "kickoff" / "assets"
STYLE = re.search(r"<style>.*?</style>", (OUT / "hag-ladder.svg").read_text(), re.S).group(0)

B = "#326ab6"; G = "#318549"; INK = "#20282f"; MUTE = "#5b6670"; GREY = "#9aa3ab"; LINE = "#d5d9dd"
GFILL = "#e7f2ea"; BFILL = "#e8eef8"; CARD = "#f6f4ef"


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


# ---------------------------------------------------------------- stage maps
STAGES = [("status", "Status"), ("functions", "Functions"), ("scorecards", "Scorecards"), ("kffm", "KFFM"),
          ("culture", "Culture"), ("customer", "Core|Customer"),
          ("strategy", "3HAG"), ("annual", "1HAG"), ("plan", "QHAG"), ("lanes", "Sprint|Lanes"), ("priorities", "Individual|Priorities")]


def path_svg(current):
    """Six stops on the first row and five on the second. Row one runs into row two.
    Every stop is named for what the team works on there (Byron, review of the Q2 deck, 25-Nov-2026)."""
    W, H = 1440, 464
    o = [t(40, 52, "Q2", 28, 700, "#6b7780", "start", ' letter-spacing="2"')]
    gap, w, h, x0, N = 24, 206, 150, 40, 6
    rows = [84, 284]
    for i, (key, label) in enumerate(STAGES):
        done, now = i < current, i == current
        col, y = i % N, rows[i // N]
        x = x0 + col * (w + gap)
        mid = y + h / 2
        stroke = G if done else LINE
        if col < N - 1 and i < len(STAGES) - 1:
            o.append(f'<line x1="{x + w}" y1="{mid}" x2="{x + w + gap}" y2="{mid}" stroke="{stroke}" stroke-width="5"/>')
        elif i < len(STAGES) - 1:
            between = (rows[0] + h + rows[1]) / 2
            nxt = rows[1] + h / 2
            o.append(f'<polyline points="{x + w},{mid} {x + w + 20},{mid} {x + w + 20},{between} {x0 - 20},{between} {x0 - 20},{nxt} {x0},{nxt}" '
                     f'fill="none" stroke="{stroke}" stroke-width="5" stroke-linejoin="round"/>')
        cx = x + w / 2
        two = label.split("|")
        top = y + (58 if len(two) == 1 else 44)
        if now:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{B}"/>')
            o.append(lines(cx, y + (86 if len(two) == 1 else 68), two, 30, 34, 700, "white"))
        elif done:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{GFILL}" stroke="{G}" stroke-width="3"/>')
            o.append(lines(cx, top, two, 28, 34, 700, INK))
            o.append(t(cx, y + 122, "✓ Done", 25, 700, G))
        else:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="white" stroke="{LINE}" stroke-width="3"/>')
            o.append(lines(cx, y + (86 if len(two) == 1 else 68), two, 28, 34, 600, MUTE))
    return svg(W, H, "".join(o))


for i, (key, _) in enumerate(STAGES):
    (OUT / f"q2-path-{key}.svg").write_text(path_svg(i), encoding="utf-8")


# ---------------------------------------------------------------- core customer
# Labels and explanations are the master board's "Agreed Core Customers" block, in its order:
# Core Customer, Description, Prioritized Needs, Prioritized Benefits, Persona, Revenue and Profit.
NEEDS = [["Up and running", "in days"], ["A cost they", "can predict"], ["A person to call", "when stuck"]]
BENEFITS = [["Live in 5 days", "or fewer"], ["One flat", "monthly price"], ["A named contact", "for 90 days"]]


def core_customer():
    W, H = 1440, 512
    o = []

    def head(x, y, label, hint):
        o.append(t(x, y + 30, label, 27, 700, B, "start"))
        o.append(t(x, y + 57, hint, 20, 500, MUTE, "start"))

    def card(x, y, w, h, rows, size=24, num=None):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{GFILL}" stroke="{G}" stroke-width="2"/>')
        if num:
            o.append(f'<circle cx="{x + 32}" cy="{y + h / 2}" r="19" fill="{B}"/>')
            o.append(t(x + 32, y + h / 2 + 7, str(num), 20, 700, "white"))
            o.append(lines(x + 64, y + h / 2 + 8 - (len(rows) - 1) * 14, rows, size, 28, 600, INK, "start"))
        else:
            o.append(lines(x + w / 2, y + h / 2 + 8 - (len(rows) - 1) * 14, rows, size, 28, 600, INK))

    LX, LW, RX, CWD = 24, 640, 704, 349
    head(LX, 8, "Core Customer", "Name them.")
    card(LX, 76, LW, 64, ["Owner of a small business"])
    head(LX, 158, "Description", "Who makes the buying decision. 50 words or fewer.")
    card(LX, 226, LW, 110, ["The owner of a business with 10 to 50 staff.", "Decides alone, pays by card, and wants it",
                            "working this month, without an IT person."], 22)
    head(RX, 8, "Prioritized Needs", "Ranked. Needs, not wants.")
    head(RX + CWD + 14, 8, "Prioritized Benefits", "What we offer that meets those needs.")
    for i in range(3):
        card(RX, 76 + i * 90, CWD, 80, NEEDS[i], 22, i + 1)
        card(RX + CWD + 14, 76 + i * 90, CWD, 80, BENEFITS[i], 22, i + 1)
    head(LX, 356, "Persona", "Give them a name and a face.")
    card(LX, 424, LW, 64, ["Dana, owner of a 20-person business"])
    head(RX, 356, "Revenue and Profit", "Share of revenue and profit from this customer.")
    for i, (k, v) in enumerate([("Revenue", "55%"), ("Profit", "60%")]):
        x = RX + i * (CWD + 14)
        o.append(f'<rect x="{x}" y="424" width="{CWD}" height="64" rx="10" fill="{GFILL}" stroke="{G}" stroke-width="2"/>')
        o.append(t(x + CWD / 2 - 12, 465, k, 23, 500, MUTE, "end"))
        o.append(t(x + CWD / 2, 467, v, 31, 700, INK, "start"))
    return svg(W, H, "".join(o))


(OUT / "core-customer-example.svg").write_text(core_customer(), encoding="utf-8")


# ---------------------------------------------------------------- sprint lanes
# Months of the example quarter and how many of its 13 weeks fall in each (4, 4, 5).
MONTHS = ["January", "February", "March"]
WEEKS = [4, 4, 5]
WIDGETS = [  # name (two lines when long), owner, the month numbers from the Kick Off QHAG page
    (["Subscription leads"], "Chris", [650, 700, 750]),
    (["Marketing qualified", "subscription leads"], "Chris", [260, 280, 300]),
    (["New subscriptions"], "Andrew", [65, 70, 75]),
    (["Activated subscriptions"], "Jen", [60, 65, 70]),
    (["Collected payments"], "Allison", [1550, 1600, 1650]),
]
DONE = None  # a week after the priority is complete
# One checkable step for each active week. Lines hold 8 characters or fewer so they fit a week cell.
# Week 8 ends February 28, week 10 ends March 14 and week 13 ends March 31 or just after.
LANES = [  # priority, owner, done by, steps
    ("#1", ["Remove the first", "2 days of activation"], "Jen", "Feb 28", [
        ["Steps", "mapped"], ["Slowest", "2 days", "found"], ["Fix", "chosen"], ["Welcome", "flow", "drafted"],
        ["Tested", "with 5", "accounts"], ["Team", "trained"], ["New flow", "live"], ["Old flow", "switched", "off"],
        DONE, DONE, DONE, DONE, DONE]),
    ("#2", ["Hire the first", "account executive"], "Andrew", "Mar 15", [
        ["Role", "defined"], ["Job", "posted"], ["10", "sourced"], ["Phone", "screens", "done"],
        ["Top 3", "picked"], ["First", "round", "done"], ["Final", "round", "done"], ["Refs", "checked"],
        ["Offer", "made"], ["Offer", "signed"], DONE, DONE, DONE]),
    ("#3", ["Move the 100 largest", "customers to", "automatic billing"], "Allison", "Mar 31", [
        ["List of", "100", "agreed"], ["Billing", "tool", "set up"], ["Script", "approved"], ["First 10", "moved"],
        ["25", "moved"], ["40", "moved"], ["55", "moved"], ["70", "moved"],
        ["80", "moved"], ["90", "moved"], ["95", "moved"], ["Holdouts", "called"], ["100", "moved"]]),
]


def share(total, n):
    """Share a month's number across its n weeks, whole numbers that add up to the month."""
    base, extra = divmod(total, n)
    return [base + (1 if i >= n - extra else 0) for i in range(n)]


def weekly(months):
    out = []
    for total, n in zip(months, WEEKS):
        out += share(total, n)
    return out


SW = 1440


class Grid:
    """Week columns. `label` is the width of the name column; `k` scales the type.
    `floor` is the smallest type on the page, in drawing units. The page shows at about 0.76
    of its size at 1280 by 720, so 17.2 units is the 13-pixel floor (visual standard, rule 32)."""
    def __init__(self, label, k, floor=18):
        self.x0 = label
        self.cw = (SW - label - 10) / 13
        self.k = k
        self.floor = floor

    def f(self, size):
        """A type size scaled by k, never under the floor."""
        return round(max(size * self.k, self.floor), 2)

    def head(self, y):
        o, w0 = [], 0
        for name, n in zip(MONTHS, WEEKS):
            x = self.x0 + w0 * self.cw
            o.append(f'<rect x="{x + 3}" y="{y}" width="{n * self.cw - 6}" height="{30 * self.k:.0f}" rx="6" fill="{CARD}"/>')
            o.append(t(x + n * self.cw / 2, y + 22 * self.k, name, self.f(19), 700, MUTE))
            w0 += n
        y += 34 * self.k
        for w in range(13):
            o.append(t(self.x0 + w * self.cw + self.cw / 2, y + 22 * self.k, f"Wk {w + 1}", self.f(19), 700, MUTE))
        return "".join(o), y + 30 * self.k

    def band(self, y, title):
        return (f'<rect x="10" y="{y}" width="{SW - 20}" height="{34 * self.k:.0f}" rx="6" fill="{BFILL}"/>'
                + t(22, y + 24 * self.k, title, self.f(20), 700, B, "start")), y + 40 * self.k

    def widgets(self, y, rh, inline=False):
        """inline: the owner sits at the end of the name's last line, for a page with short rows."""
        o, y = [self.band(y, "Company Widgets: Week by Week")[0]], y + 40 * self.k
        k = self.k
        for name, owner, months in WIDGETS:
            if inline:
                top = y + rh / 2 - (len(name) * 20 * k) / 2 + 16 * k
                o.append(lines(18, top, name, self.f(19), 20 * k, 700, INK, "start"))
                o.append(t(self.x0 - 10, top + (len(name) - 1) * 20 * k, owner, self.f(17), 500, MUTE, "end"))
            else:
                top = y + rh / 2 - (len(name) * 20 * k + 18 * k) / 2 + 16 * k
                o.append(lines(18, top, name, self.f(19), 20 * k, 700, INK, "start"))
                o.append(t(18, top + len(name) * 20 * k, owner, self.f(17), 500, MUTE, "start"))
            for w, v in enumerate(weekly(months)):
                cx = self.x0 + w * self.cw
                o.append(f'<rect x="{cx + 3:.1f}" y="{y + 3}" width="{self.cw - 6:.1f}" height="{rh - 6}" rx="6" fill="{GFILL}" stroke="{G}" stroke-width="1.5"/>')
                o.append(t(cx + self.cw / 2, y + rh / 2 + 8 * k, f"{v:,}", 23 * k, 700, INK))
            y += rh
        return "".join(o), y

    def lanes(self, y, rh):
        o, y = [self.band(y, "Company Priorities: Week by Week")[0]], y + 40 * self.k
        k = self.k
        for num, name, owner, by, steps in LANES:
            o.append(f'<circle cx="32" cy="{y + 24 * k}" r="{16 * k:.0f}" fill="{B}"/>')
            o.append(t(32, y + 24 * k + 6 * k, num[1:], self.f(18), 700, "white"))
            o.append(lines(56, y + 24 * k + 5 * k, name, self.f(18), 21 * k, 700, INK, "start"))
            o.append(t(56, y + 24 * k + 5 * k + 21 * k * len(name) + 2, f"{owner} · Done by {by}", self.f(17), 500, MUTE, "start"))
            for w, step in enumerate(steps):
                cx = self.x0 + w * self.cw
                box = f'<rect x="{cx + 3:.1f}" y="{y + 3}" width="{self.cw - 6:.1f}" height="{rh - 6}" rx="6" '
                if step is DONE:
                    # One box across the weeks after the priority is done, with one label:
                    # "Complete" does not fit a single week cell at a readable size.
                    if w and steps[w - 1] is DONE:
                        continue
                    span = len(steps) - w
                    o.append(f'<rect x="{cx + 3:.1f}" y="{y + 3}" width="{span * self.cw - 6:.1f}" height="{rh - 6}" rx="6" '
                             f'fill="{CARD}" stroke="{LINE}" stroke-width="1.5"/>')
                    o.append(t(cx + span * self.cw / 2, y + rh / 2 + 6 * k, "Complete", self.f(18), 700, MUTE))
                else:
                    o.append(box + f'fill="{GFILL}" stroke="{G}" stroke-width="1.5"/>')
                    lh = 21 * k
                    o.append(lines(cx + self.cw / 2, y + rh / 2 + 6 * k - (len(step) - 1) * lh / 2, step, self.f(18), lh, 600, INK))
            y += rh
        return "".join(o), y


def lanes_page(widgets=True, lanes=True, note=None, label=262, k=1.0, wrow=54, lrow=96, floor=18, inline=False):
    g = Grid(label, k, floor)
    body, y = g.head(4)
    if widgets:
        part, y = g.widgets(y + 6, wrow, inline)
        body += part
    if lanes:
        part, y = g.lanes(y + 10, lrow)
        body += part
    if note:
        y += 16
        body += callout(g.x0, y, SW - g.x0 - 10, *note)
        y += 62 + 34 * len(note[1])
    return svg(SW, round(y + 12), body)


# the whole page once: an overview of its shape, sized to fill a 16:9 panel
(OUT / "sprint-lanes-example.svg").write_text(lanes_page(label=272, k=0.92, wrow=46, lrow=84, floor=17.2, inline=True), encoding="utf-8")
# then each block on its own, at a size a projector can show
(OUT / "sprint-lanes-widgets.svg").write_text(lanes_page(lanes=False, wrow=66, note=(
    "Company Widgets: Week by Week",
    ["Why: a weekly number shows a miss while there is time to act.",
     "Ask: can each owner reach this week’s number?"])), encoding="utf-8")
(OUT / "sprint-lanes-lanes.svg").write_text(lanes_page(widgets=False, label=258, lrow=112, floor=17.2, note=(
    "Company Priorities: Week by Week",
    ["Why: the team sees each week how the priority gets done.",
     "Ask: what must be done this week to finish on time?"])), encoding="utf-8")


def lane_one():
    """Lane #1 by month, in the same words as the page: two months of steps, then done."""
    num, name, owner, by, steps = LANES[0]
    W, H = 1440, 548
    o = [f'<circle cx="46" cy="46" r="26" fill="{B}"/>', t(46, 55, "1", 28, 700, "white"),
         t(88, 30, "COMPANY PRIORITY #1", 19, 700, B, "start"),
         t(88, 68, " ".join(name), 32, 700, INK, "start"),
         t(1416, 56, f"Owner: {owner} · Done by {by}", 23, 600, MUTE, "end")]
    cw, ch, gx = 232, 190, 12
    for row, month in enumerate(MONTHS[:2]):
        y = 96 + row * (ch + 36)
        o.append(t(24, y + 22, month, 22, 700, MUTE, "start"))
        for col in range(4):
            w = row * 4 + col
            x = 24 + col * (cw + gx)
            o.append(f'<rect x="{x}" y="{y + 34}" width="{cw}" height="{ch - 34}" rx="12" fill="{GFILL}" stroke="{G}" stroke-width="2"/>')
            o.append(t(x + 18, y + 68, f"Wk {w + 1}", 21, 700, G, "start"))
            words = " ".join(steps[w]).split()
            cut = next((i for i in range(1, len(words)) if len(" ".join(words[:i + 1])) > 12), len(words))
            rows = [" ".join(words[:cut])] + ([" ".join(words[cut:])] if words[cut:] else [])
            o.append(lines(x + cw / 2, y + 128 - (len(rows) - 1) * 16, rows, 26, 32, 700, INK))
    x = 24 + 4 * (cw + gx) + 12
    o.append(t(x, 118, "March", 22, 700, MUTE, "start"))
    o.append(f'<rect x="{x}" y="130" width="{W - x - 24}" height="{2 * ch + 2}" rx="12" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>')
    mid = x + (W - x - 24) / 2
    o.append(t(mid, 296, "Priority complete", 32, 700, INK))
    o.append(t(mid, 340, "Weeks 9 to 13 need no steps.", 22, 600, MUTE))
    return svg(W, H, "".join(o))


(OUT / "sprint-lane-one.svg").write_text(lane_one(), encoding="utf-8")


# ---------------------------------------------------------------- weekly number
def weekly_number():
    W, H = 1440, 660
    o = []

    def row(y, label, gloss, month, cells, total, colour, fill, tag):
        o.append(t(24, y - 16, label, 25, 700, colour, "start"))
        o.append(t(24 + len(label) * 14.2 + 16, y - 16, gloss, 21, 500, MUTE, "start"))
        o.append(f'<rect x="24" y="{y}" width="316" height="116" rx="14" fill="white" stroke="{colour}" stroke-width="3"/>')
        o.append(t(182, y + 46, month, 22, 600, MUTE))
        o.append(t(182, y + 88, total, 27, 700, INK))
        o.append(f'<line x1="350" y1="{y + 58}" x2="392" y2="{y + 58}" stroke="{colour}" stroke-width="5"/>')
        o.append(f'<path d="M392,{y + 44} L416,{y + 58} L392,{y + 72} Z" fill="{colour}"/>')
        for i, v in enumerate(cells):
            x = 430 + i * 146
            o.append(f'<rect x="{x}" y="{y}" width="134" height="116" rx="14" fill="{fill}" stroke="{colour}" stroke-width="2"/>')
            o.append(t(x + 67, y + 42, f"Wk {i + 1}", 20, 700, MUTE))
            o.append(t(x + 67, y + 92, v, 36, 700, INK))
        o.append(lines(1172, y + 50, tag, 22, 30, 600, colour, "start"))

    row(64, "A produced number divides", "Made during the week: leads, subscriptions, payments.", "January, 4 weeks",
        [str(v) for v in share(65, 4)], "65 new subscriptions", G, GFILL, ["The weeks add", "up to the month."])
    row(276, "A longer month spreads further", "", "March, 5 weeks",
        [str(v) for v in share(75, 5)], "75 new subscriptions", G, GFILL, ["A higher month,", "a lower week."])
    row(488, "A held number does not divide", "A level you hold: head count, a backlog, a cash reserve.", "January, 4 weeks",
        ["30"] * 4, "Head count 30", B, BFILL, ["Every week shows", "the same number."])
    return svg(W, H, "".join(o))


(OUT / "weekly-number.svg").write_text(weekly_number(), encoding="utf-8")


# ---------------------------------------------------------------- core customer links
# Two QR codes: Byron's article and his Core Customer Discovery prompt (ruling 1: homework).
import sys
sys.path.insert(0, str(ROOT / "tools"))
import qr_svg  # noqa: E402

LINKS = [
    ("Read the article", "Who Is Your Most Valuable Customer?", "https://www.darlison.com/who-is-your-most-valuable-customer/"),
    ("Run the prompt", "Core Customer Discovery", "https://www.darlison.com/core-customer-discovery-prompt/"),
]


def qr_block(x, y, size, url):
    m = qr_svg.encode(url)
    n = len(m) + 8
    cell = size / n
    d = "".join(f"M{x + (c + 4) * cell:.2f},{y + (r + 4) * cell:.2f}h{cell:.2f}v{cell:.2f}h-{cell:.2f}z"
                for r, row in enumerate(m) for c, on in enumerate(row) if on)
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="white"/><path d="{d}" fill="{INK}"/>'


def core_customer_links():
    W, H, size = 1440, 640, 380
    o = []
    for i, (title, sub, url) in enumerate(LINKS):
        cx = 380 + i * 680
        o.append(f'<rect x="{cx - 270}" y="20" width="540" height="600" rx="8" fill="white" stroke="{LINE}" stroke-width="3"/>')
        o.append(f'<rect x="{cx - 270}" y="20" width="540" height="8" fill="{G if i == 0 else B}"/>')
        o.append(t(cx, 92, title, 34, 700, INK))
        o.append(t(cx, 134, sub, 24, 500, MUTE))
        o.append(qr_block(cx - size / 2, 160, size, url))
        o.append(t(cx, 590, url.replace("https://www.", "").rstrip("/"), 19, 600, G if i == 0 else B))
    return svg(W, H, "".join(o))


(OUT / "core-customer-links.svg").write_text(core_customer_links(), encoding="utf-8")



# ---------------------------------------------------------------- purpose note
def sticky():
    """The Kick Off's sticky with its handwriting replaced (Pillow, Chalkboard font), as at Q1."""
    from PIL import Image, ImageDraw, ImageFont
    src = Image.open(OUT / "two-days-sticky.jpg").convert("RGB")
    # cover the old handwriting with the note's own colour, sampled beside it
    from PIL import ImageFilter
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).polygon([(400, 300), (1055, 262), (1075, 520), (1010, 548), (985, 612), (415, 640)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    pts = [(450, 255), (640, 250), (960, 300), (430, 660), (700, 660), (380, 420)]
    colour = tuple(sum(src.getpixel(q)[c] for q in pts) // len(pts) for c in range(3))
    patch = Image.new("RGBA", src.size, colour + (255,))
    patch.putalpha(mask)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Chalkboard.ttc", 66)
    text = Image.new("RGBA", (660, 330), (0, 0, 0, 0))
    td = ImageDraw.Draw(text)
    for i, row in enumerate(["Planning and", "executing with", "increasing", "momentum"]):
        w = td.textlength(row, font=font)
        td.text(((660 - w) / 2, i * 78), row, font=font, fill=(38, 42, 44, 255))
    text = text.rotate(3.5, expand=True, resample=Image.BICUBIC)
    patch.alpha_composite(text, (405, 262))
    out = Image.alpha_composite(src.convert("RGBA"), patch).convert("RGB")
    out.save(OUT / "q2-sticky.jpg", quality=90)
    b64 = base64.b64encode((OUT / "q2-sticky.jpg").read_bytes()).decode()
    (OUT / "q2-sticky-checked.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1672" height="940" '
        f'viewBox="0 0 1672 940" role="img"><image width="1672" height="940" href="data:image/jpeg;base64,{b64}"/>'
        '<path d="M70,560 C105,595 140,640 175,690 C235,560 300,440 400,330" fill="none" stroke="#54b570" '
        'stroke-width="42" stroke-linecap="round" stroke-linejoin="round"/></svg>', encoding="utf-8")


# Pillow draws the handwriting a little differently from one version to the next,
# so keep the approved image. Delete q2-sticky.jpg to redraw it.
if not (OUT / "q2-sticky.jpg").exists():
    sticky()
print("wrote the Q2 drawings to", OUT)

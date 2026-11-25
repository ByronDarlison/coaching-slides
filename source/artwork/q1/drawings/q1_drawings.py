"""Draw the Q1 deck's diagrams.

Writes into libraries/kickoff/assets (artwork must sit in the library of the slides that use it):
- q1-path-<stage>.svg: the day's stage map, one per stage (rule 8: show where we are).
- market-map-example.svg and market-map-<part>.svg: the worked Market Map for the
  Kick Off's subscription company, then one dimmed copy per part with one callout
  (rule 9: point at the example; don't redraw it).
- team-view-example.svg and scorecard-example.svg.
- cash-rolling.svg and cash-rolling-miss.svg: the cash forecast chart, one set of numbers.
- cash-forecast-examples.svg: QR codes for the 12- and 36-month templates' Example tabs.

Fonts come from the embedded <style> in the Kick Off hag-ladder.svg. Edit here, then run:

    python3 source/artwork/q1/drawings/q1_drawings.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "libraries" / "kickoff" / "assets"
OUT.mkdir(parents=True, exist_ok=True)
STYLE = re.search(r"<style>.*?</style>", (ROOT / "libraries" / "kickoff" / "assets" / "hag-ladder.svg").read_text(), re.S).group(0)

B = "#326ab6"; G = "#318549"; INK = "#20282f"; MUTE = "#5b6670"; GREY = "#9aa3ab"; LINE = "#d5d9dd"
GFILL = "#e7f2ea"; BFILL = "#e8eef8"; CARD = "#f6f4ef"
R = "#b84034"; RFILL = "#f5c4bd"  # the KFFM "needs attention" red


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size, weight=500, fill=INK, anchor="middle", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'


def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">{STYLE}'
            f'<defs>{defs}</defs><rect width="{w}" height="{h}" fill="white"/>{body}</svg>')


# ---------------------------------------------------------------- stage maps
STAGES = [("status", "Status"), ("functions", "Functions"), ("scorecards", "Scorecards"), ("kffm", "KFFM"),
          ("culture", "Culture"), ("market-map", "Market Map"), ("strategy", "3HAG"), ("annual", "1HAG"), ("plan", "QHAG"), ("cash", "Cash")]


def path_svg(current):
    """Two rows of five, the same map as Q2, so the labels read from the back of the room.
    Every stop names what the team works on (Byron, review 25-Nov-2026)."""
    W, H = 1440, 464
    o = [t(40, 52, "Q1", 28, 700, "#6b7780", "start", ' letter-spacing="2"')]
    gap, w, h, x0, N = 30, 248, 150, 40, 5
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
        if now:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{B}"/>')
            o.append(t(cx, y + 86, label, 30, 700, "white"))
        elif done:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{GFILL}" stroke="{G}" stroke-width="3"/>')
            o.append(t(cx, y + 58, label, 28, 700, INK))
            o.append(t(cx, y + 122, "✓ Done", 25, 700, G))
        else:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="white" stroke="{LINE}" stroke-width="3"/>')
            o.append(t(cx, y + 86, label, 28, 600, MUTE))
    return svg(W, H, "".join(o))


for i, (key, _) in enumerate(STAGES):
    (OUT / f"q1-path-{key}.svg").write_text(path_svg(i), encoding="utf-8")


# ---------------------------------------------------------------- market map
# Layout and colours follow the master board's Market Map area: Customers, then Channels
# on the left (customers buy through channels), the company in the centre with
# Associations above and Competitors below, Suppliers then Paid Partners on the right.
# LABEL is the smallest type on the map. The example shows at 0.642 of its size on the
# quarterly check slides (1280 by 720, sidebar hidden), so 21 renders at 13.5 pixels:
# above the 13-pixel floor (visual standard, rule 32). Boxes are sized to hold their
# names at that size with 12 units clear each side.
LABEL = 21
# Money is drawn as bands whose thickness is the share: green in, blue out. The bands from
# customers to channels show the split (shares of all money in), each with its own label.
W, H = 1440, 760
ARROW = ""  # bands carry direction; kept so callers of svg(..., ARROW) still work
S = 1.8      # band thickness in px per percentage point
BAND_OPACITY = ".42"
COLOURS = {  # board sticky colour, and a darker edge
    "customers": ("#FFF28A", "#C9B52A"), "channels": ("#9FE0F5", "#3E9FC2"), "associations": ("#C5A3FF", "#7D55C7"),
    "suppliers": ("#8FE3D1", "#2F9C84"), "partners": ("#FFD8A8", "#D08A3C"), "competitors": ("#FF8A80", "#C94A40")}
# key: (label, header x, header y, [(id, name, pct, x, y, w, h)], money side)
GROUPS = {
    "customers": ("Customers", 24, 136, [("small", "Small businesses", 55, 24, 150, 228, 116),
                                         ("mid", "Mid-size companies", 35, 24, 282, 228, 104),
                                         ("np", "Non-profits", 10, 24, 402, 228, 70),
                                         ("schools", "Schools", 0, 24, 488, 228, 70)], "in"),
    "channels": ("Channels", 384, 136, [("res", "Resellers", 30, 384, 150, 176, 96),
                                        ("web", "Direct: website", 70, 384, 262, 176, 170),
                                        ("mkt", "App marketplaces", 0, 364, 452, 216, 70)], "in"),
    "associations": ("Associations", 470, 36, [("ia", "Industry association", 0, 470, 50, 232, 68),
                                               ("cc", "Chamber of commerce", 0, 716, 50, 254, 68)], None),
    "suppliers": ("Suppliers", 926, 162, [("dev", "Contract developers", 45, 926, 176, 230, 100),
                                          ("host", "Cloud hosting", 30, 926, 302, 230, 100),
                                          ("pay", "Payment processor", 10, 926, 466, 230, 90)], "out"),
    "partners": ("Paid Partners", 1190, 348, [("impl", "Implementation|partner", 15, 1190, 362, 226, 152)], "out"),
    "competitors": ("Competitors", 470, 606, [("ca", "Competitor A", 0, 470, 620, 160, 68),
                                              ("cb", "Competitor B", 0, 642, 620, 160, 68),
                                              ("cc2", "Competitor C", 0, 814, 620, 160, 68),
                                              ("subs", "Substitutes", 0, 986, 620, 327, 68)], None),
}
# players on the field we don't reach yet: drawn dashed, with no share
# (caption, keep the category fill): substitutes are competitors that are not companies
UNUSED = {"schools": ("Not served yet", False), "mkt": ("Not used", False), "subs": ("Do nothing, or build in-house", True)}
CO = (620, 250, 200, 240)  # company box: x, y, w, h
NODES = {nid: (x, y, w, h) for g in GROUPS.values() for nid, _, _, x, y, w, h in g[3]}
NODES["co"] = CO
# (from, to, share): the customer-to-channel split, then channels in, then money out
SPLIT = [("small", "res", 10), ("small", "web", 45), ("mid", "res", 20), ("mid", "web", 15), ("np", "web", 10)]
IN = [("res", "co", 30), ("web", "co", 70)]
SPEND = [("co", "dev", 45), ("co", "host", 30), ("co", "impl", 15), ("co", "pay", 10)]
OUT_GAPS = [10, 22, 14]  # between the company's outgoing bands; the partner band runs between hosting and payment


def stack(node, flows, side, gaps=None, gap=6):
    """Top and bottom of each band where it meets a node edge, stacked and centred on the node."""
    x, y, w, h = NODES[node]
    gaps = gaps or [gap] * (len(flows) - 1)
    total = sum(p * S for p in flows) + sum(gaps)
    top = y + h / 2 - total / 2
    out = []
    for i, p in enumerate(flows):
        out.append((top, top + p * S))
        top += p * S + (gaps[i] if i < len(gaps) else 0)
    return out


def ports():
    """Where every band leaves and lands, in board order so bands from one node never cross each other."""
    src, dst = {}, {}
    for flows, src_gaps in ((SPLIT, None), (IN, None), (SPEND, OUT_GAPS)):
        for node in dict.fromkeys(a for a, _, _ in flows):
            mine = [f for f in flows if f[0] == node]
            for f, span in zip(mine, stack(node, [p for _, _, p in mine], "out", src_gaps)):
                src[f] = span
        for node in dict.fromkeys(b for _, b, _ in flows):
            mine = [f for f in flows if f[1] == node]
            for f, span in zip(mine, stack(node, [p for _, _, p in mine], "in", gap=16 if node == "co" else 6)):
                dst[f] = span
    return src, dst


SRC, DST = ports()


def band_geom(f):
    a, b, _ = f
    ax, _, aw, _ = NODES[a]
    bx = NODES[b][0]
    return ax + aw, SRC[f], bx, DST[f]


def band(f, colour):
    x0, (t0, b0), x1, (t1, b1) = band_geom(f)
    xm = (x0 + x1) / 2
    d = (f"M{x0},{t0} C{xm},{t0} {xm},{t1} {x1},{t1} L{x1},{b1} C{xm},{b1} {xm},{b0} {x0},{b0} Z")
    return f'<path d="{d}" fill="{colour}" fill-opacity="{BAND_OPACITY}"/>'


def split_label(f, at=.3):
    """The split share, sitting on its own band near the customer it comes from."""
    x0, (t0, b0), x1, (t1, b1) = band_geom(f)
    s = 3 * at * at - 2 * at ** 3  # the band's vertical progress along its curve
    xm = (x0 + x1) / 2
    x = (1 - at) ** 3 * x0 + 3 * (1 - at) ** 2 * at * xm + 3 * (1 - at) * at * at * xm + at ** 3 * x1
    y = (t0 + b0) / 2 + ((t1 + b1) / 2 - (t0 + b0) / 2) * s
    return (f'<rect x="{x - 30}" y="{y - 15}" width="60" height="30" rx="15" fill="white" stroke="{G}" stroke-width="2.5"/>'
            + t(x, y + 7, f"{f[2]}%", LABEL, 700, G))


def split_bands():
    return "".join(band(f, G) for f in SPLIT) + "".join(split_label(f) for f in SPLIT)


def in_bands():
    return "".join(band(f, G) for f in IN)


def out_bands(only=None):
    return "".join(band(f, B) for f in SPEND if only is None or f[1] in only)


def group_svg(key, hi=False):
    label, hx, hy, items, side = GROUPS[key]
    fill, edge = COLOURS[key]
    o = [t(hx, hy, label, 22, 700, B, "start")]
    for nid, name, pct, x, y, w, h in items:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{B if hi else edge}" stroke-width="{4 if hi else 2.5}"/>')
        if nid in UNUSED:
            caption, keep = UNUSED[nid]
            o[-1] = o[-1].replace('stroke-width=', 'stroke-dasharray="9 7" stroke-width=')
            if not keep:
                o[-1] = o[-1].replace(f'fill="{fill}"', 'fill="white"')
            o.append(t(x + w / 2, y + h / 2 - 4, name, LABEL, 600, INK) + t(x + w / 2, y + h / 2 + 22, caption, LABEL, 600, INK if keep else "#6B7280"))
        elif pct and "|" in name:  # a name on two lines, then its share
            a, b = name.split("|")
            o.append(t(x + w / 2, y + h / 2 - 18, a, LABEL, 600, INK) + t(x + w / 2, y + h / 2 + 6, b, LABEL, 600, INK)
                     + t(x + w / 2, y + h / 2 + 37, f"{pct}%", 24, 700, G if side == "in" else B))
        elif pct:
            o.append(t(x + w / 2, y + h / 2 - 4, name, LABEL, 600, INK) + t(x + w / 2, y + h / 2 + 26, f"{pct}%", 24, 700, G if side == "in" else B))
        else:
            o.append(t(x + w / 2, y + h / 2 + 7, name, LABEL, 600, INK))
    return "".join(o)


def company():
    cx, cy, cw, ch = CO
    return (f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="#2E6B4F"/>'
            + t(cx + cw / 2, cy + ch / 2 - 4, "The company", 26, 700, "white") + t(cx + cw / 2, cy + ch / 2 + 28, "Subscriptions", LABEL, 600, "white"))


def legend():
    return (f'<rect x="24" y="716" width="64" height="22" rx="4" fill="{G}" fill-opacity="{BAND_OPACITY}"/>'
            + t(100, 734, "Money in", LABEL, 700, G, "start")
            + f'<rect x="{W - 88}" y="716" width="64" height="22" rx="4" fill="{B}" fill-opacity="{BAND_OPACITY}"/>'
            + t(W - 100, 734, "Money out", LABEL, 700, B, "end"))


def money_bands():
    return split_bands() + in_bands() + out_bands()


def rival_line():
    """Competitor A reaches customers through a channel we don't use: a dashed red line."""
    ax, ay, aw, _ = NODES["ca"]
    mx, my, mw, mh = NODES["mkt"]
    red = COLOURS["competitors"][1]
    return (f'<path d="M{ax + 30},{ay} C{ax + 30},{my + mh + 40} {mx + mw + 30},{my + mh / 2} {mx + mw},{my + mh / 2}"'
            f' fill="none" stroke="{red}" stroke-width="3.5" stroke-dasharray="10 7"/>')


# which competitor also works with a player on our map: a red letter badge on that player
BADGES = {"mkt": "A", "res": "B", "impl": "B", "host": "C", "ia": "C"}


def badges(only=None):
    red = COLOURS["competitors"][1]
    o = []
    for nid, letter in BADGES.items():
        if only is not None and nid not in only:
            continue
        x, y, w, _ = NODES[nid]
        o.append(f'<circle cx="{x + w - 4}" cy="{y + 4}" r="16" fill="{red}" stroke="white" stroke-width="3"/>'
                 + t(x + w - 4, y + 11.5, letter, LABEL, 700, "white"))
    return "".join(o)


def badge_legend():
    red = COLOURS["competitors"][1]
    return (f'<circle cx="{W / 2 - 172}" cy="{727}" r="15" fill="{red}"/>' + t(W / 2 - 172, 734.5, "B", LABEL, 700, "white")
            + t(W / 2 - 148, 734, "A competitor works with them too", LABEL, 700, red, "start"))


def full_map():
    return money_bands() + "".join(group_svg(k) for k in GROUPS) + company() + badges() + legend() + badge_legend()


def callout(x, y, title, lines, w=540):
    """lines: plain text lines, or (text, colour); a line starting with 'Ask:' (or indented) is set in bold blue."""
    h = 80 + 34 * len(lines)
    r = (f'<rect x="{x + 6}" y="{y + 8}" width="{w}" height="{h}" rx="16" fill="#000" opacity=".12"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="white" stroke="{B}" stroke-width="4"/>'
         + t(x + 30, y + 48, title, 32, 700, B, "start"))
    for i, ln in enumerate(lines):
        ln, colour = ln if isinstance(ln, tuple) else (ln, None)
        ask = ln.startswith("Ask:") or ln.startswith("  ")
        r += t(x + 30, y + 90 + i * 34, ln.strip(), 23, 700 if ask or colour else 500, colour or (B if ask else INK), "start")
    return r


DIM = f'<rect width="{W}" height="{H}" fill="white" opacity=".82"/>'
# callouts sit on dimmed canvas, never on the lit part
BR, BL = (806, 568), (96, 568)  # each covers whole dimmed boxes, never a sliver
CALLOUTS = {  # each says why the part is on the map, then the coach's question
    "customers": (BR, "Customers", ["Why: find where your revenue concentrates,", "including segments you don’t serve yet.", "Ask: what share comes from each?"]),
    "channels": (BR, "Channels", ["Why: find the gatekeepers, and the", "channels your competitors use.", "Ask: can these get you to your 3HAG?"]),
    "associations": (BL, "Associations", ["Why: they shape how buyers think", "before you ever meet them.", "Ask: whom can you leverage to grow?"]),
    "suppliers": (BL, "Suppliers", ["Why: find the dependency that could", "switch you off tomorrow.", "Ask: where does the most money go?"]),
    "partners": (BL, "Paid Partners", ["Why: see whom you rely on to reach", "or serve your customers.", "Ask: is any player in two places?"]),
    "competitors": ((10, 568), "Competitors", ["Why: overlap is a head-on fight.", "Gaps may be open space.", "Ask: could one block us anywhere?"]),
}
CALLOUT_W = {"competitors": 450}  # fits left of the lit competitors
LIT = {  # what each callout lights besides its own group: the money that belongs to it
    "customers": split_bands, "channels": lambda: split_bands() + in_bands(),
    "suppliers": lambda: out_bands({"dev", "host", "pay"}), "partners": lambda: out_bands({"impl"}),
    "associations": lambda: "", "competitors": lambda: badges() + badge_legend(),
}

(OUT / "market-map-example.svg").write_text(svg(W, H, full_map(), ARROW), encoding="utf-8")
for key, ((x, y), title, lines) in CALLOUTS.items():
    # rule 9: the exact example drawing, dimmed, with only this part lit and one callout
    # A lit player keeps its competitor badge at full strength (Byron, 16-Nov-2026).
    lit = {n[0] for n in GROUPS[key][3]} if key in GROUPS else set()
    top = badges() if key == "competitors" else badges(lit | ({"mkt"} if key == "channels" else set()))
    body = full_map() + DIM + LIT[key]() + group_svg(key, hi=True) + company() + top + callout(x, y, title, lines, CALLOUT_W.get(key, 540))
    (OUT / f"market-map-{key}.svg").write_text(svg(W, H, body, ARROW), encoding="utf-8")
money_body = (full_map() + DIM + money_bands() + "".join(group_svg(k) for k in ("customers", "channels", "suppliers", "partners"))
              + company() + legend() + badges({"res", "mkt", "host", "impl"})
              + callout(432, 568, "Money lines", ["Why: look for concentration, not precision.", "Rough shares are enough.", "Ask: where does cash come in?"], w=548))
(OUT / "market-map-money.svg").write_text(svg(W, H, money_body, ARROW), encoding="utf-8")

# circle what worries you (dashed red) and what excites you (green), then pull up to three into the QHAG
RED = COLOURS["competitors"][1]


def ring(nid, colour, dash):
    x, y, w, h = NODES[nid]
    d = ' stroke-dasharray="14 9"' if dash else ""
    return (f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2 + 10}" ry="{h / 2 + 7}" fill="none"'
            f' stroke="{colour}" stroke-width="5"{d}/>')


circles_body = (full_map() + DIM + group_svg("customers") + group_svg("channels") + group_svg("associations") + company() + badges({"res", "mkt", "ia"})
                + ring("small", RED, True) + ring("res", RED, True) + ring("schools", G, False) + ring("ia", G, False)
                + callout(432, 538, "Circle what matters", [("Worry: 55% of money from one segment.", RED),
                                                            ("Worry: Competitor B could block resellers.", RED),
                                                            ("Open space: a segment nobody serves yet.", G),
                                                            ("Opportunity: win C’s association first.", G)], w=548))
(OUT / "market-map-circles.svg").write_text(svg(W, H, circles_body, ARROW), encoding="utf-8")


# ---------------------------------------------------------------- team view
def team_view():
    W, H = 1440, 640
    o = []
    def card(x, y, func, owner, title, w=250, h=150, dashed=False, fill="white", stroke=B):
        d = ' stroke-dasharray="10 8"' if dashed else ""
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="3"{d}/>'
                + t(x + w / 2, y + 46, func, 26, 700, B if not dashed else GREY)
                + t(x + w / 2, y + 88, owner, 23, 600, INK if not dashed else GREY)
                + t(x + w / 2, y + 122, title, 19, 500, MUTE if not dashed else GREY))
    # Owners match the Kick Off Function Chart's agreed owners (Byron, 16-Nov-2026).
    two = {"Pat", "Jen"}  # each holds two functions: red (rule 13)
    o.append(card(570, 30, "Head of Company", "Pat", "CEO", w=300, fill=RFILL, stroke=R))
    xs = [30 + i * 233 for i in range(6)]
    funcs = [("Marketing", "Chris", "Marketing Manager"), ("Sales", "Andrew", "Sales Lead"), ("Operations", "Jen", "Operations Manager"),
             ("Development", "Jen", "Operations Manager"), ("Finance", "Allison", "Controller"), ("People", "Pat", "CEO")]
    o.append(f'<path d="M720,180 L720,230 M{xs[0] + 105},230 L{xs[-1] + 105},230" fill="none" stroke="{LINE}" stroke-width="3"/>')
    for x, (f, n, ti) in zip(xs, funcs):
        o.append(f'<line x1="{x + 105}" y1="230" x2="{x + 105}" y2="262" stroke="{LINE}" stroke-width="3"/>')
        o.append(card(x, 262, f, n, ti, w=210, fill=RFILL if n in two else "white", stroke=R if n in two else B))
    o.append(card(xs[1] - 35, 462, "Customer Success", "Planned", "Next year", w=280, dashed=True, stroke=GREY))
    o.append(f'<line x1="{xs[1] + 105}" y1="412" x2="{xs[1] + 105}" y2="462" stroke="{GREY}" stroke-width="3" stroke-dasharray="8 6"/>')
    o.append(t(600, 506, "Red: one person owns two functions.", 21, 600, R, "start"))
    o.append(t(600, 540, "Dashed: a planned function.", 21, 600, MUTE, "start"))
    return svg(W, H, "".join(o))


(OUT / "team-view-example.svg").write_text(team_view(), encoding="utf-8")


# ---------------------------------------------------------------- scorecard
def scorecard():
    W, H = 1440, 700
    o = [f'<rect x="20" y="20" width="1400" height="660" rx="18" fill="white" stroke="{LINE}" stroke-width="3"/>',
         f'<rect x="20" y="20" width="1400" height="96" rx="18" fill="{B}"/>', f'<rect x="20" y="90" width="1400" height="26" fill="{B}"/>',
         t(60, 82, "Operations scorecard", 36, 700, "white", "start"), t(1380, 82, "Owner: Jen", 26, 600, "white", "end")]
    def section(x, y, head, lines, w):
        r = t(x, y, head.upper(), 20, 700, MUTE, "start", ' letter-spacing="1.5"')
        for i, s in enumerate(lines):
            r += t(x, y + 40 + i * 36, s, 24, 500, INK, "start")
        return r
    o.append(section(60, 170, "Purpose", ["Turn every new subscription into an active customer, fast."], 1300))
    # Metronome's scorecard sections, in its order (metronome.help: How do I build an effective Scorecard?)
    o.append(section(60, 270, "Core Values", ["Your company’s core values, in this role."], 640))
    o.append(section(760, 490, "Metrics Owned by the Function", ["Activated subscriptions a week.", "Cost per activation."], 620))
    o.append(section(60, 380, "Functional Accountabilities", ["Owns activation of every new subscription.", "Owns onboarding quality.",
                                                               "Owns the hand-off to Finance.", "Owns execution of the Operations priorities."], 640))
    o.append(section(760, 270, "Key Competencies", ["Communicates clearly. Thinks in process.", "Focuses on the customer. Coaches the team.",
                                                     "Uses data. Follows through."], 620))
    return svg(W, H, "".join(o))


(OUT / "scorecard-example.svg").write_text(scorecard(), encoding="utf-8")
# ---------------------------------------------------------------- cash forecast
# The numbers come from the deck's own plan for the subscription company.
# QHAG: 2,100 leads, 840 marketing qualified, 210 new subscriptions, cash $1.0M at March.
# 1HAG: $6M revenue from about 2,000 collected payments a month, so about $250 a subscription a month;
# cash $1.5M at December. A month: 700 leads, 280 qualified (40%), 70 new subscriptions (25%).
# February closes 42, not 70 (15%). If that holds, 28 fewer subscriptions a month at $250,
# each paying from two months later: cash at December is 7,000 x (1 + ... + 9) = $315,000 lower.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# Jan to Mar come from the QHAG example's cash row.
APPROVED = [1100000, 1050000, 1000000] + [1000000 + round((m - 2) * 500000 / 9) for m in range(3, 12)]
LOST = [0, 0, 0] + [sum(7000 * (k - 2) for k in range(3, m + 1)) for m in range(3, 12)]
ROLLING = [a - l for a, l in zip(APPROVED, LOST)]
assert APPROVED[2] == 1000000 and APPROVED[11] == 1500000 and ROLLING[11] == APPROVED[11] - 315000


def cash_chart(gap_callout=False):
    W, H = 1440, 640
    O = "#a94f1f"
    L, R, T, Bm = 150, 1110, 60, 540
    lo, hi = 800000, 1600000
    X = lambda m: L + m * (R - L) / 11
    Y = lambda v: Bm - (v - lo) * (Bm - T) / (hi - lo)
    o = []
    for v in range(800000, 1600001, 100000):
        o.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{R}" y2="{Y(v):.1f}" stroke="{LINE}" stroke-width="1.5"/>')
        o.append(t(L - 16, Y(v) + 7, f"${v / 1e6:.1f}M", 19, 500, MUTE, "end"))
    for m, name in enumerate(MONTHS):
        o.append(t(X(m), Bm + 36, name, 20, 600 if m < 2 else 500, INK if m < 2 else MUTE))
    o.append(f'<rect x="{L}" y="{T}" width="{X(1.5) - L:.1f}" height="{Bm - T}" fill="{GFILL}" opacity=".6"/>')
    o.append(t(X(0.75), T + 28, "Closed", 19, 700, G))
    ap = " ".join(f"{X(m):.1f},{Y(v):.1f}" for m, v in enumerate(APPROVED))
    ro = " ".join(f"{X(m):.1f},{Y(v):.1f}" for m, v in enumerate(ROLLING))
    dim = ' opacity=".35"' if gap_callout else ""
    o.append(f'<polyline points="{ap}" fill="none" stroke="{B}" stroke-width="4" stroke-dasharray="12 9"{dim}/>')
    o.append(f'<polyline points="{ro}" fill="none" stroke="{O}" stroke-width="5"/>')
    act = " ".join(f"{X(m):.1f},{Y(APPROVED[m]):.1f}" for m in range(2))
    o.append(f'<polyline points="{act}" fill="none" stroke="{G}" stroke-width="7"/>')
    for m in range(2):
        o.append(f'<circle cx="{X(m):.1f}" cy="{Y(APPROVED[m]):.1f}" r="8" fill="{G}"/>')
    # legend
    lx = 1150
    for i, (c, lab, sub, dash) in enumerate([(G, "Actual", "what happened", ""), (B, "Approved", "the plan, locked", ' stroke-dasharray="12 9"'), (O, "Rolling", "Actual to date plus|forecasted Approved", "")]):
        yy = 120 + i * 100
        o.append(f'<line x1="{lx}" y1="{yy}" x2="{lx + 44}" y2="{yy}" stroke="{c}" stroke-width="5"{dash}/>')
        o.append(t(lx + 54, yy + 8, lab, 22, 700, c, "start")); [o.append(t(lx + 54, yy + 36 + k * 22, line, 17, 500, MUTE, "start")) for k, line in enumerate(sub.split("|"))]
    if gap_callout:
        x = X(11); ya, yr = Y(APPROVED[11]), Y(ROLLING[11])
        o.append(f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x:.1f}" y2="{yr:.1f}" stroke="{O}" stroke-width="3"/>')
        o.append(f'<rect x="{X(5.6):.1f}" y="{Y(1000000) - 30:.1f}" width="520" height="150" rx="14" fill="white" stroke="{O}" stroke-width="3"/>')
        bx, by = X(5.6) + 24, Y(1000000) + 10
        o.append(t(bx, by, "February: 42 new subscriptions, not 70.", 22, 700, O, "start"))
        o.append(t(bx, by + 36, "Close rate 15%, not 25%.", 21, 600, INK, "start"))
        o.append(t(bx, by + 72, "If it holds: $315,000 less cash by December.", 21, 600, INK, "start"))
        o.append(f'<circle cx="{X(1):.1f}" cy="{Y(APPROVED[1]):.1f}" r="18" fill="none" stroke="{O}" stroke-width="3"/>')
    return svg(W, H, "".join(o))


(OUT / "cash-rolling.svg").write_text(cash_chart(), encoding="utf-8")
(OUT / "cash-rolling-miss.svg").write_text(cash_chart(True), encoding="utf-8")

# ---------------------------------------------------------------- forecast examples
# Two QR codes that open the Example tab of each public forecast template (Byron, 16-Nov-2026).
# The 36-month caption says when it is built: 12 months at the first annual, 36 from the second
# (Byron, 25-Nov-2026).
import sys
sys.path.insert(0, str(ROOT / "tools"))
import qr_svg  # noqa: E402

EXAMPLES = [
    ("12-month forecast", "Build this one first.",
     "https://docs.google.com/spreadsheets/d/1Gopb6QtY_HixT8lOjo7Tu4HZ-2Yy2M02jxbSptdoSJM/edit#gid=1174451209"),
    ("36-month forecast", "The 3-year view, from the second annual.",
     "https://docs.google.com/spreadsheets/d/1qhzbTYzfBUSeTjJf08UJ4kRKDljA65IgIOSnc82OGV4/edit#gid=861046588"),
]


def qr_block(x, y, size, url):
    m = qr_svg.encode(url)
    n = len(m) + 8
    cell = size / n
    d = "".join(f"M{x + (c + 4) * cell:.2f},{y + (r + 4) * cell:.2f}h{cell:.2f}v{cell:.2f}h-{cell:.2f}z"
                for r, row in enumerate(m) for c, on in enumerate(row) if on)
    return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="white"/><path d="{d}" fill="{INK}"/>'


def forecast_examples():
    W, H, size = 1440, 640, 380
    o = []
    for i, (title, sub, url) in enumerate(EXAMPLES):
        cx = 380 + i * 680
        o.append(f'<rect x="{cx - 250}" y="20" width="500" height="600" rx="8" fill="white" stroke="{LINE}" stroke-width="3"/>')
        o.append(f'<rect x="{cx - 250}" y="20" width="500" height="8" fill="{G if i == 0 else B}"/>')
        o.append(t(cx, 92, title, 34, 700, INK))
        o.append(t(cx, 134, sub, 24, 500, MUTE))
        o.append(qr_block(cx - size / 2, 160, size, url))
        o.append(t(cx, 590, "Opens the Example tab", 22, 600, G if i == 0 else B))
    return svg(W, H, "".join(o))


(OUT / "cash-forecast-examples.svg").write_text(forecast_examples(), encoding="utf-8")
print("wrote", len(list(OUT.glob("*.svg"))), "SVGs to", OUT)

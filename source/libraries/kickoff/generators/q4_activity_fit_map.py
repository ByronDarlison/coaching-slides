#!/usr/bin/env python3
"""Draw the example Activity Fit Map, and how a team builds it, in the look of the map on the strategy site
(darlison/strategy/build_activity_fit_map.py): the differentiators as coloured circles in a diamond, their
activities as small gray circles on the outer side, thin gray lines between two that depend on each other, with
the reason on the line.

The team builds it from the activities up, so the pictures follow the steps:
  write  the activities, loose
  group  the same notes in named groups
  keep   the 3 to 5 groups the team keeps, in colour; the group not kept fades
  map    the lines drawn: the finished map
The three side pictures carry names only (slide standard rule 32). The finished map carries every label.
The example has 18 activities, because each leader writes 5 to 7 and a real board is full (Byron, 26-Nov-2026).
The telling of the strategy sits in the middle of the finished map only: it comes after the lines.
Run from the library folder: python3 generators/q4_activity_fit_map.py"""
import math
from q4_common import svg, write, text, block, CORNER

NODE_FILL, NODE_STROKE, NODE_TEXT = "#F4F6F8", "#8997A5", "#263746"
LINK, REASON, TEST = "#8A8A8A", "#4D5560", "#326AB6"
PLAIN = ("#FFFFFF", "#8997A5", "#263746")  # a named group the team has not yet kept
# place -> name, (fill, stroke, ink) from the strategy site, activities (line breaks set by hand)
GROUPS = {
    "L": (["A Named", "Person for", "90 Days"], ("#E9F0FA", "#326AB6", "#1F3F6E"),
          [["A handover", "at day 90"], ["A 30-day", "check-in"], ["A single", "contact"], ["A call in", "week one"],
           ["Answers", "in one", "day"]]),
    "T": (["Live in", "a Day"], ("#E4F3F0", "#167568", "#10594F"),
          [["Import", "from a", "sheet"], ["Guided", "setup"], ["Ready-made", "templates"], ["Nothing", "to install"]]),
    "R": (["Standard,", "Not Custom"], ("#F0EAF8", "#7952A3", "#563475"),
          [["Fewer", "settings"], ["One", "product", "for all"], ["No custom", "work"], ["A short,", "fixed", "report set"],
           ["Say no to", "one-offs"]]),
    "B": (["One Flat", "Price"], ("#FBF1DB", "#A57516", "#6D4B08"),
          [["No setup", "fee"], ["One plan"], ["No add-ons"], ["Price on", "the site"]]),
}
# Why one depends on the other. The words sit on the line (Darlison practice).
LINKS = [("L", "T", ["a fast start leaves", "time for the customer"]),
         ("T", "R", ["one product", "makes setup fast"]),
         ("R", "B", ["no custom work", "keeps one price"])]
# A group the team names and then does not keep: a task, not a differentiator.
SPARE = ["New", "Billing", "System"]

SIDE = dict(w=900, h=690, hubs={"L": (160, 345), "T": (450, 104), "R": (740, 345), "B": (450, 586)}, hub_r=88,
            centre=(450, 345), centre_r=86, note_r=26, ring=124, name=24,
            # Which way each group's activities fan out, in degrees (0 is right, 90 is down).
            fan={"L": [124, 152, 180, 208, 236], "R": [56, 28, 0, -28, -56], "T": [205, 170, 10, -25], "B": [155, 190, -10, 25]},
            spare=((786, 574), 64, [175, 215, 255], 100),
            loose=[(80 + c * 123 + dx, 130 + r * 205 + dy) for r, row in enumerate(
                [[(0, 20), (10, -40), (-8, 30), (12, -10), (-6, 44), (8, -30), (-4, 16)],
                 [(14, -6), (-10, 36), (6, -34), (-12, 10), (10, 40), (-6, -20), (4, 30)],
                 [(-4, 22), (12, -24), (-10, 34), (8, -8), (-8, 26), (12, -36), (-2, 12)]]) for c, (dx, dy) in enumerate(row)])
FULL = dict(w=1440, h=610, hubs={"L": (350, 305), "T": (720, 92), "R": (1090, 305), "B": (720, 518)}, hub_r=78,
            centre=(720, 305), centre_r=92, note_r=54, ring=230, name=23, note=17.5, reason=18,
            fan={"L": [115, 147.5, 180, 212.5, 245], "R": [65, 32.5, 0, -32.5, -65]},
            # The top and bottom groups set their activities in a row beside them.
            spots={"T": [(445, 92), (570, 92), (870, 92), (995, 92)], "B": [(445, 518), (570, 518), (870, 518), (995, 518)]})
assert len(SIDE["loose"]) == sum(len(g[2]) for g in GROUPS.values()) + len(SIDE["spare"][2])


def at(centre, ring, degrees):
    a = math.radians(degrees)
    return centre[0] + ring * math.cos(a), centre[1] + ring * math.sin(a)


def circle(c, r, fill, stroke, width, extra=""):
    return f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width:g}"{extra}/>'


def line(a, b, stroke, width, extra=""):
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{width:g}"{extra}/>'


def strokes(c, wide, colour, width):
    """Two short strokes stand for words where the picture is too small to carry them."""
    return "".join(line((c[0] - w / 2, c[1] + dy), (c[0] + w / 2, c[1] + dy), colour, width, ' stroke-linecap="round"')
                   for w, dy in ((wide, -width * 2.1), (wide * 0.6, width * 2.1)))


def note(p, r, bold, written):
    """A sticky note."""
    return circle(p, r, NODE_FILL, NODE_STROKE, 1.8 * bold) + (strokes(p, r * 0.95, NODE_STROKE, 2.4) if written else "")


def draw(g, stage, names=True, bold=1.0):
    """One picture. bold thickens the strokes for a picture that is shown small."""
    o, nr = [], g["note_r"]
    labelled = "note" in g
    small = not names  # the strip: no words fit, so marks stand for them
    if stage == "write":
        if small:
            return "".join(circle(p, g["note_r"], NODE_FILL, "#5b6670", 1.8 * bold) for p in g["loose"])
        return "".join(note(p, nr, bold, names) for p in g["loose"])
    if stage == "map":
        for a, b, _ in LINKS:
            o.append(line(g["hubs"][a], g["hubs"][b], "#263746" if small else LINK, 12 if small else 2.6 * bold))
    for key, (name, colours, notes) in GROUPS.items():
        hub = g["hubs"][key]
        spots = g.get("spots", {}).get(key) or [at(hub, g["ring"], d) for d in g["fan"][key]]
        assert len(spots) == len(notes), key
        o += [line(hub, p, NODE_STROKE, 1.5 * bold, ' stroke-opacity="0.7"') for p in spots]
        for p, words in zip(spots, notes):
            o.append(note(p, nr, bold, names and not labelled))
            if labelled:
                o.append(block(p[0], p[1], words, g["note"], 21, weight=500, fill=NODE_TEXT))
        fill, stroke, ink = PLAIN if stage == "group" else colours
        if small and stage != "group":
            o.append(circle(hub, g["hub_r"], "#FFFFFF", stroke, 3 * bold))
            o.append(circle(hub, g["hub_r"], stroke, stroke, 3 * bold, ' fill-opacity="0.35"'))
        else:
            o.append(circle(hub, g["hub_r"], fill, stroke, 3 * bold))
        if small:
            o.append(strokes(hub, g["hub_r"] * 0.9, stroke, 9))
        if names:
            o.append(block(hub[0], hub[1], name, g["name"], round(g["name"] * 1.2), weight=700, fill=ink))
    if "spare" in g and stage in ("group", "keep"):
        c, r, fan, ring = g["spare"]
        kept = stage == "group"
        body = "".join(line(c, at(c, ring, d), NODE_STROKE, 1.5 * bold, ' stroke-opacity="0.7"') for d in fan)
        body += "".join(note(at(c, ring, d), nr, bold, names) for d in fan)
        body += circle(c, r, "#FFFFFF", NODE_STROKE, 3 * bold, "" if kept else ' stroke-dasharray="7 6"')
        if small:
            body += strokes(c, r * 0.9, NODE_STROKE, 9)
        if names:
            body += block(c[0], c[1], SPARE, g["name"] - 2, round(g["name"] * 1.1), weight=700, fill=NODE_TEXT)
        if small and not kept:
            body += line((c[0] - r * 1.25, c[1] + r * 1.25), (c[0] + r * 1.25, c[1] - r * 1.25), "#8A8A8A", 8, ' stroke-linecap="round"')
        o.append(body if kept else f'<g opacity="{0.7 if small else 0.42}">{body}</g>')
        if names and not kept:
            o.append(text(c[0], c[1] + r + 34, "Not kept", g["name"], 600, REASON, "middle"))
    # In the middle of the finished map: tell the strategy with the names and the lines (Byron, 26-Nov-2026: the
    # telling comes after the lines are drawn; at the naming step the team only checks that each name is specific).
    c, r = g["centre"], g["centre_r"]
    if names and stage == "map":
        o.append(circle(c, r, "#FFFFFF", TEST, 2.5 * bold, f' stroke-dasharray="{7 * bold:g} {5 * bold:g}"'))
        o.append(block(c[0], c[1], ["Test: tell", "the strategy", "with the names", "and the lines"], g["name"] - 3, 25, weight=600, fill="#1F3F6E"))
    if stage == "map" and "reason" in g:
        for a, b, why in LINKS:
            (x1, y1), (x2, y2) = g["hubs"][a], g["hubs"][b]
            o.append(block((x1 + x2) / 2, (y1 + y2) / 2, why, g["reason"], 22, weight=500, fill=REASON,
                           extra=' stroke="#fff" stroke-width="7" paint-order="stroke" stroke-linejoin="round"'))
    return "".join(o)


def example(x=40, y=50):
    return text(x, y, "Example", 26, 700, CORNER, "start", ' letter-spacing="2"')


# The three steps before the lines, for the side of the slide that asks for each one.
for stage in ("write", "group", "keep"):
    write(f"q4-activity-fit-map-{stage}.svg", svg(SIDE["w"], SIDE["h"], example() + draw(SIDE, stage)))

# The finished map: every activity labelled, and the reason on every line.
# Under it, what the finished lines tell the team: is this one strategy, or a list?
READ = [("All joined", "One strategy. Hard to copy."),
        ("One left alone", "It sets you apart, or it is a task."),
        ("None joined", "A list of capabilities.")]
key = [text(40, 654, "WHAT THE LINES", 19, 700, CORNER, "start", ' letter-spacing="1.5"'),
       text(40, 680, "TELL YOU", 19, 700, CORNER, "start", ' letter-spacing="1.5"')]
for k, (head, sub) in enumerate(READ):
    kx = 286 + k * 376
    key.append(f'<rect x="{kx}" y="626" width="360" height="66" rx="12" fill="#FBFAF7" stroke="#D5D9DD" stroke-width="1.5"/>')
    key.append(text(kx + 18, 653, head, 22, 700, "#20282f", "start"))
    key.append(text(kx + 18, 680, sub, 20, 500, "#4D5560", "start"))
write("q4-activity-fit-map-example.svg", svg(FULL["w"], 706, example(40, 46) + draw(FULL, "map") + "".join(key)))

# How you build it: the four steps side by side, with the step under each. The strip stretches the side picture
# upward so each small picture fills its card.
STRETCH = 1.5
def tall(p): return (p[0], (p[1] - 345) * STRETCH + 345 * STRETCH)
(sc, sr, sfan, sring) = SIDE["spare"]
# Bigger notes and hubs than the side pictures, so they read at card size; the side hubs move in to make room.
STRIP = dict(SIDE, h=690 * STRETCH, note_r=34, hub_r=100, ring=150,
             hubs={k: tall((x + {"L": 34, "R": -34}.get(k, 0), y)) for k, (x, y) in SIDE["hubs"].items()},
             centre=tall(SIDE["centre"]), spare=(tall(sc), sr, sfan, 104), loose=[tall(p) for p in SIDE["loose"]])
STEPS = [("write", "1. Write the activities.", ["Everything you must do to", "create your white space."]),
         ("group", "2. Group them. Name each group.", ["The name sums up", "what the group does."]),
         ("keep", "3. Keep 3 to 5 groups.", ["These are your", "differentiators."]),
         ("map", "4. Draw the lines.", ["They depend on each other.", "They become your swim lanes."])]
W, SCALE, CARD, GAP, TOP = 1440, 0.355, 328, 26, 30
left = (W - 4 * CARD - 3 * GAP) / 2
strip = []
pw, ph = STRIP["w"] * SCALE, STRIP["h"] * SCALE
for k, (stage, head, sub) in enumerate(STEPS):
    x = left + k * (CARD + GAP)
    strip.append(f'<rect x="{x:.1f}" y="{TOP}" width="{CARD}" height="{ph + 28:.1f}" rx="14" fill="#FBFAF7" stroke="#D5D9DD" stroke-width="1.5"/>')
    strip.append(f'<g transform="translate({x + (CARD - pw) / 2:.1f} {TOP + 14}) scale({SCALE})">{draw(STRIP, stage, names=False, bold=2.2)}</g>')
    if k:
        ax, ay = x - GAP / 2, TOP + 14 + ph / 2
        strip.append(f'<path d="M{ax - 7:.1f} {ay - 11:.1f} L{ax + 7:.1f} {ay:.1f} L{ax - 7:.1f} {ay + 11:.1f}" fill="none" stroke="{CORNER}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    ty = TOP + ph + 28 + 48
    strip.append(text(x + CARD / 2, ty, head, 24, 700, "#20282f"))
    strip += [text(x + CARD / 2, ty + 38 + n * 30, s, 22, 500, "#5b6670") for n, s in enumerate(sub)]
write("q4-activity-fit-map-steps.svg", svg(W, round(TOP + ph + 28 + 48 + 38 + 30 + 26), "".join(strip)))
print("wrote q4-activity-fit-map-{write,group,keep,example,steps}.svg")

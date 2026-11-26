#!/usr/bin/env python3
"""Draw the example Activity Fit Map, and how a team builds it, in the look of the map on the strategy site
(darlison/strategy/build_activity_fit_map.py): the differentiators as coloured circles in a diamond around the
names test, their activities as small gray circles on the outer side, thin gray lines between two that depend
on each other, with the reason on the line.

The team builds it from the activities up, so the pictures follow the steps:
  write  the activities, loose
  group  the same notes in named groups, with the names test in the middle
  keep   the 3 to 5 groups the team keeps, in colour; the group not kept fades
  map    the lines drawn: the finished map
The three side pictures carry names only (slide standard rule 32). The finished map carries every label.
Run from the library folder: python3 generators/q4_activity_fit_map.py"""
import math
from q4_common import svg, write, text, block, CORNER

NODE_FILL, NODE_STROKE, NODE_TEXT = "#F4F6F8", "#8997A5", "#263746"
LINK, REASON, TEST = "#8A8A8A", "#4D5560", "#326AB6"
PLAIN = ("#FFFFFF", "#8997A5", "#263746")  # a named group the team has not yet kept
# place -> name, (fill, stroke, ink) from the strategy site, activities (line breaks set by hand)
GROUPS = {
    "L": (["A Named", "Person for", "90 Days"], ("#E9F0FA", "#326AB6", "#1F3F6E"),
          [["A single", "contact"], ["A call in", "week one"], ["Answers", "in one", "day"]]),
    "T": (["Live in", "a Day"], ("#E4F3F0", "#167568", "#10594F"),
          [["Guided", "setup"], ["Ready-made", "templates"]]),
    "R": (["Standard,", "Not Custom"], ("#F0EAF8", "#7952A3", "#563475"),
          [["One", "product", "for all"], ["No custom", "work"], ["A short,", "fixed", "report set"]]),
    "B": (["One Flat", "Price"], ("#FBF1DB", "#A57516", "#6D4B08"),
          [["One plan"], ["No add-ons"]]),
}
# Why one depends on the other. The words sit on the line.
LINKS = [("L", "T", ["a fast start leaves", "time for the customer"]),
         ("T", "R", ["one product", "makes setup fast"]),
         ("R", "B", ["no custom work", "keeps one price"])]
# A group the team names and then does not keep: a task, not a differentiator.
SPARE = ["New", "Billing", "System"]
# Which way each group's activities fan out, in degrees (0 is right, 90 is down).
FAN = {"L": [225, 180, 135], "R": [-45, 0, 45]}

SIDE = dict(w=900, h=690, hubs={"L": (160, 345), "T": (450, 104), "R": (740, 345), "B": (450, 586)}, hub_r=88,
            centre=(450, 345), centre_r=86, note_r=26, ring=124, fan={**FAN, "T": [200, -20], "B": [160, 20]},
            name=24, spare=((786, 574), 64, [200, 255], 100),
            loose=[(96, 150), (268, 92), (452, 168), (640, 96), (806, 170), (190, 318), (392, 372), (590, 300),
                   (776, 398), (120, 520), (330, 580), (560, 500), (720, 600)][:12])
FULL = dict(w=1440, h=610, hubs={"L": (350, 305), "T": (720, 92), "R": (1090, 305), "B": (720, 518)}, hub_r=78,
            centre=(720, 305), centre_r=92, note_r=62, ring=207, fan={**FAN, "T": [187, -7], "B": [173, 7]},
            rings={"T": 177, "B": 177}, name=23, note=17.5, reason=18)


def at(centre, ring, degrees):
    a = math.radians(degrees)
    return centre[0] + ring * math.cos(a), centre[1] + ring * math.sin(a)


def circle(c, r, fill, stroke, width, extra=""):
    return f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width:g}"{extra}/>'


def line(a, b, stroke, width, extra=""):
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{width:g}"{extra}/>'


def note(p, r, bold, written):
    """A sticky note. Two short strokes stand for the words where the picture is too small to carry them."""
    words = "".join(line((p[0] - w / 2, p[1] + dy), (p[0] + w / 2, p[1] + dy), NODE_STROKE, 2.4, ' stroke-linecap="round"')
                    for w, dy in ((r * 0.95, -5), (r * 0.6, 5))) if written else ""
    return circle(p, r, NODE_FILL, NODE_STROKE, 1.8 * bold) + words


def draw(g, stage, names=True, bold=1.0):
    """One picture. bold thickens the strokes for a picture that is shown small."""
    o, nr = [], g["note_r"]
    labelled = "note" in g
    small = not names  # the strip: no words fit, so marks stand for them
    if stage == "write":
        if small:
            return "".join(circle(p, 34, NODE_FILL, "#5b6670", 1.8 * bold) for p in g["loose"])
        return "".join(note(p, nr, bold, names) for p in g["loose"])
    if stage == "map":
        for a, b, _ in LINKS:
            o.append(line(g["hubs"][a], g["hubs"][b], "#263746" if small else LINK, 12 if small else 2.6 * bold))
    for key, (name, colours, notes) in GROUPS.items():
        hub = g["hubs"][key]
        ring = g.get("rings", {}).get(key, g["ring"])
        spots = [at(hub, ring, d) for d in g["fan"][key]]
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
            o += [line((hub[0] - w / 2, hub[1] + dy), (hub[0] + w / 2, hub[1] + dy), stroke, 9, ' stroke-linecap="round"')
                  for w, dy in ((g["hub_r"] * 0.9, -11), (g["hub_r"] * 0.5, 11))]
        if names:
            o.append(block(hub[0], hub[1], name, g["name"], round(g["name"] * 1.2), weight=700, fill=ink))
    if "spare" in g and stage in ("group", "keep"):
        c, r, fan, ring = g["spare"]
        kept = stage == "group"
        body = "".join(line(c, at(c, ring, d), NODE_STROKE, 1.5 * bold, ' stroke-opacity="0.7"') for d in fan)
        body += "".join(note(at(c, ring, d), nr, bold, names) for d in fan)
        body += circle(c, r, "#FFFFFF", NODE_STROKE, 3 * bold, "" if kept else ' stroke-dasharray="7 6"')
        if small:
            body += "".join(line((c[0] - w / 2, c[1] + dy), (c[0] + w / 2, c[1] + dy), NODE_STROKE, 9, ' stroke-linecap="round"')
                            for w, dy in ((r * 0.9, -11), (r * 0.5, 11)))
        if names:
            body += block(c[0], c[1], SPARE, g["name"] - 2, round(g["name"] * 1.1), weight=700, fill=NODE_TEXT)
        if small and not kept:
            body += line((c[0] - r * 1.25, c[1] + r * 1.25), (c[0] + r * 1.25, c[1] - r * 1.25), "#8A8A8A", 8, ' stroke-linecap="round"')
        o.append(body if kept else f'<g opacity="{0.7 if small else 0.42}">{body}</g>')
        if names and not kept:
            o.append(text(c[0], c[1] + r + 34, "Not kept", g["name"], 600, REASON, "middle"))
    # Shannon's test, in the middle: tell the strategy using only the names.
    c, r = g["centre"], g["centre_r"]
    if names:
        o.append(circle(c, r, "#FFFFFF", TEST, 2.5 * bold, f' stroke-dasharray="{7 * bold:g} {5 * bold:g}"'))
    if names:
        o.append(block(c[0], c[1], ["Tell the", "strategy", "using only", "the names"], g["name"] - 2, 25, weight=600, fill="#1F3F6E"))
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
key = [text(40, 668, "READ THE LINES", 21, 700, CORNER, "start", ' letter-spacing="1.5"')]
for k, (head, sub) in enumerate(READ):
    kx = 286 + k * 376
    key.append(f'<rect x="{kx}" y="626" width="360" height="66" rx="12" fill="#FBFAF7" stroke="#D5D9DD" stroke-width="1.5"/>')
    key.append(text(kx + 18, 653, head, 22, 700, "#20282f", "start"))
    key.append(text(kx + 18, 680, sub, 20, 500, "#4D5560", "start"))
write("q4-activity-fit-map-example.svg", svg(FULL["w"], 706, example(40, 46) + draw(FULL, "map") + "".join(key)))

# How you build it: the four steps side by side, small, with the step under each.
STEPS = [("write", "1. Write the activities.", ["One on each note."]),
         ("group", "2. Group them. Name each group.", ["The name sums up", "what the group does."]),
         ("keep", "3. Keep 3 to 5 groups.", ["These are your", "differentiators."]),
         ("map", "4. Draw the lines.", ["Show how they depend", "on each other."])]
W, H, SCALE, CARD, GAP, TOP = 1440, 600, 0.355, 328, 26, 92
left = (W - 4 * CARD - 3 * GAP) / 2
strip = []
for k, (stage, head, sub) in enumerate(STEPS):
    x = left + k * (CARD + GAP)
    pw, ph = SIDE["w"] * SCALE, SIDE["h"] * SCALE
    strip.append(f'<rect x="{x:.1f}" y="{TOP}" width="{CARD}" height="{ph + 28:.1f}" rx="14" fill="#FBFAF7" stroke="#D5D9DD" stroke-width="1.5"/>')
    strip.append(f'<g transform="translate({x + (CARD - pw) / 2:.1f} {TOP + 14}) scale({SCALE})">{draw(SIDE, stage, names=False, bold=2.2)}</g>')
    if k:
        ax, ay = x - GAP / 2, TOP + 14 + ph / 2
        strip.append(f'<path d="M{ax - 7:.1f} {ay - 11:.1f} L{ax + 7:.1f} {ay:.1f} L{ax - 7:.1f} {ay + 11:.1f}" fill="none" stroke="{CORNER}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>')
    ty = TOP + ph + 28 + 48
    strip.append(text(x + CARD / 2, ty, head, 24, 700, "#20282f"))
    strip += [text(x + CARD / 2, ty + 38 + n * 30, s, 22, 500, "#5b6670") for n, s in enumerate(sub)]
# The end: where the differentiators go.
def band(y, tag, words):
    """The start and the end of the four steps: a bar with a tag at its left."""
    return (f'<rect x="{left:.1f}" y="{y}" width="{W - 2 * left:.1f}" height="54" rx="14" fill="#EEF4FB" stroke="#326AB6" stroke-width="2"/>'
            f'<rect x="{left + 12:.1f}" y="{y + 10}" width="96" height="34" rx="17" fill="#1F3F6E"/>'
            + text(left + 60, y + 34, tag, 19, 700, "#FFFFFF", "middle", ' letter-spacing="1.5"')
            + text(left + 128, y + 36, words, 24, 600, "#1F3F6E", "start"))
def down(x, y):
    return f'<path d="M{x - 11:.1f} {y:.1f} L{x:.1f} {y + 12:.1f} L{x + 11:.1f} {y:.1f}" fill="none" stroke="{CORNER}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
strip.append(band(14, "START", "Your white space, as agreed on your Attribution Map."))
strip.append(down(left + CARD / 2, 72))
strip.append(down(left + 3 * (CARD + GAP) + CARD / 2, 500))
strip.append(band(522, "END", "Your differentiators become your swim lanes: what you must get done, quarter by quarter, for three years."))
write("q4-activity-fit-map-steps.svg", svg(W, H, "".join(strip)))
print("wrote q4-activity-fit-map-{write,group,keep,example,steps}.svg")

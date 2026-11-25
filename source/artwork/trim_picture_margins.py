"""Trim the empty white margin around a library illustration.

The illustrations were made on a 16:9 white page with the figures in the middle, so a picture
shown beside the copy sat small inside its panel (25-Nov-2026). This crops each named picture to
its drawing plus a 6% margin. It never crops into the drawing and keeps the shape between
1:1 and 1.9:1. Needs Pillow. Run once per new picture:

    /usr/bin/python3 source/artwork/trim_picture_margins.py libraries/kickoff/assets/<file> ...
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]


def trim(path: Path) -> str:
    im = Image.open(path)
    rgb = im.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, (255, 255, 255))).convert("L").point(lambda p: 255 if p > 24 else 0)
    box = diff.getbbox()
    if not box:
        return f"{path.name}: blank, left alone"
    W, H = rgb.size
    l, t, r, b = box
    m = round(0.06 * max(r - l, b - t))
    l, t, r, b = l - m, t - m, r + m, b + m
    w, h = r - l, b - t
    if w / h < 1.0:      # a tall drawing: widen the crop to a square
        add = (h - w) / 2; l -= add; r += add
    elif w / h > 1.9:    # a very wide drawing: add height
        add = (w / 1.9 - h) / 2; t -= add; b += add
    l, t, r, b = max(0, round(l)), max(0, round(t)), min(W, round(r)), min(H, round(b))
    if (r - l) * (b - t) > 0.85 * W * H:
        return f"{path.name}: already tight, left alone"
    out = im.crop((l, t, r, b))
    if path.suffix.lower() in (".jpg", ".jpeg"):
        out.convert("RGB").save(path, quality=93, subsampling=0)
    else:
        out.save(path)
    return f"{path.name}: {W}x{H} -> {r - l}x{b - t}"


for name in sys.argv[1:]:
    print(trim((ROOT / name).resolve()))

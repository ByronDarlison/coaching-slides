#!/usr/bin/env python3
"""Compile reusable slide libraries and ordered playlists onto the house shell.

CLI is the real tool. The Coach compile-deck skill is the agent front door.

Units and playlists live beside this tool under source/. Compiled output is local and
ephemeral. Publish copies the built deck into ByronDarlison/coaching-slides
for GitHub Pages. Do not invent secrets. Do not call a broker from this tool.
"""

from __future__ import annotations

import argparse
import html
import json
import hashlib
import itertools
import math
import re
import struct
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

TOOLS = Path(__file__).resolve().parent
PRESENTATIONS = TOOLS.parent
SHARED_DECK = PRESENTATIONS / "shared" / "deck"
CHECK_SHELL = PRESENTATIONS / "shared" / "check-shell.py"
METRONOMICS = PRESENTATIONS / "metronomics"
LIBRARY = METRONOMICS / "library"
PLAYLISTS = METRONOMICS / "playlists"
COMPILED = METRONOMICS / "compiled"

PUBLIC_PAGES_ROOT = "https://byrondarlison.github.io/coaching-slides"
COACHING_SLIDES_REL = "metronomics"
NUMBERED_ROLE = re.compile(r"(\d+)(?:\s*\u00b7\s*(.+))?", re.S)
LAYOUTS = {"title", "comp-story", "comp-causal", "comp-decision", "comp-rule", "about-timeline", "comp-attempts", "comp-figure"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
TIMELINE_KINDS = {"photo", "logo", "illustration"}
SVG_FORBIDDEN = re.compile(r"<\s*(script|foreignObject|iframe|object|embed|image|use|style)\b|\son[a-z]+\s*=|href\s*=|url\s*\(|javascript:|<!", re.I)
SHELL_FILES = ("shell.css", "shell.js")
FONT_NAMES = (
    "geist-latin.woff2",
    "geist-mono-latin.woff2",
    "LICENSE.txt",
    "README.md",
)


class CompileError(ValueError):
    """Fail closed on a missing unit, playlist, or invalid field."""


# Text a layout cannot show. A warning for now, because two published slides still carry
# such text; --fail-on-dropped-text turns each one into a build failure.
WARNINGS: list[str] = []


def dropped_text(unit: dict[str, Any], message: str) -> None:
    where = unit.get("_name") or unit.get("_source") or unit.get("id") or "slide"
    if unit.get("_fail_on_dropped_text") is True:
        raise CompileError(f"{where}: {message}")
    WARNINGS.append(f"{where}: {message}")


def number(value: Any) -> bool:
    """A real, finite number of a sane size. JSON true and false are not numbers here."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if isinstance(value, float) and not math.isfinite(value):
        return False
    return -1e9 <= value <= 1e9


# The only network address a compiled deck may carry: a link a person chooses to click.
# The pattern admits only what link_tag writes, so no other text can hide an address inside it.
DECK_LINK = re.compile(r'<a class="deck-link(?: [a-z-]+)*" href="https://[^"\s<>()\\]*" target="_blank" rel="noopener"')
LINK_HOST = re.compile(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+")


def safe_link(value: Any) -> str:
    """Return an https address fit to print in an href, or fail closed."""
    if not isinstance(value, str) or not value.startswith("https://") or not value.isascii():
        raise CompileError("a link needs an https address")
    # One spelling of an address everywhere (href, text, frozen copy): nothing is re-encoded on the way out.
    if re.search(r"[\s\"'<>()\\`{}|^\x00-\x1f\x7f]", value):
        raise CompileError(f"a link address cannot contain spaces, quotes or brackets; write ( and ) as %28 and %29: {value!r}")
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise CompileError(f"not a valid link address: {value!r}") from exc
    host = parts.hostname or ""
    if "@" in parts.netloc or port is not None or not LINK_HOST.fullmatch(host):
        raise CompileError(f"a link needs a plain https host name, with no sign-in part or port: {value!r}")
    return value


MISSING = object()  # a field that was not written, as distinct from one written as null


def link_label(value: Any, href: str) -> str:
    if not isinstance(value, str) and value is not MISSING:
        raise CompileError("a link label is a line of text")
    label = (visible_text(value) if value is not MISSING else "") or display_url(href)
    if "://" in label:
        raise CompileError("a link label shows the address without https://")
    return label


def link_tag(href: str, extra: str = "") -> str:
    """The opening tag of every link the compiler writes. DECK_LINK must match it.

    Every address is checked here as well as where it is read, so no caller can skip the check.
    """
    css = f"deck-link {extra}".strip()
    return f'<a class="{css}" href="{escape(safe_link(href))}" target="_blank" rel="noopener"'


def repo_root() -> Path:
    return PRESENTATIONS.parent.parent


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CompileError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CompileError(f"invalid JSON in {path}: {exc}") from exc


def unit_path(unit_id: str) -> Path:
    if "/" in unit_id or "\\" in unit_id or unit_id in {".", ".."}:
        raise CompileError(f"invalid unit id: {unit_id}")
    return LIBRARY / f"{unit_id}.json"


def load_unit(unit_id: str) -> dict[str, Any]:
    data = load_json(unit_path(unit_id))
    if not isinstance(data, dict):
        raise CompileError(f"unit {unit_id} must be an object")
    if data.get("id") != unit_id:
        raise CompileError(f"unit file {unit_id}.json id must be {unit_id!r}")
    required = ("title", "tags", "layout", "headline")
    missing = [key for key in required if key not in data]
    if missing:
        raise CompileError(f"unit {unit_id} missing fields: {', '.join(missing)}")
    layout = data["layout"]
    if layout not in LAYOUTS:
        raise CompileError(f"unit {unit_id} has unknown layout {layout!r}")
    tags = data.get("tags")
    if not isinstance(tags, list) or not all(isinstance(tag, str) and tag for tag in tags):
        raise CompileError(f"unit {unit_id} tags must be a list of strings")
    return data


def load_playlist(playlist_id: str) -> dict[str, Any]:
    if "/" in playlist_id or "\\" in playlist_id or playlist_id in {".", ".."}:
        raise CompileError(f"invalid playlist id: {playlist_id}")
    data = load_json(PLAYLISTS / f"{playlist_id}.json")
    if not isinstance(data, dict):
        raise CompileError(f"playlist {playlist_id} must be an object")
    if data.get("id") != playlist_id:
        raise CompileError(f"playlist file id must be {playlist_id!r}")
    units = data.get("units")
    if not isinstance(units, list) or not units:
        raise CompileError(f"playlist {playlist_id} needs a non-empty units list")
    return data


def identifier(value: Any, label: str = "id") -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", value):
        raise CompileError(f"invalid {label}: {value!r}")
    return value


def resolve_playlist(playlist: dict[str, Any], library: Path | None = None) -> list[dict[str, Any]]:
    """Resolve ordered references without changing their reusable source files."""
    roots = {"metronomics": library or LIBRARY}
    base = Path(playlist.get("_base", PRESENTATIONS))
    sources = playlist.get("sources", {})
    if not isinstance(sources, dict):
        raise CompileError("sources must map library names to local directories")
    for name, location in sources.items():
        identifier(name, "library")
        if not isinstance(location, str) or not location:
            raise CompileError("source location must be a local directory")
        roots[name] = (base / location).resolve()
    resolved = []
    entries = playlist.get("units")
    if not isinstance(entries, list) or not entries:
        raise CompileError("playlist needs a non-empty units list")
    for raw in entries:
        entry = {"id": raw} if isinstance(raw, str) else raw
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise CompileError("playlist entry must be a reference or object with id")
        ref = entry["id"]
        library, unit_id = ref.split(":", 1) if ":" in ref else (entry.get("library", "metronomics"), ref)
        identifier(library, "library")
        identifier(unit_id)
        if library not in roots:
            raise CompileError(f"unknown library: {library}")
        root = roots[library].resolve()
        path = (root / f"{unit_id}.json").resolve()
        if not path.is_relative_to(root):
            raise CompileError("unit escapes its library")
        unit = load_json(path)
        if not isinstance(unit, dict) or unit.get("id") != unit_id:
            raise CompileError(f"unit file id must be {unit_id!r}")
        slides = unit.get("slides", [unit])
        if not isinstance(slides, list) or not slides:
            raise CompileError(f"unit {ref} needs slides")
        by_id = {}
        for slide in slides:
            if not isinstance(slide, dict):
                raise CompileError("slide must be an object")
            sid = identifier(slide.get("id"), "slide id")
            if any(str(key).startswith("_") for key in slide):
                raise CompileError(f"slide {ref}#{sid} sets a build-only field; names starting with _ belong to the compiler")
            if sid in by_id:
                raise CompileError(f"duplicate slide id: {sid}")
            by_id[sid] = slide
        selection = entry.get("slides", list(by_id))
        if not isinstance(selection, list) or not selection or any(sid not in by_id for sid in selection if isinstance(sid, str)) or any(not isinstance(sid,str) for sid in selection):
            raise CompileError(f"unknown or invalid slide selection in {ref}")
        override = entry.get("override", {})
        if not isinstance(override, dict):
            raise CompileError("override must be an object")
        if any(key in override for key in ("id", "slides", "artifact", "seed")) or any(key.startswith("_") for key in override):
            raise CompileError("override cannot change a unit id or source identity")
        for sid in selection:
            slide = dict(by_id[sid])
            for field in ("artifact", "seed", "tags"):
                if field not in slide and field in unit:
                    slide[field] = unit[field]
            slide.update(override)
            if any(not isinstance(slide.get(key), str) for key in ("title", "headline")):
                raise CompileError(f"slide {ref}#{sid} requires string title and headline fields")
            if slide.get("layout") not in LAYOUTS:
                raise CompileError(f"unknown layout in {ref}#{sid}")
            if not isinstance(slide.get("tags", []), list):
                raise CompileError("tags must be a list")
            slide["_root"] = root
            slide["_source"] = f"{library}:{unit_id}#{sid}"
            slide["_source_hash"] = hashlib.sha256(path.read_bytes()).hexdigest()
            slide["_path"] = str(path)
            resolved.append(slide)
    return assign_names(resolved)


def slide_name(reference: str) -> str:
    """Stable, readable link name for a slide: <unit>-<slide>, or <unit> when they match."""
    unit_id, sid = reference.split(":", 1)[1].split("#", 1)
    name = unit_id if sid == unit_id else f"{unit_id}-{sid}"
    name = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    # Never collide with the numeric #slide-N form the runtime still accepts.
    return f"n-{name}" if re.fullmatch(r"slide-\d+", name) else name


def assign_names(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Give every slide in a deck a unique name; a repeated slide gets -2, -3."""
    seen: dict[str, int] = {}
    for slide in slides:
        base = slide_name(slide["_source"])
        seen[base] = seen.get(base, 0) + 1
        slide["_name"] = base if seen[base] == 1 else f"{base}-{seen[base]}"
    return slides


def load_playlist_file(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise CompileError("playlist must be an object")
    identifier(data.get("id"), "playlist id")
    data["_base"] = path.resolve().parent
    return data


def bundle_asset(root: Path, src: Any, dest: Path) -> tuple[str, str]:
    """Copy one library image into the build under a content hash. Fail closed."""
    if not isinstance(src, str) or not src:
        raise CompileError("an image needs a local src")
    try:
        source = (root / src).resolve()
    except (OSError, ValueError, RuntimeError) as exc:  # RuntimeError: a link that points at itself
        raise CompileError("artwork must be an image inside its library") from exc
    if not source.is_relative_to(root) or source.suffix.lower() not in IMAGE_SUFFIXES:
        raise CompileError("artwork must be an image inside its library")
    if not source.is_file():
        raise CompileError(f"missing artwork: {source}")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    relative = f"assets/{digest[:20]}{source.suffix.lower()}"
    (dest / "assets").mkdir(exist_ok=True)
    shutil.copy2(source, dest / relative)
    return relative, digest


def inline_svg(root: Path, figure: Any) -> str:
    """Read one library SVG figure for inlining. Refuse scripts, handlers and references."""
    if not isinstance(figure, dict) or not isinstance(figure.get("src"), str) or not visible_text(figure.get("alt")):
        raise CompileError("a figure needs a local svg src and descriptive alt text")
    source = (root / figure["src"]).resolve()
    if not source.is_relative_to(root) or source.suffix.lower() != ".svg":
        raise CompileError("a figure must be an svg inside its library")
    if not source.is_file():
        raise CompileError(f"missing figure: {source}")
    text = source.read_text(encoding="utf-8").strip()
    text = re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", text)
    if not re.match(r"<svg[\s>]", text) or not text.endswith("</svg>") or text.count("<svg") != 1:
        raise CompileError("a figure file must hold exactly one svg element")
    if SVG_FORBIDDEN.search(text) or "http" in text.lower():
        raise CompileError("a figure cannot contain scripts, event handlers, styles or references")
    label = escape(visible_text(figure["alt"]))
    return re.sub(r"^<svg", f'<svg class="figure-svg" role="img" aria-label="{label}"', text, count=1)


_HOT_IDS = itertools.count(1)


def view_box(art: dict[str, Any], what: str) -> tuple[float, float]:
    box = art.get("viewbox")
    if not (isinstance(box, list) and len(box) == 2 and all(number(v) and v > 0 for v in box)):
        raise CompileError(f"{what} need a viewbox of [width, height]")
    return box[0], box[1]


def target_hole(target: Any) -> str:
    """One bright area in a hotspot's dim mask: an [x, y, w, h] box, or a line along points."""
    if isinstance(target, list) and len(target) == 4 and all(number(v) for v in target):
        tx, ty, tw, th = target
        return f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="black"/>'
    if isinstance(target, dict) and set(target) == {"points", "width"}:
        points, stroke = target["points"], target["width"]
        if not (isinstance(points, list) and len(points) >= 2
                and all(isinstance(p, list) and len(p) == 2 and all(number(v) for v in p) for p in points)):
            raise CompileError("a line target needs at least two [x, y] points in viewBox units")
        if not (number(stroke) and stroke > 0):
            raise CompileError("a line target needs a width above zero")
        path = " ".join(f"{x},{y}" for x, y in points)
        return (f'<polyline points="{path}" fill="none" stroke="black" stroke-width="{stroke}" '
                'stroke-linecap="round" stroke-linejoin="round"/>')
    raise CompileError('hotspot targets are [x, y, w, h] boxes or {"points": [[x, y], ...], "width": n} lines in viewBox units')


def hotspot_parts(art: dict[str, Any], width: float, height: float) -> list[str]:
    spots = art.get("hotspots")
    if not isinstance(spots, list):
        raise CompileError("hotspots must be a list")
    parts = []
    for spot in spots:
        if not isinstance(spot, dict) or not all(number(spot.get(k)) for k in ("x", "y", "w", "h")) or not (spot["w"] and spot["h"]):
            raise CompileError("each hotspot needs numeric x, y, w and h")
        term, tip = visible_text(spot.get("term")), visible_text(spot.get("tip"))
        if not term or not tip:
            raise CompileError("each hotspot needs a term and a tip")
        pos = (f'left:{spot["x"] / width * 100:.3f}%;top:{spot["y"] / height * 100:.3f}%;'
               f'width:{spot["w"] / width * 100:.3f}%;height:{spot["h"] / height * 100:.3f}%')
        below = " hotspot--below" if spot["y"] / height < 0.3 else ""
        icon = spot.get("icon", [spot["x"] + spot["w"] - 26, spot["y"] + 26])
        if icon is False:
            mark = ""  # "icon": false hides the info mark; the area still answers hover, focus and tap.
        elif not (isinstance(icon, list) and len(icon) == 2 and all(number(v) for v in icon)):
            raise CompileError("a hotspot icon is [x, y] in viewBox units, or false for no mark")
        else:
            mark = (f'<span class="hotspot-i" aria-hidden="true" style="left:{(icon[0] - spot["x"]) / spot["w"] * 100:.3f}%;'
                    f'top:{(icon[1] - spot["y"]) / spot["h"] * 100:.3f}%">i</span>')
        targets = spot.get("targets", [])
        if not isinstance(targets, list):
            raise CompileError("hotspot targets must be a list")
        if targets:
            # Dim the artwork (or the spot's "dim" box) except the targets, which stay in full colour.
            holes = "".join(target_hole(target) for target in targets)
            dx, dy, dw, dh = spot.get("dim", [0, 0, width, height])
            mask_id = f"hotdim{next(_HOT_IDS)}"
            mark += (f'<svg class="hot-dim" aria-hidden="true" viewBox="0 0 {width} {height}" preserveAspectRatio="none" '
                     f'style="left:{-spot["x"] / spot["w"] * 100:.3f}%;top:{-spot["y"] / spot["h"] * 100:.3f}%;'
                     f'width:{width / spot["w"] * 100:.3f}%;height:{height / spot["h"] * 100:.3f}%">'
                     f'<mask id="{mask_id}"><rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" fill="white"/>{holes}</mask>'
                     f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" mask="url(#{mask_id})"/></svg>')
            below += " hotspot--targets"
        parts.append(f'<span class="hotspot{below}" tabindex="0" style="{pos}" aria-label="{escape(term)}: {escape(tip)}">{mark}'
                     + (f'<span class="hotspot-tip" role="tooltip"><strong>{escape(term)}</strong>{escape(tip)}</span>' if not targets else "") + '</span>')
    return parts


def link_parts(art: dict[str, Any], width: float, height: float) -> tuple[list[str], str]:
    """Clickable areas over a picture, and the same links as a row of text beneath it."""
    links = art.get("links")
    if not isinstance(links, list) or not links:
        raise CompileError("links must be a non-empty list")
    areas, texts = [], []
    for link in links:
        if not isinstance(link, dict) or set(link) - {"x", "y", "w", "h", "href", "label"}:
            raise CompileError("each link takes x, y, w, h, href and an optional label")
        if not all(number(link.get(k)) for k in ("x", "y", "w", "h")):
            raise CompileError("each link needs numeric x, y, w and h in viewBox units")
        x, y, w, h = (link[k] for k in ("x", "y", "w", "h"))
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > width or y + h > height:
            raise CompileError("a link area must sit inside the picture's viewbox")
        href = safe_link(link.get("href"))
        label = link_label(link.get("label", MISSING), href)
        pos = f"left:{x / width * 100:.3f}%;top:{y / height * 100:.3f}%;width:{w / width * 100:.3f}%;height:{h / height * 100:.3f}%"
        areas.append(f'{link_tag(href, "art-link")} style="{pos}" aria-label="{escape(label)}, opens in a new tab"></a>')
        texts.append(f'{link_tag(href, "art-link-text")}>{escape(label)}</a>')
    return areas, f'<span class="art-links">{"".join(texts)}</span>'


def art_overlay(image: str, art: dict[str, Any]) -> tuple[str, str]:
    """Overlay hover definitions and links on artwork. Boxes are in the artwork's viewBox units.

    Returns the wrapped picture and the row of text links that goes beneath it.
    """
    has_spots, has_links = bool(art.get("hotspots")), "links" in art
    if "qr" in art and not isinstance(art["qr"], bool):
        raise CompileError('artwork "qr" is true or false')
    if art.get("qr") is True and not has_links:
        raise CompileError('a picture marked "qr": true must record a link for each code in "links"')
    if not has_spots and not has_links:
        return image, ""
    width, height = view_box(art, "links" if has_links and not has_spots else "hotspots")
    parts = hotspot_parts(art, width, height) if has_spots else []
    row = ""
    if has_links:
        areas, row = link_parts(art, width, height)
        parts += areas
    return f'<span class="art-hot" style="--ar:{width}/{height}">{image}{"".join(parts)}</span>', row


def hotspot_wrap(image: str, art: dict[str, Any]) -> str:
    """Overlay hover definitions on artwork. Kept for callers that only need the picture."""
    view_box(art, "hotspots")
    if not isinstance(art.get("hotspots"), list):
        raise CompileError("hotspots must be a list")
    return art_overlay(image, art)[0]


def image_ratio(path: Path) -> float:
    """Width over height of a library picture, so a hover picture has its size before it loads."""
    ratio = None
    try:
        if path.suffix.lower() == ".svg":
            head = path.read_text(encoding="utf-8", errors="replace")[:4000]
            found = re.search(r'viewBox="\s*-?[\d.]+[\s,]+-?[\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*"', head)
            if found and float(found.group(2)) > 0:
                ratio = float(found.group(1)) / float(found.group(2))
        elif path.suffix.lower() == ".png":
            data = path.read_bytes()[:24]
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                wide, tall = struct.unpack(">II", data[16:24])
                ratio = wide / tall if tall else None
    except (OSError, ValueError, struct.error):
        ratio = None
    return round(min(4.0, max(0.4, ratio)), 4) if ratio else 1.6


def prepare_terms(unit: dict[str, Any], root: Path, dest: Path) -> None:
    """Bundle the picture a hover term shows ("image" on a "terms" entry)."""
    terms = unit.get("terms")
    if not isinstance(terms, list):
        return
    prepared = []
    for entry in terms:
        if isinstance(entry, dict) and "image" in entry:
            image = entry["image"]
            if not isinstance(image, dict) or set(image) - {"src", "alt"} or not isinstance(image.get("alt"), str) or not visible_text(image["alt"]):
                raise CompileError("a term image needs a local src and descriptive alt text")
            relative, _ = bundle_asset(root, image.get("src"), dest)
            entry = {**entry, "_image": {"src": relative, "alt": visible_text(image["alt"]), "ratio": image_ratio((root / image["src"]).resolve())}}
        prepared.append(entry)
    unit["terms"] = prepared


DECK_QR = "assets/deck-qr.svg"


def display_url(url: str) -> str:
    return url.split("://", 1)[-1].rstrip("/")


def deck_qr_alt(url: str) -> str:
    return f"QR code that opens these slides at {display_url(url)}."


def write_deck_qr(dest: Path, url: str) -> None:
    import qr_svg
    (dest / "assets").mkdir(exist_ok=True)
    (dest / DECK_QR).write_text(qr_svg.svg(url, deck_qr_alt(url)), encoding="utf-8")


def prepare_artwork(units: list[dict[str, Any]], dest: Path, deck_url: str | None = None) -> None:
    for unit in units:
        root = Path(unit["_root"])
        if unit.get("deck_qr") is True:
            # A QR code that opens the deck it sits in. Freezing a delivered copy rewrites it,
            # so the code always opens the version the audience saw (Byron, 16-Nov-2026).
            if unit.get("artwork"):
                raise CompileError("a deck_qr slide draws its own code; remove its artwork")
            if not deck_url:
                raise CompileError("a deck_qr slide needs the deck's public URL")
            write_deck_qr(dest, deck_url)
            unit["artwork"] = {"src": DECK_QR, "alt": deck_qr_alt(deck_url)}
            # Freezing rewrites this address by its folder form, so a query or fragment would be left behind.
            if not deck_url.endswith("/") or "?" in deck_url or "#" in deck_url:
                raise CompileError("a deck's public address is a folder address ending in /, with no ? or #")
            unit["_deck_url"] = safe_link(deck_url)
            unit["body"] = [display_url(deck_url) if item == "{deck_url}" else item for item in unit.get("body") or []]
            prepare_terms(unit, root, dest)
            continue
        art = unit.get("artwork")
        if art:
            if not isinstance(art, dict) or not isinstance(art.get("src"), str) or not art.get("alt"):
                raise CompileError("artwork needs a local src and descriptive alt text")
            relative, digest = bundle_asset(root, art["src"], dest)
            unit["artwork"] = {**art, "src": relative, "sha256": digest}
        prepare_terms(unit, root, dest)
        if unit.get("layout") == "about-timeline":
            rows = unit.get("timeline")
            if not isinstance(rows, list) or not rows:
                raise CompileError("a timeline needs a non-empty timeline list")
            bundled = []
            for row in rows:
                if not isinstance(row, dict) or not visible_text(row.get("text")) or row.get("kind", "logo") not in TIMELINE_KINDS:
                    raise CompileError("a timeline row needs text and a photo, logo or illustration kind")
                media = row.get("media")
                if not isinstance(media, list) or not 1 <= len(media) <= 2:
                    raise CompileError("a timeline row needs one or two images")
                images = []
                for item in media:
                    if not isinstance(item, dict) or not visible_text(item.get("alt")):
                        raise CompileError("every timeline image needs descriptive alt text")
                    relative, _ = bundle_asset(root, item.get("src"), dest)
                    images.append({**item, "src": relative})
                bundled.append({**row, "media": images})
            unit["timeline"] = bundled
        if unit.get("layout") == "comp-figure":
            unit["_figure_svg"] = inline_svg(root, unit.get("figure"))


def public_url(playlist_id: str) -> str:
    return f"{PUBLIC_PAGES_ROOT}/{COACHING_SLIDES_REL}/{playlist_id}/"


def coaching_slides_dest(dest_root: Path, playlist_id: str) -> Path:
    return dest_root / COACHING_SLIDES_REL / playlist_id


def escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def visible_text(value: Any) -> str:
    """Return stripped text, or empty. Do not invent a stand-in title."""
    return str(value).strip() if value is not None else ""


def notes_html(notes: Any) -> str:
    items = notes if isinstance(notes, list) else [notes] if notes is not None else []
    paragraphs = []
    for item in items:
        text = str(item).strip()
        if text:
            paragraphs.append(f"        <p>{escape(text)}</p>")
    if not paragraphs:
        paragraphs.append("        <p>No speaker notes.</p>")
    return "\n".join(paragraphs)


def emphasis(text: str) -> str:
    """Escape text, then render **word** as a highlighted <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r'<strong class="hl">\1</strong>', escape(text))


def term_tips(html: str, unit: dict[str, Any], below: bool = False) -> str:
    """Wrap each listed term in already-escaped text with a hover definition (unit "terms").

    A term may show text lines ("tip"), a library picture ("image"), or both. "below" opens the
    box under the word, for a title at the top of a slide. Terms are matched against the text
    as written, never inside a tag or inside another term's box, and matches cannot overlap.
    """
    terms = unit.get("terms") or []
    if not isinstance(terms, list):
        raise CompileError("terms must be a list")
    tokens = re.split(r"(<[^>]*>)", html)  # even places are text, odd places are tags
    claimed: dict[int, list[tuple[int, int, str]]] = {}
    for entry in terms:
        term, tip = visible_text(entry.get("term")) if isinstance(entry, dict) else "", entry.get("tip") if isinstance(entry, dict) else None
        lines = tip if isinstance(tip, list) else [tip]
        lines = [visible_text(line) for line in lines if visible_text(line)]
        wants_image = isinstance(entry, dict) and "image" in entry
        picture = entry.get("_image") if wants_image else None
        if wants_image and not picture:
            raise CompileError("a term image needs preparing before the slide renders")
        if not term or not (lines or picture):
            raise CompileError("each term needs a term and a tip or an image")
        label = escape(term)
        body = "".join(f'<span class="term-line">{escape(line)}</span>' for line in lines)
        spoken = " ".join(lines)
        css, ratio = "term", ""
        if picture:
            body += (f'<img class="term-image" src="./{escape(picture["src"])}" alt="{escape(picture["alt"])}" '
                     f'style="--ar:{picture["ratio"]}">')
            ratio = f' style="--ar:{picture["ratio"]}"'
            spoken = f'{spoken} {picture["alt"]}'.strip()
            css += " term--image"
        if below:
            css += " term--below"
        span = (f'<span class="{css}" tabindex="0" aria-label="{label}: {escape(spoken)}">{label}'
                f'<span class="hotspot-tip" role="tooltip"{ratio}><strong>{label}</strong>{body}</span></span>')
        for place in range(0, len(tokens), 2):
            taken = claimed.get(place, [])
            start = tokens[place].find(label)
            while start != -1 and any(start < end and begin < start + len(label) for begin, end, _ in taken):
                start = tokens[place].find(label, start + 1)
            if start != -1:
                claimed.setdefault(place, []).append((start, start + len(label), span))
                break
    for place, matches in claimed.items():
        text = tokens[place]
        for begin, end, span in sorted(matches, reverse=True):
            text = text[:begin] + span + text[end:]
        tokens[place] = text
    return "".join(tokens)


def support_paragraphs(unit: dict[str, Any]) -> str:
    blocks: list[str] = []
    support = visible_text(unit.get("support"))
    if support:
        blocks.append(f"          <p class=\"support\">{term_tips(emphasis(support), unit)}</p>")
    body = unit.get("body") or []
    item_class = "support check-item" if unit.get("checklist") is True else "support"
    if isinstance(body, list):
        for item in body:
            text = visible_text(item)
            deck_url = unit.get("_deck_url")
            if text and deck_url and text == display_url(deck_url):
                # The address beside a deck QR code is a real link. Freezing a copy rewrites it.
                blocks.append(f"          <p class=\"{item_class}\">{link_tag(deck_url)}>{escape(text)}</a></p>")
            elif text:
                blocks.append(f"          <p class=\"{item_class}\">{term_tips(escape(text), unit)}</p>")
    return "\n".join(blocks)


def panel_items(unit: dict[str, Any]) -> list[str]:
    body = unit.get("body")
    items: list[str] = []
    if isinstance(body, list):
        items = [visible_text(item) for item in body if visible_text(item)]
    return items


def heading_html(text: str, css_class: str, indent: str = "        ", unit: dict[str, Any] | None = None) -> str:
    """A slide title. With its unit, listed "terms" in the title get their hover definition."""
    if not text:
        return ""
    inner = term_tips(escape(text), unit, below=True) if unit else escape(text)
    return f"{indent}<h1 class=\"{css_class}\">{inner}</h1>\n"


def eyebrow_html(text: str) -> str:
    if not text:
        return ""
    return f'        <p class="eyebrow">{escape(text)}</p>\n'


def accent_heading_html(unit: dict[str, Any], css_class: str) -> str:
    """A headline with an optional blue second clause."""
    headline = visible_text(unit.get("headline"))
    accent = visible_text(unit.get("headline_accent"))
    if not headline:
        return ""
    tail = f' <span class="title-accent">{term_tips(escape(accent), unit, below=True)}</span>' if accent else ""
    return f'        <h1 class="{css_class}">{term_tips(escape(headline), unit, below=True)}{tail}</h1>\n'


def timeline_html(unit: dict[str, Any]) -> str:
    items = []
    for row in unit["timeline"]:
        kind = row.get("kind", "logo")
        classes = ["timeline-media", "timeline-photo" if kind == "photo" else "timeline-logo"]
        if kind == "illustration":
            classes.append("timeline-logo--illus")
        if row.get("portrait"):
            classes.append("timeline-portrait")
        if len(row["media"]) == 2:
            classes.append("timeline-logo--two")
        lazy = ' loading="lazy"' if kind == "photo" else ""
        images = "".join(f'<img src="./{escape(m["src"])}" alt="{escape(visible_text(m["alt"]))}"{lazy}>' for m in row["media"])
        age = row.get("age")
        age_html = f'<span class="timeline-age">age {escape(age)}</span>' if age is not None else ""
        items.append(f'<li class="timeline-item"><span class="timeline-year">{escape(row.get("year", ""))}</span><div class="{" ".join(classes)}">{images}</div><p class="timeline-text">{escape(visible_text(row["text"]))}{age_html}</p></li>')
    label = visible_text(unit.get("timeline_label")) or "Timeline, scrollable"
    heading = visible_text(unit.get("timeline_title"))
    heading_html = f'<h2 class="timeline-heading">{escape(heading)}</h2>' if heading else ""
    return f'<div class="timeline-column">{heading_html}<ol class="timeline-list" tabindex="0" aria-label="{escape(label)}">{"".join(items)}</ol></div>'


def attempts_html(unit: dict[str, Any], limit: int = 4, compact: bool = False) -> str:
    attempts = unit.get("attempts")
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= limit:
        raise CompileError(f"an attempts slide needs one to {limit} attempts")
    cards = []
    for index, item in enumerate(attempts, start=1):
        if not isinstance(item, dict) or not visible_text(item.get("heading")):
            raise CompileError("every attempt needs a heading")
        win = " attempt--win" if item.get("win") is True else ""
        cards.append(
            f'<article class="attempt{win}"><span class="attempt-year"><span class="attempt-badge">{index}</span>{escape(item.get("year", ""))}</span>'
            f'<h2>{escape(item["heading"])}</h2>{"" if compact and not item.get("support") else "<p>" + escape(item.get("support", "")) + "</p>"}<span class="attempt-outcome">{escape(item.get("outcome", ""))}</span></article>'
        )
    extra = " attempts-compact" if compact else ""
    return f'<div class="attempts-grid attempts-{len(cards)}{extra}">{"".join(cards)}</div>'


def render_slide(unit: dict[str, Any], number: int, branding: dict[str, Any] | None = None) -> str:
    layout = unit["layout"]
    title = visible_text(unit.get("title"))
    headline = visible_text(unit.get("headline"))
    eyebrow = eyebrow_html(visible_text(unit.get("eyebrow")))
    art = unit.get("artwork")
    replay = " data-replay" if art and art.get("replay") is True else ""
    image = f'<img src="./{escape(art["src"])}" alt="{escape(art["alt"])}"{replay}>' if art else ""
    links_row = ""
    if art:
        image, links_row = art_overlay(image, art)
        if links_row and layout != "comp-story":
            raise CompileError("artwork links are supported on comp-story slides only")
    if unit.get("_deck_url") and image:
        # The deck's own QR code is itself a link to the deck.
        image = f'{link_tag(unit["_deck_url"], "art-link-img")} aria-label="{escape(display_url(unit["_deck_url"]))}, opens in a new tab">{image}</a>'
    title_of = lambda css: heading_html(headline, css, unit=unit)
    if layout == "title":
        if headline and not image:
            raise CompileError("a populated opening slide requires artwork")
        inner = f'<div class="title-opening"><div class="title-identity">{title_of("slide-title")}<hr class="hairline" aria-hidden="true"></div><div class="title-art">{image}</div></div>' if headline else ""
    elif layout == "comp-story":
        panel = (image + links_row) if image else support_paragraphs(unit)
        art_class = (" story-panel--art" + (" story-panel--links" if links_row else "")) if image else ""
        fit = " story-frame--fit" if image and unit.get("art_fit") is True else ""
        wide = (" story-frame--full" + fit) if image and unit.get("art_full") is True else (" story-frame--wide" if image and unit.get("art_wide") is True else "")
        if image and unit.get("art_side") is True:
            copy = f'<div class="story-copy">{title_of("story-title")}{support_paragraphs(unit)}</div>'
            narrow = " story-frame--art-narrow" if unit.get("art_narrow") is True else ""
            inner = f'<div class="slide-stage"><div class="story-frame story-frame--side{narrow}">{copy}<div class="story-panel{art_class}">{panel}</div></div></div>'
        elif not image and (unit.get("checklist") is True or unit.get("copy_stack") is True):
            copy = f'<div class="story-copy">{title_of("story-title")}{support_paragraphs(unit)}</div>'
            short = " story-frame--short" if unit.get("copy_stack") is True else ""
            inner = f'<div class="slide-stage"><div class="story-frame story-frame--side story-frame--copy{short}">{copy}</div></div>'
        else:
            lede = ""
            if image:
                support = visible_text(unit.get("support"))
                if unit.get("art_full") is True:
                    # One instruction line under the title. Body text has no place on this layout.
                    if support:
                        lede = f'<p class="support story-lede">{term_tips(emphasis(support), unit)}</p>'
                        wide += " story-frame--lede"
                    if panel_items(unit):
                        dropped_text(unit, 'a full-width drawing slide (art_full) cannot show "body" text; move one line to "support" or use art_side')
                elif support or panel_items(unit):
                    dropped_text(unit, 'a drawing slide shows only its title and picture; "support" and "body" are dropped. Use art_full for one line or art_side for more')
            inner = f'<div class="slide-stage"><div class="story-frame{wide}">{heading_html(headline, "story-title", unit=unit)}{lede}<div class="story-panel{art_class}">{panel}</div></div></div>'
    elif layout in {"comp-causal", "comp-decision"}:
        panels = unit.get("panels")
        if panels is None:
            roles = ("Action", "Gap") if layout == "comp-decision" else ("Structure", "Action", "Structure")
            panels = [{"heading": item, "role": roles[i], "mark": roles[i].lower()} for i, item in enumerate(panel_items(unit)) if i < len(roles)]
        limit = 6 if layout == "comp-decision" and unit.get("arrows") is False else 4
        if not isinstance(panels, list) or len(panels) > limit:
            raise CompileError("a card slide supports at most four panels, or a grid of six")
        cells = []
        arrows = layout == "comp-causal" and unit.get("arrows", True)
        if arrows and len(panels) > 3:
            raise CompileError("a connected causal sequence supports at most three panels")
        numbered = bool(panels) and all(isinstance(p, dict) and NUMBERED_ROLE.fullmatch(str(p.get("role", ""))) for p in panels)
        sequence = numbered or arrows
        for panel in panels:
            if not isinstance(panel, dict) or panel.get("mark", "structure") not in {"structure", "action", "gap"}:
                raise CompileError("invalid panel or colour role")
            if cells and arrows:
                cells.append('<p class="causal-arrow" aria-hidden="true">→</p>')
            if numbered:
                match = NUMBERED_ROLE.fullmatch(str(panel["role"]))
                label = (match.group(2) or "").strip()
                role = f'<p class="role">{escape(label)}</p>' if label else ""
                head = f'{role}<h2><span class="step">{int(match.group(1))}</span>{escape(panel.get("heading", ""))}</h2>'
            else:
                head = f'<p class="role">{escape(panel.get("role", ""))}</p><h2>{escape(panel.get("heading", ""))}</h2>'
            items = panel.get("items") or []
            if not isinstance(items, list):
                raise CompileError("panel items must be a list")
            agenda = ('<ol class="panel-items">' + "".join(f"<li>{term_tips(escape(visible_text(i)), unit)}</li>" for i in items if visible_text(i)) + "</ol>") if items else ""
            cells.append(f'<article class="panel mark-{escape(panel.get("mark", "structure"))}">{head}<p class="support title-follow">{term_tips(escape(panel.get("support", "")), unit)}</p>{agenda}</article>')
        row = "causal-row" if arrows else ("grid-6" if len(panels) == 6 else "meet-grid" if len(panels) == 4 else "stack-3" if len(panels) == 3 else "decision-row")
        if sequence:
            row += f" seq seq-{len(panels)}"
        lede_text = visible_text(unit.get("support"))
        lede = f'<p class="support card-lede title-follow">{escape(lede_text)}</p>' if lede_text else ""
        inner = eyebrow + title_of("slide-title") + lede + f'<div class="slide-stage title-follow"><div class="{row}">{"".join(cells)}</div></div>'
    elif layout == "about-timeline":
        role = visible_text(unit.get("role"))
        role_html = f'<p class="identity-role">{escape(role)}</p>' if role else ""
        identity = f'<div class="timeline-identity">{eyebrow}{title_of("story-title")}{role_html}<hr class="identity-hair" aria-hidden="true">{support_paragraphs(unit)}</div>'
        inner = f'<div class="slide-stage"><div class="timeline-frame">{identity}{timeline_html(unit)}</div></div>'
    elif layout == "comp-attempts":
        inner = eyebrow + accent_heading_html(unit, "slide-title") + f'<div class="slide-stage title-follow">{attempts_html(unit)}</div>'
    elif layout == "comp-figure":
        if "_figure_svg" not in unit:
            raise CompileError("a figure slide needs its svg prepared")
        inner = eyebrow + accent_heading_html(unit, "slide-title") + f'<div class="slide-stage title-follow">{unit["_figure_svg"]}{attempts_html(unit, limit=5, compact=True) if unit.get("attempts") is not None else ""}</div>'
    else:
        inner = f'<div class="rule-stack">{title_of("slide-title")}<p class="rule-line support title-follow">{escape(unit.get("support", ""))}</p></div>'
        if image:
            inner = f'<div class="rule-frame">{inner}<div class="rule-art">{image}</div></div>'
    brand = branding or {}
    if not isinstance(brand, dict) or brand.get("logo", "metronomics") not in {"metronomics", "none"}:
        raise CompileError("branding must use the metronomics or none logo")
    logo = '<img class="footer-logo" src="./assets/metronomics-logo.svg" alt="Metronomics">' if brand.get("logo", "metronomics") == "metronomics" else ""
    footer = f'<footer class="slide-footer"><span>{escape(brand.get("domain", "darlison.com"))}</span>{logo}</footer>'
    css = "layout-title" if layout == "title" else layout
    return f'''    <section class="slide {css}" id="slide-{number}" data-name="{escape(unit.get('_name', ''))}"{' data-deck-qr="true"' if unit.get('deck_qr') is True else ''} data-group="{escape(unit.get('group', ''))}" data-title="{escape(title)}" data-unit="{escape(unit['id'])}" data-source="{escape(unit.get('_source', unit['id']))}">
      <div class="slide-content"><span class="slide-label">{number:02d} {layout}</span>{inner}{footer}</div>
      <aside class="speaker-notes">{notes_html(unit.get('notes', []))}</aside>
    </section>'''


def render_deck(playlist: dict[str, Any], units: list[dict[str, Any]]) -> str:
    title = visible_text(playlist.get("title"))
    sidebar_title = visible_text(playlist.get("sidebar_title"))
    sidebar_help = visible_text(playlist.get("sidebar_help")) or (
        "Arrow keys move. Press N for notes. Press F for full screen."
    )
    description = visible_text(playlist.get("description"))
    sidebar_blurb = visible_text(playlist.get("sidebar_blurb"))
    slides = "\n\n".join(render_slide(unit, index + 1, playlist.get("branding")) for index, unit in enumerate(units))
    count = len(units)
    doc_title = title or "Slides"
    sidebar_heading = f"      <h1>{escape(sidebar_title)}</h1>\n" if sidebar_title else ""
    sidebar_blurb_html = f"      <p>{escape(sidebar_blurb)}</p>\n" if sidebar_blurb else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description)}">
  <link rel="icon" href="data:,">
  <title>{escape(doc_title)}</title>
  <link rel="preload" href="./fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="./fonts/geist-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="./shell.css">
</head>
<body>
  <button class="sidebar-toggle" id="sidebarToggle" type="button" aria-label="Open slide navigation" aria-expanded="false" aria-controls="slideSidebar">☰</button>
  <div class="sidebar-backdrop" id="sidebarBackdrop" aria-hidden="true"></div>

  <aside class="slide-sidebar" id="slideSidebar" aria-label="Slide navigation">
    <header class="sidebar-head">
{sidebar_heading}{sidebar_blurb_html}    </header>
    <nav class="sidebar-nav" id="sidebarNav" aria-label="Presentation slides"></nav>
    <p class="sidebar-help">{escape(sidebar_help)}<br>Press S to hide the sidebar.</p>
  </aside>

  <main id="presentation" aria-label="{escape(doc_title)}">
{slides}
  </main>

  <div class="controls" aria-label="Presentation controls">
    <button class="control-button control-button--wide" id="sidebarDesktopToggle" type="button" aria-controls="slideSidebar" aria-expanded="true">Hide sidebar</button>
    <button class="control-button" id="previousButton" type="button" aria-label="Previous slide">←</button>
    <div class="control-count" id="controlCount" aria-live="polite">1 / {count}</div>
    <button class="control-button control-button--wide" id="fullscreenButton" type="button" aria-label="Enter full screen" aria-pressed="false">
      <span aria-hidden="true">⛶</span>
      <span id="fullscreenLabel">Full screen</span>
    </button>
    <button class="control-button" id="nextButton" type="button" aria-label="Next slide">→</button>
  </div>

  <aside class="notes-panel" id="notesPanel" aria-label="Speaker notes" aria-hidden="true">
    <div class="notes-header">
      <h2 id="notesTitle">Speaker notes</h2>
      <button class="notes-close" id="notesClose" type="button" aria-label="Close speaker notes">×</button>
    </div>
    <div class="notes-body" id="notesBody"></div>
  </aside>

  <script src="./shell.js"></script>
</body>
</html>
"""


def copy_shell(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in SHELL_FILES:
        source = SHARED_DECK / name
        if not source.is_file():
            raise CompileError(f"shared shell missing {name}")
        shutil.copy2(source, dest / name)
    (dest / "assets").mkdir(exist_ok=True)
    shutil.copy2(SHARED_DECK / "assets/metronomics-logo.svg", dest / "assets/metronomics-logo.svg")
    fonts_src = SHARED_DECK / "fonts"
    fonts_dest = dest / "fonts"
    fonts_dest.mkdir(parents=True, exist_ok=True)
    for name in FONT_NAMES:
        source = fonts_src / name
        if not source.is_file():
            raise CompileError(f"shared shell missing fonts/{name}")
        shutil.copy2(source, fonts_dest / name)


def compile_playlist(playlist_id: str, out_dir: Path | None = None, playlist_file: Path | None = None,
                     fail_on_dropped_text: bool = False) -> Path:
    playlist = load_playlist_file(playlist_file) if playlist_file else load_playlist(playlist_id)
    playlist_id = identifier(playlist["id"], "playlist id")
    units = resolve_playlist(playlist)
    WARNINGS.clear()
    for unit in units:
        unit["_fail_on_dropped_text"] = fail_on_dropped_text
    requested = out_dir or (COMPILED / playlist_id)
    if any(part.is_symlink() for part in [requested, *requested.parents]):
        raise CompileError("output cannot traverse a symlink")
    dest = requested.resolve()
    # Never erase an arbitrary directory or a source library on a failed compile.
    protected = [SHARED_DECK.resolve(), *[Path(u["_root"]).resolve() for u in units]]
    if any(dest == root or root.is_relative_to(dest) or dest.is_relative_to(root) for root in protected):
        raise CompileError("output overlaps a source library or shared shell")
    if dest.exists() and any(dest.iterdir()) and not (dest / "manifest.json").is_file():
        raise CompileError("output is not an existing compiled deck; choose an empty directory")
    if dest.is_symlink():
        raise CompileError("output cannot be a symlink")
    if (dest / "manifest.json").exists():
        previous = load_json(dest / "manifest.json")
        if not isinstance(previous, dict) or previous.get("generator") != "darlison-slides":
            raise CompileError("output manifest is not a darlison-slides build")
    if (dest / ".git").exists():
        raise CompileError("refusing to compile into a git directory")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".deck-build-", dir=dest.parent) as temporary:
        stage = Path(temporary)
        copy_shell(stage)
        prepare_artwork(units, stage, playlist.get("public_url") or public_url(playlist_id))
        html_text = render_deck(playlist, units)
        check_no_dashes(html_text)
        check_no_network(html_text)
        (stage / "index.html").write_text(html_text, encoding="utf-8")
        manifest = {
            "generator": "darlison-slides",
            "playlist": playlist_id,
            "title": playlist.get("title") or playlist_id,
            "unit_ids": [u["id"] for u in units],
            "slides": [{"number": i + 1, "name": u["_name"], "reference": u["_source"]} for i, u in enumerate(units)],
            "sources": [{"reference": u["_source"], "sha256": u["_source_hash"], "artifact": u.get("artifact"), "seed": u.get("seed"), "artwork_sha256": u.get("artwork", {}).get("sha256")} for u in units],
            "public_path": f"{COACHING_SLIDES_REL}/{playlist_id}/",
            "public_url": public_url(playlist_id),
            "shell": ["shell.css", "shell.js", "fonts/", "assets/"],
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(stage, dest)
    # Every route that builds a deck (compile, publish) reports dropped text, once.
    for warning in WARNINGS:
        print(f"WARNING: {warning}", file=sys.stderr)
    return dest


def check_no_network(html_text: str) -> None:
    """Nothing in a deck loads from the network. A link a person clicks is the one address allowed."""
    lowered = DECK_LINK.sub("<a", html_text).lower()
    if "http://" in lowered or "https://" in lowered:
        raise CompileError("compiled HTML requests a network URL")


def check_no_dashes(html_text: str) -> None:
    decoded = html.unescape(html_text)
    if "\u2013" in decoded or "\u2014" in decoded:
        raise CompileError("compiled HTML contains an em or en dash")


def check_publish_overlap(deck: Path, target: Path) -> None:
    source = deck.resolve()
    dest = target.resolve()
    if source == dest or source.is_relative_to(dest) or dest.is_relative_to(source):
        raise CompileError("publish source and destination overlap")


def run_check_shell(deck: Path) -> int:
    if not CHECK_SHELL.is_file():
        raise CompileError(f"missing check-shell: {CHECK_SHELL}")
    result = subprocess.run(
        [sys.executable, str(CHECK_SHELL), "--deck", str(deck)],
        check=False,
        text=True,
    )
    return result.returncode


def copy_publish(deck: Path, dest_root: Path, playlist_id: str, dry_run: bool) -> Path:
    target = coaching_slides_dest(dest_root, playlist_id)
    if dry_run:
        print(f"DRY-RUN would copy {deck} -> {target}")
        print(f"Public URL after Pages publish: {public_url(playlist_id)}")
        return target
    if dest_root.exists() and not dest_root.is_dir():
        raise CompileError(f"publish dest is not a directory: {dest_root}")
    check_publish_overlap(deck, target)
    if (target / "FROZEN.json").is_file() or DELIVERED_REL in target.resolve().relative_to(dest_root.resolve()).parts:
        raise CompileError(f"refusing to publish over a frozen client copy: {target}")
    dest_root.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(deck, target)
    print(f"Copied {deck} -> {target}")
    print(f"Public URL after Pages publish: {public_url(playlist_id)}")
    print("Commit and push that copy in the coaching-slides repo. No extra credentials.")
    return target


# ---------------------------------------------------------------------------
# Change impact: which master decks a library change alters (Byron, 16-Nov-2026).

def master_playlists(presentations: Path) -> list[Path]:
    """Every playlist that builds a master deck: the explicit files and the legacy named ones."""
    found = sorted((presentations / "playlists").rglob("*.json"))
    found += sorted((presentations / "metronomics" / "playlists").glob("*.json"))
    return found


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=False, text=True, capture_output=True)
    if result.returncode:
        raise CompileError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def changed_paths(base: str, root: Path) -> set[Path]:
    rel = PRESENTATIONS.resolve().relative_to(root)
    names = git("diff", "--name-only", base, "--", str(rel), cwd=root).split()
    names += git("ls-files", "--others", "--exclude-standard", "--", str(rel), cwd=root).split()
    return {(root / n).resolve() for n in names}


def slide_content(slide: dict[str, Any]) -> str:
    """What a viewer sees and the presenter reads, without build-only fields."""
    return json.dumps({k: v for k, v in slide.items() if not k.startswith("_")}, sort_keys=True, default=str)


def resolve_quietly(path: Path, library: Path) -> list[dict[str, Any]] | None:
    try:
        return resolve_playlist(load_playlist_file(path), library)
    except (CompileError, OSError, ValueError):
        return None


def impact_report(base: str) -> list[dict[str, Any]]:
    root = Path(git("rev-parse", "--show-toplevel", cwd=PRESENTATIONS).strip()).resolve()
    changed = changed_paths(base, root)
    rel = PRESENTATIONS.resolve().relative_to(root)
    rows = []
    with tempfile.TemporaryDirectory(prefix="deck-impact-") as temporary:
        old_root = Path(temporary)
        archive = subprocess.run(["git", "archive", base, "--", str(rel)], cwd=root, check=False, capture_output=True)
        if archive.returncode:
            raise CompileError(f"cannot read {base}: {archive.stderr.decode().strip()}")
        subprocess.run(["tar", "-x", "-C", str(old_root)], input=archive.stdout, check=True)
        old_presentations = old_root / rel
        for path in master_playlists(PRESENTATIONS):
            now = resolve_quietly(path, LIBRARY)
            if now is None:
                continue
            if path.resolve() not in changed and not any(Path(u["_path"]).resolve() in changed for u in now):
                continue
            old_path = old_presentations / path.resolve().relative_to(PRESENTATIONS.resolve())
            before = resolve_quietly(old_path, old_presentations / "metronomics" / "library") if old_path.is_file() else None
            old_names = [u["_name"] for u in before] if before else []
            new_names = [u["_name"] for u in now]
            old_content = {u["_name"]: slide_content(u) for u in before or []}
            touched = [u["_name"] for u in now if u["_name"] in old_content and slide_content(u) != old_content[u["_name"]]]
            if not touched and old_names == new_names:
                continue
            rows.append({
                "playlist": load_playlist_file(path)["id"],
                "file": str(path.resolve().relative_to(PRESENTATIONS.resolve())),
                "slides_before": len(old_names) if before else None,
                "slides_after": len(new_names),
                "changed_slides": touched,
                "added": [n for n in new_names if n not in old_names],
                "removed": [n for n in old_names if n not in new_names],
            })
    return rows


def shell_changed(base: str) -> bool:
    root = Path(git("rev-parse", "--show-toplevel", cwd=PRESENTATIONS).strip()).resolve()
    return any(p.is_relative_to(SHARED_DECK.resolve()) for p in changed_paths(base, root))


def print_impact(rows: list[dict[str, Any]], base: str) -> None:
    if shell_changed(base):
        print("The shared deck shell changed: every master deck looks or behaves differently on its next build.")
    if not rows:
        print(f"No master deck changes against {base}.")
    for row in rows:
        before = "new deck" if row["slides_before"] is None else f"{row['slides_before']} slides"
        print(f"{row['playlist']} ({row['file']}): {before} -> {row['slides_after']} slides")
        if row["changed_slides"]:
            print(f"  changed: {', '.join(row['changed_slides'])}")
        if row["added"] and row["slides_before"] is not None:
            print(f"  added: {', '.join(row['added'])}")
        if row["removed"]:
            print(f"  removed: {', '.join(row['removed'])}")
    print("Frozen client copies under delivered/ never change unless Byron asks.")


# ---------------------------------------------------------------------------
# Frozen client copies (Byron, 16-Nov-2026): the master keeps one live address;
# each delivery is copied once to delivered/<deck>/<label>/ and never rebuilt.

DELIVERED_REL = "delivered"
LABEL = re.compile(r"\d{4}-\d{2}-\d{2}(-[a-z0-9]+(-[a-z0-9]+)*)?")


def freeze_copy(dest_root: Path, playlist_id: str, label: str, replace: bool, source_rel: str | None = None, today: str | None = None) -> Path:
    identifier(playlist_id, "playlist id")
    if not LABEL.fullmatch(label):
        raise CompileError("label must be a date, optionally with a short code: 2026-11-17 or 2026-11-17-k1")
    source = (dest_root / (source_rel or f"{COACHING_SLIDES_REL}/{playlist_id}")).resolve()
    if not (source / "index.html").is_file():
        raise CompileError(f"no published master deck at {source}")
    target = (dest_root / DELIVERED_REL / playlist_id / label).resolve()
    if not target.is_relative_to(dest_root.resolve()):
        raise CompileError("frozen copy escapes the coaching-slides checkout")
    check_publish_overlap(source, target)
    marker = target / "FROZEN.json"
    history: list[str] = []
    if target.exists():
        if not replace:
            raise CompileError(f"{target} is frozen. Replace it only when Byron asks: --replace")
        if not marker.is_file():
            raise CompileError(f"{target} exists but is not a frozen copy")
        previous = load_json(marker)
        history = [*previous.get("replaced", []), previous.get("frozen_on", "")]
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("FROZEN.json", ".git"))
    qr_opens = point_qr_at_copy(target, source_url=public_url(playlist_id) if not source_rel else None, copy_url=frozen_url(playlist_id, label))
    manifest = source / "manifest.json"
    from datetime import date
    record = {
        "deck": playlist_id,
        "label": label,
        "frozen_on": today or date.today().isoformat(),
        "copied_from": str(source.relative_to(dest_root.resolve())) + "/",
        "master_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.is_file() else None,
        "replaced": [h for h in history if h],
        "qr_opens": qr_opens,
        "rule": "Frozen after delivery. Rebuilds and publishes never touch it. Replace only when Byron asks.",
    }
    marker.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return target


def point_qr_at_copy(target: Path, source_url: str | None, copy_url: str) -> str | None:
    """Make the deck's own QR code open the frozen copy instead of the live master."""
    page = target / "index.html"
    text = page.read_text(encoding="utf-8")
    sections = re.findall(r'<section\b[^>]*data-deck-qr="true"[^>]*>.*?</section>', text, re.S)
    if not sections:
        return None
    if not (target / DECK_QR).is_file():
        raise CompileError("the deck has a QR slide but no QR image to rewrite")
    old = source_url
    if old is None:
        found = re.search(r'alt="QR code that opens these slides at ([^"]+)\."', sections[0])
        if not found:
            raise CompileError("cannot find the address the QR slide shows")
        old = "https://" + html.unescape(found.group(1)) + "/"  # the page holds the address escaped
    write_deck_qr(target, copy_url)
    for section in sections:
        new = section.replace(escape(deck_qr_alt(old)), escape(deck_qr_alt(copy_url))).replace(escape(display_url(old)), escape(display_url(copy_url)))
        if new == section:
            raise CompileError("the QR slide does not show the master address it should")
        text = text.replace(section, new, 1)
    page.write_text(text, encoding="utf-8")
    return copy_url


def frozen_url(playlist_id: str, label: str) -> str:
    return f"{PUBLIC_PAGES_ROOT}/{DELIVERED_REL}/{playlist_id}/{label}/"


def list_playlists() -> list[str]:
    return sorted(path.stem for path in PLAYLISTS.glob("*.json"))


def build_compile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile a Metronomics playlist onto the shared house shell."
    )
    parser.add_argument(
        "playlist",
        nargs="?",
        default="kickoff",
        help="Playlist id under metronomics/playlists/ (default: kickoff)",
    )
    parser.add_argument("--playlist-file", type=Path, help="Explicit local playlist JSON; source paths are relative to this file")
    parser.add_argument(
        "--out",
        type=Path,
        help="Compile output directory (default: metronomics/compiled/<playlist>)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run shared/check-shell.py --deck on the compiled output",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List playlist ids and exit",
    )
    parser.add_argument(
        "--fail-on-dropped-text",
        action="store_true",
        help="Fail the build when a slide carries text its layout cannot show (default: warn)",
    )
    return parser


def build_publish_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy a compiled Metronomics deck into a coaching-slides checkout."
    )
    parser.add_argument("--playlist", default="kickoff", help="Playlist id to publish")
    parser.add_argument(
        "--dest",
        type=Path,
        required=True,
        help="Path to a local ByronDarlison/coaching-slides checkout",
    )
    parser.add_argument(
        "--from",
        dest="from_dir",
        type=Path,
        help="Existing compiled deck to copy (default: compile first)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the copy plan without writing",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run shared/check-shell.py --deck on the compiled output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    try:
        if raw and raw[0] == "impact":
            parser = argparse.ArgumentParser(description="List the master decks a slide-library change alters.")
            parser.add_argument("--base", default="origin/main", help="Git ref to compare against (default: origin/main)")
            parser.add_argument("--json", action="store_true", help="Print the report as JSON")
            args = parser.parse_args(raw[1:])
            rows = impact_report(args.base)
            if args.json:
                print(json.dumps(rows, indent=2))
            else:
                print_impact(rows, args.base)
            return 0
        if raw and raw[0] == "freeze":
            parser = argparse.ArgumentParser(description="Freeze the delivered copy of a published master deck.")
            parser.add_argument("--deck", required=True, help="Deck id, for example kickoff")
            parser.add_argument("--label", required=True, help="Delivery date plus optional short code, for example 2026-11-17-k1")
            parser.add_argument("--dest", type=Path, required=True, help="Path to a local ByronDarlison/coaching-slides checkout")
            parser.add_argument("--source", help="Master folder inside coaching-slides (default: metronomics/<deck>)")
            parser.add_argument("--replace", action="store_true", help="Replace an existing frozen copy. Only when Byron asks.")
            args = parser.parse_args(raw[1:])
            target = freeze_copy(args.dest, args.deck, args.label, args.replace, args.source)
            print(f"Frozen {args.deck} -> {target}")
            print(f"Public URL after Pages publish: {frozen_url(args.deck, args.label)}")
            return 0
        if raw and raw[0] == "publish":
            args = build_publish_parser().parse_args(raw[1:])
            playlist_id = identifier(args.playlist, "playlist id")
            if args.dry_run and not args.from_dir:
                resolve_playlist(load_playlist(playlist_id))
                copy_publish(COMPILED / playlist_id, args.dest, playlist_id, True)
                return 0
            deck = args.from_dir or compile_playlist(playlist_id)
            if args.from_dir and not (deck / "index.html").is_file():
                raise CompileError(f"compiled deck missing index.html: {deck}")
            if args.check:
                status = run_check_shell(deck)
                if status:
                    return status
            copy_publish(deck, args.dest, playlist_id, args.dry_run)
            return 0
        args = build_compile_parser().parse_args(raw)
        if args.list:
            for name in list_playlists():
                print(name)
            return 0
        dest = compile_playlist(args.playlist, args.out, args.playlist_file, args.fail_on_dropped_text)
        playlist = load_playlist_file(args.playlist_file) if args.playlist_file else load_playlist(args.playlist)
        units = resolve_playlist(playlist)
        print(f"Compiled {playlist['id']} -> {dest}")
        print(f"Resolved {len(units)} unit ids: {', '.join(unit['id'] for unit in units)}")
        print(f"Shell assets: {', '.join(SHELL_FILES)} and fonts/")
        print(f"Documented public URL: {public_url(playlist['id'])}")
        if args.check:
            return run_check_shell(dest)
        return 0
    except CompileError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

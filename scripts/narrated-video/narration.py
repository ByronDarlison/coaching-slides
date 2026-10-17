"""Narration extraction and deck fingerprints for narrated slide videos.

A narrated deck is any tracked ``index.html`` (outside ``tests/`` and
``node_modules/``, and not the repository landing page) with at least one
``aside.speaker-notes`` inside a ``section.slide``.

Spoken text for a slide is its ``aside.video-script`` when it has one;
otherwise its speaker notes up to the facilitator marker ``In the room:``.
The pronunciation list is applied either way. A slide marked
``data-narration="skip"`` is left out of the video.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

FORMAT_VERSION = 1
MAX_SLIDE_CHARS = 5000
FACILITATOR_MARKER = "In the room:"
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
PRONUNCIATIONS = HERE / "pronunciations.json"


class NarrationError(Exception):
    pass


VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "area", "base", "col", "embed", "track"}


class _DeckParser(HTMLParser):
    """Collects, per section.slide: id, skip flag, and paragraphs of each direct-child notes aside."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides: list[dict] = []
        self.stack: list[tuple[str, str]] = []  # (tag, role)
        self.current: dict | None = None
        self.in_notes = False
        self.notes_key = "notes"
        self.notes_depth = 0
        self.paragraph: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        role = ""
        if tag == "section" and "slide" in classes:
            if self.current is not None:
                raise NarrationError("nested slide sections")
            self.current = {"id": a.get("id"), "skip": a.get("data-narration") == "skip", "notes": [], "script": []}
            self.slides.append(self.current)
            role = "slide"
        elif tag == "aside" and ("speaker-notes" in classes or "video-script" in classes) and self.current is not None:
            self.notes_key = "script" if "video-script" in classes else "notes"
            self.current[self.notes_key].append([])
            self.in_notes = True
            self.notes_depth = len(self.stack) + 1
            role = "notes"
        elif tag == "p" and self.in_notes:
            self.paragraph = []
            role = "p"
        if tag not in VOID:
            self.stack.append((tag, role))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not any(open_tag == tag for open_tag, _ in self.stack):
            return  # stray close tag: ignore rather than unwind the stack
        while self.stack:
            open_tag, role = self.stack.pop()
            if role == "p" and self.paragraph is not None:
                text = re.sub(r"\s+", " ", "".join(self.paragraph)).strip()
                if text:
                    self.current[self.notes_key][-1].append(text)
                self.paragraph = None
            elif role == "notes":
                self.in_notes = False
            elif role == "slide":
                self.current = None
            if open_tag == tag:
                break

    def handle_data(self, data):
        if self.paragraph is not None:
            self.paragraph.append(data)


def load_pronunciations(path: Path = PRONUNCIATIONS) -> list[dict]:
    entries = json.loads(path.read_text())
    for e in entries:
        if not isinstance(e.get("term"), str) or not isinstance(e.get("say"), str) or not e["term"]:
            raise NarrationError("bad pronunciation entry")
    return sorted(entries, key=lambda e: len(e["term"]), reverse=True)


def apply_pronunciations(text: str, entries: list[dict]) -> str:
    if not entries:
        return text
    lookup = {e["term"]: e["say"] for e in entries}
    pattern = re.compile(
        r"(?<![A-Za-z0-9])(" + "|".join(re.escape(e["term"]) for e in entries) + r")(?![A-Za-z0-9])")
    return pattern.sub(lambda m: lookup[m.group(1)], text)


def spoken_text(paragraphs: list[str], entries: list[dict]) -> str:
    text = "\n\n".join(paragraphs)
    cut = text.find(FACILITATOR_MARKER)
    if cut != -1:
        text = text[:cut]
    text = text.strip()
    return apply_pronunciations(text, entries) if text else ""


def extract(index_html: str, entries: list[dict] | None = None) -> list[dict]:
    """Returns [{slide: N, text: str}] for every narrated slide, in order."""
    entries = load_pronunciations() if entries is None else entries
    parser = _DeckParser()
    parser.feed(index_html)
    parser.close()
    out = []
    for n, slide in enumerate(parser.slides, start=1):
        if slide["id"] != f"slide-{n}":
            raise NarrationError(f"slide {n} has id {slide['id']!r}, expected slide-{n}")
        if len(slide["notes"]) > 1:
            raise NarrationError(f"slide {n} has more than one speaker-notes block")
        if len(slide["script"]) > 1:
            raise NarrationError(f"slide {n} has more than one video-script block")
        if slide["skip"]:
            continue
        if slide["script"]:
            text = "\n\n".join(slide["script"][0]).strip()
            text = apply_pronunciations(text, entries) if text else ""
        elif slide["notes"]:
            text = spoken_text(slide["notes"][0], entries)
        else:
            continue
        if not text:
            continue
        if len(text) > MAX_SLIDE_CHARS:
            raise NarrationError(f"slide {n} narration exceeds {MAX_SLIDE_CHARS} characters")
        out.append({"slide": n, "text": text})
    return out


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def discover(cwd: Path = REPO_ROOT) -> list[str]:
    """Deck directories (repo-relative, '/' separated) that carry speaker notes."""
    decks = []
    for path in git("ls-files", "*index.html", cwd=cwd).splitlines():
        p = Path(path)
        if p.name != "index.html" or len(p.parts) < 2:
            continue
        if p.parts[0] in ("tests", "node_modules") or "node_modules" in p.parts:
            continue
        text = (cwd / p).read_text(encoding="utf-8")
        if re.search(r"<aside\b[^>]*class=\"[^\"]*\bspeaker-notes\b", text) and \
           re.search(r"<section\b[^>]*class=\"[^\"]*\bslide\b", text):
            decks.append(str(p.parent.as_posix()))
    return sorted(decks)


def check_self_contained(deck: str, cwd: Path = REPO_ROOT) -> None:
    text = (cwd / deck / "index.html").read_text(encoding="utf-8")
    if re.search(r"""(?:src|href)\s*=\s*["']\.\./""", text):
        raise NarrationError(f"{deck} references files outside its folder")


def deck_files(deck: str, cwd: Path = REPO_ROOT) -> list[list[str]]:
    rows = []
    for line in git("ls-tree", "-r", "HEAD", "--", f"{deck}/", cwd=cwd).splitlines():
        meta, path = line.split("\t", 1)
        if path.endswith(".md"):
            continue
        rows.append([path, meta.split()[2]])
    return sorted(rows)


def fingerprint(deck: str, narration: list[dict], settings: dict, files: list[list[str]]) -> str:
    payload = {
        "format_version": FORMAT_VERSION,
        "voice_id": settings["voice_id"], "model_id": settings["model_id"],
        "output_format": settings["output_format"],
        "deck_path": deck,
        "narration": [[n["slide"], n["text"]] for n in narration],
        "files": files,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def video_name(deck: str, date: str, commit: str) -> str:
    return f"{deck.replace('/', '-')}-{date}-{commit[:7]}.mp4"

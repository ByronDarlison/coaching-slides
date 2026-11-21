#!/usr/bin/env python3
"""Check the shared slideshow shell against the house visual standard."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DECK = ROOT / "deck"
STANDARD_PATH = ROOT.parent / "SLIDE-VISUAL-STANDARD.md"

REQUIRED_CSS = (
    "#1b1f24",
    "#f6f4ef",
    "#ffffff",
    "#326ab6",
    "#326ab5",
    "#54b570",
    "#a94f1f",
    "clamp(24px, 2.4vh, 37px)",
    "1180px",
    "44px",
    "aspect-ratio: 16 / 9",
    'font-family: "Geist"',
    'font-family: "Geist Mono"',
    'url("./fonts/geist-latin.woff2")',
    'url("./fonts/geist-mono-latin.woff2")',
)
REQUIRED_HTML = (
    'href="./shell.css"',
    'src="./shell.js"',
    'href="./fonts/geist-latin.woff2"',
    'href="./fonts/geist-mono-latin.woff2"',
    "speaker-notes",
    "data-title",
    "data-group",
)
SAMPLE_LAYOUT_HTML = (
    "comp-story",
    "comp-causal",
    "comp-decision",
    "comp-rule",
)
# A deck that uses one of these layouts needs the shell styles and behaviour for it.
LAYOUT_SHELL_TOKENS = {
    'class="slide about-timeline"': (("css", ".timeline-list"), ("css", ".timeline-item.active"), ("js", "setupTimeline")),
    'class="slide comp-attempts"': (("css", ".attempts-grid"), ("css", ".attempt--win")),
    'class="slide comp-figure"': (("css", ".figure-svg"),),
}
REMOTE_FONT_HOSTS = (
    "fonts.googleapis",
    "fonts.gstatic",
    "use.typekit",
    "cdn.jsdelivr",
    "unpkg.com",
    "fontshare",
)
FONT_FILES = (
    "geist-latin.woff2",
    "geist-mono-latin.woff2",
    "LICENSE.txt",
)


def check_deck(deck: Path, standard_text: str) -> list[str]:
    """Return failure strings for one deck folder that uses the shared shell."""
    failures: list[str] = []
    css_path = deck / "shell.css"
    html_path = deck / "index.html"
    js_path = deck / "shell.js"
    if not css_path.is_file():
        return [f"missing {css_path}"]
    if not html_path.is_file():
        return [f"missing {html_path}"]
    if not js_path.is_file():
        return [f"missing {js_path}"]
    css = css_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")
    bundle = css + "\n" + html + "\n" + js
    for token in REQUIRED_CSS:
        if token not in css:
            failures.append(f"shell.css missing {token}")
    for token in REQUIRED_HTML:
        if token not in html:
            failures.append(f"index.html missing {token}")
    if deck.resolve() == DECK.resolve():
        for token in SAMPLE_LAYOUT_HTML:
            if token not in html:
                failures.append(f"index.html missing {token}")
    for marker, tokens in LAYOUT_SHELL_TOKENS.items():
        if marker in html:
            for kind, token in tokens:
                if token not in (css if kind == "css" else js):
                    failures.append(f"shell.{kind} missing {token} for {marker}")
    lowered = bundle.lower()
    for host in REMOTE_FONT_HOSTS:
        if host in lowered:
            failures.append(f"remote font host found: {host}")
    if "http://" in lowered or "https://" in lowered:
        failures.append("deck source requests a network URL")
    if "brand-line" in bundle:
        failures.append("brand-line chrome is present")
    em_dash = chr(0x2014)
    if em_dash in bundle or em_dash in standard_text:
        failures.append("em dash found in the shell or visual standard")
    if "shared/README.md" not in standard_text:
        failures.append("visual standard does not point at the shared shell")
    for name in FONT_FILES:
        path = deck / "fonts" / name
        if not path.is_file() or path.stat().st_size < 1000:
            failures.append(f"font bundle missing or too small: {name}")
    return failures


def parse_args(argv: list[str]) -> Path:
    if not argv:
        return DECK
    if argv[0] in {"-h", "--help"}:
        print("Usage: check-shell.py [--deck PATH]")
        print("Default PATH is source/shared/deck")
        raise SystemExit(0)
    if argv[0] == "--deck":
        if len(argv) < 2:
            print("Usage: check-shell.py [--deck PATH]", file=sys.stderr)
            raise SystemExit(2)
        return Path(argv[1]).resolve()
    print("Usage: check-shell.py [--deck PATH]", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    deck = parse_args(sys.argv[1:])
    standard = STANDARD_PATH.read_text(encoding="utf-8")
    failures = check_deck(deck, standard)
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    if deck.resolve() == DECK.resolve():
        print("PASS: shared slideshow shell")
    else:
        print(f"PASS: slideshow shell {deck}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

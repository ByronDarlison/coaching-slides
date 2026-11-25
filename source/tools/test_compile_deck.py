#!/usr/bin/env python3
"""Compile-deck smoke: resolve unit ids, emit a shell-backed kickoff deck."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
PRESENTATIONS = TOOLS.parent
COMPILE = TOOLS / "compile_deck.py"
CHECK_SHELL = PRESENTATIONS / "shared" / "check-shell.py"

sys.path.insert(0, str(TOOLS))
import compile_deck  # noqa: E402


def test_kickoff_playlist_units_resolve() -> None:
    playlist = compile_deck.load_playlist("kickoff")
    units = compile_deck.resolve_playlist(playlist)
    ids = [unit["id"] for unit in units]
    assert ids
    assert ids == [
        entry if isinstance(entry, str) else entry["id"]
        for entry in playlist["units"]
    ]
    assert ids == ["blank-template"]
    assert all(unit.get("tags") for unit in units)


def test_unknown_unit_fails_closed(tmp_path: Path) -> None:
    playlist = tmp_path / "broken.json"
    playlist.write_text(
        json.dumps({"id": "broken", "units": ["no-such-unit"]}) + "\n",
        encoding="utf-8",
    )
    original = compile_deck.PLAYLISTS
    try:
        compile_deck.PLAYLISTS = tmp_path
        with pytest.raises(compile_deck.CompileError, match="missing file"):
            compile_deck.resolve_playlist(compile_deck.load_playlist("broken"))
    finally:
        compile_deck.PLAYLISTS = original


def test_override_cannot_change_id() -> None:
    playlist = {
        "id": "kickoff",
        "units": [{"id": "blank-template", "override": {"id": "other"}}],
    }
    with pytest.raises(compile_deck.CompileError, match="cannot change a unit id"):
        compile_deck.resolve_playlist(playlist)


def test_compile_kickoff_loads_shell(tmp_path: Path) -> None:
    dest = tmp_path / "kickoff"
    result = subprocess.run(
        [sys.executable, str(COMPILE), "kickoff", "--out", str(dest), "--check"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    html = (dest / "index.html").read_text(encoding="utf-8")
    assert 'href="./shell.css"' in html
    assert 'src="./shell.js"' in html
    assert 'href="./fonts/geist-latin.woff2"' in html
    assert (dest / "shell.css").is_file()
    assert (dest / "shell.js").is_file()
    assert (dest / "fonts" / "geist-latin.woff2").is_file()
    assert 'data-unit="blank-template"' in html
    assert html.count("<section class=\"slide") == 1
    assert "brand-line" not in html
    assert "brand-line" not in (dest / "shell.css").read_text(encoding="utf-8")
    assert "http://" not in html.lower()
    assert "https://" not in html.lower()
    assert "PASS: slideshow shell" in result.stdout
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["public_path"] == "metronomics/kickoff/"
    assert manifest["public_url"].endswith("/coaching-slides/metronomics/kickoff/")
    assert manifest["unit_ids"] == ["blank-template"]
    assert 'data-title=""' in html
    invented = (
        "Kickoff",
        "Kick Off",
        "Metronomics Kickoff",
        "Metronomics kickoff",
        "Intros with functional questions",
        "Open with intros",
        "Good News",
        "People and culture",
        "Session ritual",
        'data-group="Human"',
        'data-group="Cultural"',
        'data-group="Session"',
        "Gut out the",
        "Map how work flows",
    )
    for phrase in invented:
        assert phrase not in html, phrase
    assert "<p class=\"eyebrow\">" not in html
    assert "<h1 class=\"slide-title\">" not in html
    assert "<h1 class=\"story-title\">" not in html
    assert "<h1>Metronomics" not in html


def test_check_shell_default_still_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECK_SHELL)],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "PASS: shared slideshow shell"


def test_publish_dry_run(tmp_path: Path) -> None:
    dest = tmp_path / "coaching-slides"
    result = subprocess.run(
        [
            sys.executable,
            str(COMPILE),
            "publish",
            "--dest",
            str(dest),
            "--dry-run",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "metronomics/kickoff" in result.stdout
    assert not dest.exists()


def test_numbered_panels_render_as_green_to_blue_sequence() -> None:
    unit = {"id": "seq", "layout": "comp-decision", "title": "T", "headline": "H",
            "panels": [{"role": "01", "heading": "A", "support": "a", "mark": "structure"},
                       {"role": "02", "heading": "B", "support": "b", "mark": "action"},
                       {"role": "03", "heading": "C", "support": "c", "mark": "structure"}]}
    html = compile_deck.render_slide(unit, 1)
    assert 'class="stack-3 seq seq-3"' in html
    assert '<span class="step">1</span>A' in html
    assert 'class="role"' not in html


def test_labelled_panels_keep_meaning_colours() -> None:
    unit = {"id": "lab", "layout": "comp-decision", "title": "T", "headline": "H",
            "panels": [{"role": "Achievable", "heading": "A", "support": "a", "mark": "structure"},
                       {"role": "Realistic", "heading": "B", "support": "b", "mark": "action"}]}
    html = compile_deck.render_slide(unit, 1)
    assert " seq" not in html
    assert '<p class="role">Achievable</p>' in html


def test_numbered_roles_with_labels_render_sequence_and_keep_labels() -> None:
    dot = "\u00b7"
    roles = [f"01 {dot} Marketing {dot} Chris", f"02 {dot} Sales {dot} Andrew",
             f"03 {dot} Operations {dot} Jen", f"04 {dot} Controller {dot} Allison"]
    unit = {"id": "seats", "layout": "comp-decision", "title": "T", "headline": "H",
            "panels": [{"role": role, "heading": f"H{i}", "support": "s", "mark": "structure"}
                       for i, role in enumerate(roles, 1)]}
    html = compile_deck.render_slide(unit, 1)
    assert 'class="meet-grid seq seq-4"' in html
    for i, label in enumerate([f"Marketing {dot} Chris", f"Sales {dot} Andrew",
                               f"Operations {dot} Jen", f"Controller {dot} Allison"], 1):
        assert f'<p class="role">{label}</p><h2><span class="step">{i}</span>H{i}</h2>' in html


@pytest.mark.parametrize("text", ["a \u2013 b", "a \u2014 b", "a &ndash; b", "a &#8211; b", "a &mdash; b", "a &#x2014; b"])
def test_dash_gate_rejects_literal_and_entity_dashes(text: str) -> None:
    with pytest.raises(compile_deck.CompileError, match="em or en dash"):
        compile_deck.check_no_dashes(f"<p>{text}</p>")


def test_dash_gate_allows_plain_hyphen() -> None:
    compile_deck.check_no_dashes("<p>a - b</p>")


def test_publish_rejects_path_like_playlist_id(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    deck = tmp_path / "deck"
    deck.mkdir()
    (deck / "index.html").write_text("<html></html>", encoding="utf-8")
    dest = tmp_path / "slides"
    code = compile_deck.main(["publish", "--playlist", "../../elsewhere", "--from", str(deck), "--dest", str(dest)])
    assert code == 1
    assert "invalid playlist id" in capsys.readouterr().err
    assert not dest.exists()


def test_publish_check_failure_stops_before_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    deck = tmp_path / "deck"
    deck.mkdir()
    (deck / "index.html").write_text("<html></html>", encoding="utf-8")
    dest = tmp_path / "slides"
    calls: list[Path] = []

    def failing_check(path: Path) -> int:
        calls.append(path)
        return 3

    monkeypatch.setattr(compile_deck, "run_check_shell", failing_check)
    code = compile_deck.main(["publish", "--playlist", "kickoff", "--from", str(deck), "--dest", str(dest), "--check"])
    assert code == 3
    assert calls == [deck]
    assert not dest.exists()


def test_publish_check_success_then_copies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    deck = tmp_path / "deck"
    deck.mkdir()
    (deck / "index.html").write_text("<html></html>", encoding="utf-8")
    dest = tmp_path / "slides"
    monkeypatch.setattr(compile_deck, "run_check_shell", lambda path: 0)
    code = compile_deck.main(["publish", "--playlist", "kickoff", "--from", str(deck), "--dest", str(dest), "--check"])
    assert code == 0
    assert (dest / "metronomics" / "kickoff" / "index.html").is_file()


def test_publish_rejects_same_source_and_target(tmp_path: Path) -> None:
    dest_root = tmp_path / "slides"
    target = dest_root / "metronomics" / "kickoff"
    target.mkdir(parents=True)
    (target / "index.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(compile_deck.CompileError, match="overlap"):
        compile_deck.copy_publish(target, dest_root, "kickoff", False)
    assert (target / "index.html").is_file()


def test_publish_rejects_source_inside_target(tmp_path: Path) -> None:
    dest_root = tmp_path / "slides"
    deck = dest_root / "metronomics" / "kickoff" / "nested"
    deck.mkdir(parents=True)
    (deck / "index.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(compile_deck.CompileError, match="overlap"):
        compile_deck.copy_publish(deck, dest_root, "kickoff", False)
    assert (deck / "index.html").is_file()


def test_publish_rejects_target_inside_source(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    deck.mkdir()
    (deck / "index.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(compile_deck.CompileError, match="overlap"):
        compile_deck.copy_publish(deck, deck, "kickoff", False)
    assert (deck / "index.html").is_file()


# About Me layouts.

KICKOFF_PLAYLIST = PRESENTATIONS / "playlists" / "kickoff.json"


def _library(tmp_path: Path, slide: dict, files: dict[str, bytes | str]) -> Path:
    lib = tmp_path / "lib"
    for name, data in files.items():
        target = lib / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            target.write_text(data, encoding="utf-8")
        else:
            target.write_bytes(data)
    (lib / "unit.json").write_text(json.dumps({"id": "unit", "tags": ["t"], "slides": [slide]}), encoding="utf-8")
    playlist = tmp_path / "playlist.json"
    playlist.write_text(json.dumps({"id": "about", "sources": {"lib": "lib"}, "units": ["lib:unit"]}), encoding="utf-8")
    return playlist


PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0,0 L10,10" class="fig-line"/></svg>\n'


def _timeline_slide(**extra: object) -> dict:
    slide = {"id": "me", "layout": "about-timeline", "title": "T", "headline": "Name", "eyebrow": "About me",
             "role": "Coach", "body": ["Line one."],
             "timeline": [
                 {"year": 1962, "age": 0, "text": "Born", "kind": "logo", "media": [{"src": "a/map.png", "alt": "Map"}]},
                 {"year": 1981, "age": 19, "text": "Photo", "kind": "photo", "portrait": True, "media": [{"src": "a/me.png", "alt": "Me"}]},
                 {"year": 2017, "age": 55, "text": "Two", "kind": "logo", "media": [{"src": "a/map.png", "alt": "One"}, {"src": "a/b.png", "alt": "Two"}]},
                 {"year": 1997, "age": 35, "text": "Drawn", "kind": "illustration", "media": [{"src": "a/b.png", "alt": "Drawing"}]},
             ]}
    slide.update(extra)
    return slide


def test_about_timeline_renders_rows_and_bundles_images(tmp_path: Path) -> None:
    files = {"a/map.png": PNG, "a/me.png": PNG + b"1", "a/b.png": PNG + b"2"}
    playlist = _library(tmp_path, _timeline_slide(), files)
    out = compile_deck.compile_playlist("about", tmp_path / "out", playlist)
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'class="slide about-timeline"' in html
    assert '<p class="identity-role">Coach</p>' in html
    assert html.count('class="timeline-item"') == 4
    assert 'class="timeline-media timeline-photo timeline-portrait"' in html
    assert 'class="timeline-media timeline-logo timeline-logo--two"' in html
    assert 'class="timeline-media timeline-logo timeline-logo--illus"' in html
    assert '<span class="timeline-age">age 19</span>' in html
    import re
    srcs = re.findall(r'<img src="\./([^"]+)"', html)
    assert len(srcs) == 5 and all((out / s).is_file() for s in srcs)
    assert "a/map.png" not in html


@pytest.mark.parametrize("row", [
    {"year": 1, "text": "x", "media": [{"src": "a/map.png", "alt": ""}]},
    {"year": 1, "text": "x", "media": []},
    {"year": 1, "text": "x", "kind": "video", "media": [{"src": "a/map.png", "alt": "M"}]},
    {"year": 1, "text": "x", "media": [{"src": "../escape.png", "alt": "M"}]},
    {"year": 1, "text": "", "media": [{"src": "a/map.png", "alt": "M"}]},
])
def test_about_timeline_rejects_bad_rows(tmp_path: Path, row: dict) -> None:
    (tmp_path / "escape.png").write_bytes(PNG)
    playlist = _library(tmp_path, _timeline_slide(timeline=[row]), {"a/map.png": PNG})
    with pytest.raises(compile_deck.CompileError):
        compile_deck.compile_playlist("about", tmp_path / "out", playlist)


def test_comp_attempts_renders_numbered_cards_win_and_accent() -> None:
    unit = {"id": "tries", "layout": "comp-attempts", "title": "T", "headline": "I tried four times.",
            "headline_accent": "One worked.",
            "attempts": [{"year": "1996", "heading": "A", "support": "a", "outcome": "Failed"},
                         {"year": "2018", "heading": "B", "support": "b", "outcome": "Won", "win": True}]}
    html = compile_deck.render_slide(unit, 1)
    assert 'I tried four times. <span class="title-accent">One worked.</span></h1>' in html
    assert 'class="attempts-grid attempts-2"' in html
    assert '<span class="attempt-badge">1</span>1996' in html
    assert '<article class="attempt attempt--win"><span class="attempt-year"><span class="attempt-badge">2</span>2018' in html
    assert html.count('class="attempt"') == 1


@pytest.mark.parametrize("attempts", [[], [{"heading": str(i)} for i in range(5)], [{"year": "1"}]])
def test_comp_attempts_rejects_bad_counts_and_missing_headings(attempts: list) -> None:
    unit = {"id": "tries", "layout": "comp-attempts", "title": "T", "headline": "H", "attempts": attempts}
    with pytest.raises(compile_deck.CompileError):
        compile_deck.render_slide(unit, 1)


def _figure_slide() -> dict:
    return {"id": "fig", "layout": "comp-figure", "title": "T", "headline": "Flat.", "headline_accent": "Up.",
            "figure": {"src": "fig.svg", "alt": "A line that turns up"}}


def test_comp_figure_inlines_svg_without_network_references(tmp_path: Path) -> None:
    playlist = _library(tmp_path, _figure_slide(), {"fig.svg": SVG})
    out = compile_deck.compile_playlist("about", tmp_path / "out", playlist)
    html = (out / "index.html").read_text(encoding="utf-8")
    assert '<svg class="figure-svg" role="img" aria-label="A line that turns up" viewBox="0 0 10 10">' in html
    assert "xmlns" not in html and "http" not in html.lower().replace("http-equiv", "")
    assert 'Flat. <span class="title-accent">Up.</span>' in html


@pytest.mark.parametrize("svg", [
    '<svg><script>alert(1)</script></svg>',
    '<svg onload="x()"><path/></svg>',
    '<svg><image href="a.png"/></svg>',
    '<svg><a xlink:href="https://example.com"><path/></a></svg>',
    '<svg><style>path{fill:red}</style></svg>',
    '<svg><foreignObject></foreignObject></svg>',
    '<svg><path fill="url(#g)"/></svg>',
    '<svg><path/></svg><svg></svg>',
    '<div></div>',
])
def test_comp_figure_refuses_unsafe_svg(tmp_path: Path, svg: str) -> None:
    playlist = _library(tmp_path, _figure_slide(), {"fig.svg": svg})
    with pytest.raises(compile_deck.CompileError):
        compile_deck.compile_playlist("about", tmp_path / "out", playlist)


def test_comp_figure_needs_alt_and_svg_file(tmp_path: Path) -> None:
    slide = _figure_slide()
    slide["figure"] = {"src": "fig.png", "alt": "x"}
    playlist = _library(tmp_path, slide, {"fig.png": PNG})
    with pytest.raises(compile_deck.CompileError):
        compile_deck.compile_playlist("about", tmp_path / "out", playlist)
    slide["figure"] = {"src": "fig.svg", "alt": ""}
    playlist = _library(tmp_path, slide, {"fig.svg": SVG})
    with pytest.raises(compile_deck.CompileError):
        compile_deck.compile_playlist("about", tmp_path / "out", playlist)


def test_kickoff_opens_with_about_me_slides_and_compiles(tmp_path: Path) -> None:
    playlist = compile_deck.load_playlist_file(KICKOFF_PLAYLIST)
    units = compile_deck.resolve_playlist(playlist)
    ids = [unit["id"] for unit in units]
    assert len(ids) == 77
    assert ids[-1] == "deck-link"
    assert ids[:4] == ["welcome", "byron", "scaling-tries", "good-news"]
    assert "journey" not in ids
    timeline = units[1]
    assert timeline["layout"] == "about-timeline" and len(timeline["timeline"]) == 67
    out = compile_deck.compile_playlist("kickoff", tmp_path / "kickoff", KICKOFF_PLAYLIST)
    html = (out / "index.html").read_text(encoding="utf-8")
    assert "Now I coach founders to do in 3 years what took me 33." in html
    assert html.count("Metronomics Coach") >= 2
    import re
    assert all((out / s).is_file() for s in re.findall(r'<img[^>]*src="\./([^"]+)"', html))


def test_check_shell_requires_styles_for_new_layouts(tmp_path: Path) -> None:
    playlist = _library(tmp_path, _figure_slide(), {"fig.svg": SVG})
    out = compile_deck.compile_playlist("about", tmp_path / "out", playlist)
    assert subprocess.run([sys.executable, str(CHECK_SHELL), "--deck", str(out)], check=False).returncode == 0
    css = out / "shell.css"
    css.write_text(css.read_text(encoding="utf-8").replace(".figure-svg", ".figure-x"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(CHECK_SHELL), "--deck", str(out)], check=False, capture_output=True, text=True)
    assert result.returncode == 1 and ".figure-svg" in result.stdout


def test_support_emphasis_highlights_and_escapes() -> None:
    html = compile_deck.support_paragraphs({"support": "One **owner** <b>x</b>."})
    assert '<strong class="hl">owner</strong>' in html and "&lt;b&gt;" in html


def test_hotspots_wrap_artwork_and_escape():
    hotspot_wrap, CompileError = compile_deck.hotspot_wrap, compile_deck.CompileError
    html = hotspot_wrap('<img src="./a.svg" alt="x">', {"viewbox": [1000, 500], "hotspots": [{"x": 100, "y": 50, "w": 200, "h": 100, "term": "Known <for>", "tip": "What people think."}]})
    assert 'class="art-hot"' in html and "left:10.000%" in html and "top:10.000%" in html and "hotspot--below" in html
    assert "Known &lt;for&gt;" in html and "<for>" not in html
    with pytest.raises(CompileError):
        hotspot_wrap("<img>", {"hotspots": [{"x": 1, "y": 1, "w": 1, "h": 1, "term": "a", "tip": "b"}]})


# --- Single-source slides (Byron, 16-Nov-2026) -------------------------------

KICKOFF_FILE = compile_deck.PRESENTATIONS / "playlists" / "kickoff.json"


def kickoff_slides() -> list[dict]:
    return compile_deck.resolve_playlist(compile_deck.load_playlist_file(KICKOFF_FILE))


def test_every_slide_gets_a_unique_readable_name() -> None:
    slides = kickoff_slides()
    names = [s["_name"] for s in slides]
    assert len(names) == len(set(names))
    assert names[0] == "opening-welcome"
    assert all(re.fullmatch(r"[a-z0-9-]+", n) for n in names)
    assert not any(re.fullmatch(r"slide-\d+", n) for n in names)


def test_a_repeated_slide_gets_a_numbered_name() -> None:
    slides = [{"_source": "kickoff:opening#good-news"}, {"_source": "kickoff:opening#good-news"}, {"_source": "kickoff:bhag#bhag"}]
    names = [s["_name"] for s in compile_deck.assign_names(slides)]
    assert names == ["opening-good-news", "opening-good-news-2", "bhag"]


def test_names_reach_the_html_and_manifest(tmp_path: Path) -> None:
    dest = compile_deck.compile_playlist("kickoff", tmp_path / "deck", KICKOFF_FILE)
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    html_text = (dest / "index.html").read_text(encoding="utf-8")
    assert manifest["slides"][0] == {"number": 1, "name": "opening-welcome", "reference": "kickoff:opening#welcome"}
    assert len(manifest["slides"]) == len(manifest["unit_ids"])
    assert 'id="slide-1" data-name="opening-welcome"' in html_text


def published_master(root: Path) -> Path:
    master = root / "metronomics" / "kickoff"
    master.mkdir(parents=True)
    (master / "index.html").write_text("<html>v1</html>", encoding="utf-8")
    (master / "manifest.json").write_text('{"generator": "darlison-slides"}', encoding="utf-8")
    return master


def test_freeze_copies_the_master_once(tmp_path: Path) -> None:
    master = published_master(tmp_path)
    target = compile_deck.freeze_copy(tmp_path, "kickoff", "2026-11-17-k1", False, today="2026-11-17")
    assert target == (tmp_path / "delivered" / "kickoff" / "2026-11-17-k1").resolve()
    assert (target / "index.html").read_text(encoding="utf-8") == "<html>v1</html>"
    record = json.loads((target / "FROZEN.json").read_text(encoding="utf-8"))
    assert record["frozen_on"] == "2026-11-17" and record["replaced"] == []
    # The master moves on; the frozen copy does not.
    (master / "index.html").write_text("<html>v2</html>", encoding="utf-8")
    with pytest.raises(compile_deck.CompileError, match="frozen"):
        compile_deck.freeze_copy(tmp_path, "kickoff", "2026-11-17-k1", False)
    assert (target / "index.html").read_text(encoding="utf-8") == "<html>v1</html>"


def test_freeze_replace_only_on_request_and_keeps_history(tmp_path: Path) -> None:
    master = published_master(tmp_path)
    compile_deck.freeze_copy(tmp_path, "kickoff", "2026-11-17", False, today="2026-11-17")
    (master / "index.html").write_text("<html>v2</html>", encoding="utf-8")
    target = compile_deck.freeze_copy(tmp_path, "kickoff", "2026-11-17", True, today="2026-11-20")
    assert (target / "index.html").read_text(encoding="utf-8") == "<html>v2</html>"
    record = json.loads((target / "FROZEN.json").read_text(encoding="utf-8"))
    assert record["frozen_on"] == "2026-11-20" and record["replaced"] == ["2026-11-17"]


def test_freeze_rejects_a_label_that_is_not_a_date(tmp_path: Path) -> None:
    published_master(tmp_path)
    for bad in ("kindler", "../2026-11-17", "2026-11-17/x", "2026-11-17-Kindler"):
        with pytest.raises(compile_deck.CompileError):
            compile_deck.freeze_copy(tmp_path, "kickoff", bad, False)


def test_publish_never_writes_into_a_frozen_copy(tmp_path: Path) -> None:
    deck = tmp_path / "build"
    deck.mkdir()
    (deck / "index.html").write_text("x", encoding="utf-8")
    frozen = tmp_path / "site" / "metronomics" / "kickoff"
    frozen.mkdir(parents=True)
    (frozen / "FROZEN.json").write_text("{}", encoding="utf-8")
    with pytest.raises(compile_deck.CompileError, match="frozen"):
        compile_deck.copy_publish(deck, tmp_path / "site", "kickoff", False)


def test_impact_lists_every_master_a_library_change_alters(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pres = repo / "darlison" / "presentations"
    lib = pres / "libraries" / "demo"
    lib.mkdir(parents=True)
    (pres / "playlists").mkdir()
    (pres / "metronomics" / "library").mkdir(parents=True)
    slide = lambda sid, head: {"id": sid, "layout": "comp-rule", "title": sid, "headline": head}
    (lib / "shared.json").write_text(json.dumps({"id": "shared", "slides": [slide("one", "One")]}), encoding="utf-8")
    (lib / "only-a.json").write_text(json.dumps({"id": "only-a", "slides": [slide("a", "A")]}), encoding="utf-8")
    for name, units in (("deck-a", ["demo:shared", "demo:only-a"]), ("deck-b", ["demo:shared"]), ("deck-c", ["demo:only-a"])):
        (pres / "playlists" / f"{name}.json").write_text(json.dumps({"id": name, "sources": {"demo": "../libraries/demo"}, "units": units}), encoding="utf-8")
    run = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
    run("init", "-q"); run("add", "."); run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    (lib / "shared.json").write_text(json.dumps({"id": "shared", "slides": [slide("one", "One, edited"), slide("two", "Two")]}), encoding="utf-8")
    original = compile_deck.PRESENTATIONS, compile_deck.LIBRARY
    compile_deck.PRESENTATIONS, compile_deck.LIBRARY = pres, pres / "metronomics" / "library"
    try:
        rows = {r["playlist"]: r for r in compile_deck.impact_report("HEAD")}
    finally:
        compile_deck.PRESENTATIONS, compile_deck.LIBRARY = original
    assert set(rows) == {"deck-a", "deck-b"}
    assert rows["deck-a"]["slides_before"] == 2 and rows["deck-a"]["slides_after"] == 3
    assert rows["deck-b"]["changed_slides"] == ["shared-one"]
    assert rows["deck-b"]["added"] == ["shared-two"]


# --- Deck QR codes open the version delivered (Byron, 16-Nov-2026) ------------

MASTER_URL = "https://byrondarlison.github.io/coaching-slides/metronomics/kickoff/"


def test_qr_encoder_matches_the_verified_reference() -> None:
    import hashlib
    import qr_svg
    grid = qr_svg.encode(MASTER_URL)
    bits = "".join("1" if cell else "0" for row in grid for cell in row)
    # Fingerprint of the qrcode 7.4.2 image for this address, matched module for module on 16-Nov-2026.
    assert len(grid) == 37
    assert hashlib.sha256(bits.encode()).hexdigest() == "6396da8791bbc31092d52fe3a931afa815556f058b5489f07cd950a62b9b49cd"


def test_qr_encoder_rejects_text_too_long() -> None:
    import qr_svg
    with pytest.raises(ValueError):
        qr_svg.encode("x" * 400)


def test_the_master_deck_qr_opens_the_master(tmp_path: Path) -> None:
    dest = compile_deck.compile_playlist("kickoff", tmp_path / "deck", KICKOFF_FILE)
    page = (dest / "index.html").read_text(encoding="utf-8")
    section = re.search(r'<section[^>]*data-deck-qr="true".*?</section>', page, re.S).group(0)
    assert 'src="./assets/deck-qr.svg"' in section
    assert f'<a class="deck-link" href="{MASTER_URL}" target="_blank" rel="noopener">byrondarlison.github.io/coaching-slides/metronomics/kickoff</a></p>' in section
    assert f'<a class="deck-link art-link-img" href="{MASTER_URL}"' in section
    import qr_svg
    assert (dest / "assets" / "deck-qr.svg").read_text(encoding="utf-8") == qr_svg.svg(MASTER_URL, compile_deck.deck_qr_alt(MASTER_URL))


def test_freezing_repoints_the_qr_to_the_frozen_copy(tmp_path: Path) -> None:
    build = compile_deck.compile_playlist("kickoff", tmp_path / "deck", KICKOFF_FILE)
    site = tmp_path / "site"
    compile_deck.copy_publish(build, site, "kickoff", False)
    target = compile_deck.freeze_copy(site, "kickoff", "2026-11-17-k1", False, today="2026-11-17")
    copy_url = "https://byrondarlison.github.io/coaching-slides/delivered/kickoff/2026-11-17-k1/"
    page = (target / "index.html").read_text(encoding="utf-8")
    assert f'href="{copy_url}" target="_blank" rel="noopener">byrondarlison.github.io/coaching-slides/delivered/kickoff/2026-11-17-k1</a></p>' in page
    assert f'<a class="deck-link art-link-img" href="{copy_url}"' in page
    assert MASTER_URL not in page
    assert "metronomics/kickoff</a></p>" not in page
    import qr_svg
    assert (target / "assets" / "deck-qr.svg").read_text(encoding="utf-8") == qr_svg.svg(copy_url, compile_deck.deck_qr_alt(copy_url))
    assert json.loads((target / "FROZEN.json").read_text(encoding="utf-8"))["qr_opens"] == copy_url
    # The master is untouched and still opens itself.
    assert "metronomics/kickoff</a></p>" in (site / "metronomics" / "kickoff" / "index.html").read_text(encoding="utf-8")


def test_card_slide_ask_line_sits_between_title_and_cards() -> None:
    unit = {"id": "ask", "layout": "comp-decision", "title": "T", "headline": "H", "support": "Rate each <one>.",
            "panels": [{"role": "Daily", "heading": "A", "support": "a", "mark": "structure"},
                       {"role": "Weekly", "heading": "B", "support": "b", "mark": "structure"}]}
    html = compile_deck.render_slide(unit, 1)
    assert '<p class="support card-lede title-follow">Rate each &lt;one&gt;.</p>' in html
    assert html.index("card-lede") < html.index("decision-row")
    unit.pop("support")
    assert "card-lede" not in compile_deck.render_slide(unit, 1)


def test_card_items_carry_hover_terms():
    unit = {"terms": [{"term": "Dynamic", "tip": "Stucks and topics that cannot wait."}]}
    html = compile_deck.term_tips(compile_deck.escape("Dynamic"), unit)
    assert 'class="term"' in html and "Stucks and topics" in html


# --- Deck builder: instruction line, links, hover pictures, line highlights (ai-config #1832) ---

FIXTURE = TOOLS / "fixtures" / "deck-builder" / "playlist.json"
ART = {"src": "assets/a.svg", "alt": "A test drawing."}


def _story(**extra: object) -> dict:
    return {"id": "s", "layout": "comp-story", "title": "T", "headline": "Headline", **extra}


def test_side_picture_panel_carries_its_picture_shape() -> None:
    html = compile_deck.render_slide(_story(art_side=True, support="Ask.", artwork=dict(ART), _art_ratio=1.5), 1)
    assert 'class="story-panel story-panel--art" style="--par:1.5"' in html
    plain = compile_deck.render_slide(_story(art_side=True, support="Ask.", artwork=dict(ART)), 1)
    assert "--par" not in plain


def test_image_ratio_reads_a_jpeg(tmp_path: Path) -> None:
    # SOI, then a baseline frame header: 8-bit, 300 tall, 600 wide.
    data = b"\xff\xd8" + b"\xff\xe0\x00\x04\x00\x00" + b"\xff\xc0\x00\x0b\x08" + (300).to_bytes(2, "big") + (600).to_bytes(2, "big") + b"\x01\x01\x11\x00"
    picture = tmp_path / "p.jpg"
    picture.write_bytes(data)
    assert compile_deck.image_ratio(picture) == 2.0


def test_side_picture_width_flags_set_their_own_classes() -> None:
    plain = compile_deck.render_slide(_story(art_side=True, support="Ask.", artwork=dict(ART)), 1)
    large = compile_deck.render_slide(_story(art_side=True, art_large=True, support="Ask.", artwork=dict(ART)), 1)
    small = compile_deck.render_slide(_story(art_side=True, art_small=True, support="Ask.", artwork=dict(ART)), 1)
    assert "story-frame--art-large" not in plain and "story-frame--art-small" not in plain
    assert 'class="story-frame story-frame--side story-frame--art-large"' in large
    assert 'class="story-frame story-frame--side story-frame--art-small"' in small


def test_full_width_drawing_shows_its_support_line_between_title_and_picture() -> None:
    html = compile_deck.render_slide(_story(art_full=True, support="In Metronome: open **Team View** <now>.", artwork=dict(ART)), 1)
    assert '<p class="support story-lede">In Metronome: open <strong class="hl">Team View</strong> &lt;now&gt;.</p>' in html
    assert "story-frame--full story-frame--lede" in html
    assert html.index("story-title") < html.index("story-lede") < html.index("story-panel")
    fit = compile_deck.render_slide(_story(art_full=True, art_fit=True, support="One line.", artwork=dict(ART)), 1)
    assert "story-frame--full story-frame--fit story-frame--lede" in fit
    assert "story-lede" not in compile_deck.render_slide(_story(art_full=True, artwork=dict(ART)), 1)


def test_body_text_on_a_full_width_drawing_warns_or_fails_and_is_never_silent() -> None:
    slide = _story(art_full=True, body=["A line nobody would see."], artwork=dict(ART), _name="demo-slide")
    compile_deck.WARNINGS.clear()
    compile_deck.render_slide(dict(slide), 1)
    assert len(compile_deck.WARNINGS) == 1 and "demo-slide" in compile_deck.WARNINGS[0] and "body" in compile_deck.WARNINGS[0]
    with pytest.raises(compile_deck.CompileError, match="demo-slide: a full-width drawing slide"):
        compile_deck.render_slide({**slide, "_fail_on_dropped_text": True}, 1)
    # A plain drawing slide drops support and body too: the same warning and the same switch.
    with pytest.raises(compile_deck.CompileError, match="shows only its title and picture"):
        compile_deck.render_slide(_story(support="Lost.", artwork=dict(ART), _fail_on_dropped_text=True), 1)
    compile_deck.WARNINGS.clear()


def test_the_dropped_text_switch_reaches_the_command_line(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    playlist = _library(tmp_path, _story(art_full=True, body=["Lost line."], artwork=dict(ART)), {"assets/a.svg": "<svg></svg>"})
    assert compile_deck.main(["--playlist-file", str(playlist), "--out", str(tmp_path / "out")]) == 0
    assert "WARNING: unit-s: a full-width drawing slide" in capsys.readouterr().err
    # The publish route builds through the same function, so it reports the same warning, once.
    compile_deck.compile_playlist("x", tmp_path / "out3", playlist)
    assert capsys.readouterr().err.count("WARNING: unit-s: a full-width drawing slide") == 1
    assert compile_deck.main(["--playlist-file", str(playlist), "--out", str(tmp_path / "out2"), "--fail-on-dropped-text"]) == 1
    assert "FAIL: unit-s: a full-width drawing slide" in capsys.readouterr().err


def _linked(**art: object) -> dict:
    return _story(artwork={**ART, "viewbox": [1000, 500], **art})


LINK = {"x": 100, "y": 50, "w": 200, "h": 200, "href": "https://example.com/a?b=1&c=2", "label": "Open <the> sheet"}


def test_artwork_links_render_as_real_links_over_the_picture_and_as_text() -> None:
    html = compile_deck.render_slide(_linked(qr=True, links=[LINK, {"x": 600, "y": 50, "w": 200, "h": 200, "href": "https://example.com/two/"}]), 1)
    area = ('<a class="deck-link art-link" href="https://example.com/a?b=1&amp;c=2" target="_blank" rel="noopener" '
            'style="left:10.000%;top:10.000%;width:20.000%;height:40.000%" aria-label="Open &lt;the&gt; sheet, opens in a new tab"></a>')
    assert area in html
    assert '<a class="deck-link art-link-text" href="https://example.com/a?b=1&amp;c=2" target="_blank" rel="noopener">Open &lt;the&gt; sheet</a>' in html
    # A link with no label shows its address without the scheme.
    assert 'rel="noopener">example.com/two</a>' in html
    assert 'class="story-panel story-panel--art story-panel--links"' in html
    assert html.index("art-hot") < html.index('class="art-links"')
    compile_deck.check_no_network(html)
    # An address is written exactly as given, so parentheses arrive already encoded and pass both checks.
    wiki = compile_deck.render_slide(_linked(links=[{**LINK, "href": "https://example.com/guide_%28overview%29"}]), 1)
    assert 'href="https://example.com/guide_%28overview%29"' in wiki
    compile_deck.check_no_network(wiki)


@pytest.mark.parametrize("href", [
    "http://example.com/", "javascript:alert(1)", "//example.com/", "mailto:a@example.com", "https://", "https://localhost/",
    "https://user@example.com/", "https://example.com:8443/", 'https://example.com/"onmouseover="x', "https://example.com/a b",
    "https://example.com/<script>", "https://example.com/guide_(overview)", "https://example.com/?q=(a)", "HTTPS://example.com/", " https://example.com/", "https://ex\u00e4mple.com/", 7, None,
])
def test_artwork_links_refuse_anything_but_a_plain_https_address(href: object) -> None:
    with pytest.raises(compile_deck.CompileError, match="link"):
        compile_deck.render_slide(_linked(links=[{**LINK, "href": href}]), 1)


@pytest.mark.parametrize("art,message", [
    ({"links": [LINK], "viewbox": None}, "links need a viewbox"),
    ({"links": []}, "non-empty list"),
    ({"links": "https://example.com/"}, "non-empty list"),
    ({"links": [{**LINK, "x": True}]}, "numeric x, y, w and h"),
    ({"links": [{**LINK, "y": "50"}]}, "numeric x, y, w and h"),
    ({"links": [{**LINK, "h": None}]}, "numeric x, y, w and h"),
    ({"links": [{**LINK, "w": 10 ** 400}]}, "numeric x, y, w and h"),
    ({"links": [{**LINK, "y": -1}]}, "inside the picture"),
    ({"links": [{**LINK, "h": 451}]}, "inside the picture"),
    ({"links": [LINK], "viewbox": [True, 500]}, "links need a viewbox"),
    ({"links": [LINK], "viewbox": [float("inf"), 500]}, "links need a viewbox"),
    ({"links": [{**LINK, "label": ["a"]}]}, "label is a line of text"),
    ({"links": [{**LINK, "label": 5}]}, "label is a line of text"),
    ({"qr": 1}, '"qr" is true or false'),
    ({"qr": None}, '"qr" is true or false'),
    ({"links": None}, "non-empty list"),
    ({"links": [{**LINK, "label": None}]}, "label is a line of text"),
    ({"links": [{**LINK, "w": 0}]}, "inside the picture"),
    ({"links": [{**LINK, "x": 900}]}, "inside the picture"),
    ({"links": [{**LINK, "onclick": "x"}]}, "each link takes"),
    ({"links": [{**LINK, "label": "https://example.com/a"}]}, "without https://"),
    ({"qr": True}, 'marked "qr": true must record a link'),
    ({"qr": True, "hotspots": [{"x": 1, "y": 1, "w": 5, "h": 5, "term": "A", "tip": "B"}]}, 'marked "qr": true must record a link'),
    ({"qr": "yes", "links": [LINK]}, '"qr" is true or false'),
])
def test_artwork_links_and_qr_marks_fail_closed(art: dict, message: str) -> None:
    with pytest.raises(compile_deck.CompileError, match=message):
        compile_deck.render_slide(_linked(**art), 1)


def test_artwork_links_are_refused_on_layouts_that_cannot_show_the_text_links() -> None:
    slide = {"id": "r", "layout": "comp-rule", "title": "T", "headline": "H", "support": "S", "artwork": {**ART, "viewbox": [1000, 500], "links": [LINK]}}
    with pytest.raises(compile_deck.CompileError, match="comp-story slides only"):
        compile_deck.render_slide(slide, 1)


def test_only_a_compiler_written_link_may_carry_a_network_address() -> None:
    compile_deck.check_no_network(f'{compile_deck.link_tag("https://example.com/")}>x</a>')
    hidden = ('<style>/*<a class="deck-link*/body{background-image:url(https://evil.example/pixel)}'
              '/*" href="https://example.com/" target="_blank" rel="noopener"*/</style>')
    for html in (hidden, '<img src="https://example.com/a.png">', '<a href="https://example.com/">x</a>',
                 '<a class="deck-link" href="https://example.com/" target="_blank" rel="noopener">https://example.com/</a>',
                 '<a class="deck-link" href="http://example.com/" target="_blank" rel="noopener">x</a>'):
        with pytest.raises(compile_deck.CompileError, match="network URL"):
            compile_deck.check_no_network(html)


def test_check_shell_allows_deck_links_and_still_refuses_other_addresses(tmp_path: Path) -> None:
    dest = compile_deck.compile_playlist("x", tmp_path / "deck", FIXTURE)
    assert compile_deck.run_check_shell(dest) == 0
    page = dest / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace("</main>", '<img src="https://example.com/x.png"></main>'), encoding="utf-8")
    assert compile_deck.run_check_shell(dest) == 1
    # The allowance is for the page only: an address hidden in the stylesheet behind link-shaped comments fails.
    clean = compile_deck.compile_playlist("x", tmp_path / "deck2", FIXTURE)
    with (clean / "shell.css").open("a", encoding="utf-8") as sheet:
        sheet.write('/*<a class="deck-link*/body{background-image:url(https://evil.example/pixel)}/*" href="https://example.com/" target="_blank" rel="noopener"*/')
    assert compile_deck.run_check_shell(clean) == 1


def test_fixture_deck_compiles_every_new_feature(tmp_path: Path) -> None:
    dest = compile_deck.compile_playlist("x", tmp_path / "deck", FIXTURE)
    page = (dest / "index.html").read_text(encoding="utf-8")
    assert compile_deck.WARNINGS == []
    for token in ("story-frame--lede", 'class="art-links"', "art-link-img", 'class="term term--image term--below"', "<polyline points=", 'class="term-image"'):
        assert token in page, token
    # The deck QR address is a link, and so is the code itself.
    assert '<a class="deck-link" href="https://example.com/decks/fixture/" target="_blank" rel="noopener">example.com/decks/fixture</a>' in page
    assert all((dest / src).is_file() for src in re.findall(r'<img class="term-image" src="\./([^"]+)"', page))


def test_a_term_shows_a_library_picture_and_works_in_a_title(tmp_path: Path) -> None:
    slide = _story(headline="Find your Market Map", copy_stack=True, support="The Market Map is a picture.",
                   terms=[{"term": "Market Map", "tip": "Where <each> competitor sits.", "image": {"src": "assets/map.svg", "alt": 'A "map" drawing.'}}])
    _library(tmp_path, slide, {"assets/map.svg": '<svg xmlns="x" viewBox="0 0 800 400"></svg>'})
    library = tmp_path / "lib"
    out = tmp_path / "out"
    out.mkdir()
    unit = {**slide, "_root": library}
    compile_deck.prepare_artwork([unit], out)
    html = compile_deck.render_slide(unit, 1)
    title = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1)
    assert 'class="term term--image term--below" tabindex="0"' in title
    assert 'aria-label="Market Map: Where &lt;each&gt; competitor sits. A &quot;map&quot; drawing."' in title
    picture = re.search(r'<img class="term-image" src="\./(assets/[0-9a-f]{20}\.svg)" alt="A &quot;map&quot; drawing\." style="--ar:2\.0">', title)
    assert picture and (out / picture.group(1)).is_file()
    # The box carries the picture's ratio too, so its text lines can share the picture's width.
    assert '<span class="hotspot-tip" role="tooltip" style="--ar:2.0">' in title
    # The same term still works in support text, opening above the word by default.
    support = html.split("</h1>", 1)[1]
    assert 'class="term term--image" tabindex="0"' in support and "term-image" in support
    # A picture alone is enough; text lines are optional.
    unit2 = {**slide, "_root": library, "terms": [{"term": "Market Map", "image": {"src": "assets/map.svg", "alt": "A map."}}]}
    compile_deck.prepare_artwork([unit2], out)
    assert "term-line" not in compile_deck.render_slide(unit2, 1)


@pytest.mark.parametrize("image,message", [
    ({"src": "assets/map.svg"}, "descriptive alt text"),
    ({"src": "assets/map.svg", "alt": "A map.", "href": "x"}, "descriptive alt text"),
    ("assets/map.svg", "descriptive alt text"),
    ({"src": "../outside.svg", "alt": "A map."}, "inside its library"),
    ({"src": "assets/missing.svg", "alt": "A map."}, "missing artwork"),
    ({"src": "assets/notes.txt", "alt": "A map."}, "inside its library"),
    ({"src": "assets/\u0000.svg", "alt": "A map."}, "inside its library"),
    ({"src": "assets/map.svg", "alt": ["A map."]}, "descriptive alt text"),
    ({"src": "assets/map.svg", "alt": 7}, "descriptive alt text"),
    ({"src": "assets/loop.svg", "alt": "A map."}, "inside its library|missing artwork"),
    (None, "descriptive alt text"),
])
def test_a_term_image_must_be_a_described_picture_inside_its_library(tmp_path: Path, image: object, message: str) -> None:
    slide = _story(terms=[{"term": "Headline", "tip": "A line.", "image": image}])
    _library(tmp_path, slide, {"assets/map.svg": "<svg></svg>", "assets/notes.txt": "x"})
    library = tmp_path / "lib"
    (tmp_path / "outside.svg").write_text("<svg></svg>", encoding="utf-8")
    (tmp_path / "lib" / "assets" / "loop.svg").symlink_to("loop.svg")
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(compile_deck.CompileError, match=message):
        compile_deck.prepare_artwork([{**slide, "_root": library}], out)


def test_a_term_needs_a_tip_or_a_prepared_image() -> None:
    with pytest.raises(compile_deck.CompileError, match="a tip or an image"):
        compile_deck.term_tips("Word", {"terms": [{"term": "Word"}]})
    with pytest.raises(compile_deck.CompileError, match="needs preparing"):
        compile_deck.term_tips("Word", {"terms": [{"term": "Word", "image": {"src": "a.svg", "alt": "A."}}]})


def test_image_ratio_reads_svg_and_png_sizes_and_falls_back(tmp_path: Path) -> None:
    svg = tmp_path / "a.svg"
    svg.write_text('<svg viewBox="0 0 900 300"></svg>', encoding="utf-8")
    png = tmp_path / "a.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (400).to_bytes(4, "big") + (200).to_bytes(4, "big"))
    other = tmp_path / "a.jpg"
    other.write_bytes(b"not a picture")
    assert compile_deck.image_ratio(svg) == 3.0 and compile_deck.image_ratio(png) == 2.0 and compile_deck.image_ratio(other) == 1.6
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert compile_deck.image_ratio(png) == 1.6


def _spot(**extra: object) -> dict:
    return {"x": 100, "y": 300, "w": 200, "h": 100, "term": "Line A", "tip": "Follow line A.", **extra}


def test_a_hotspot_can_hide_its_info_mark() -> None:
    shown = compile_deck.render_slide(_linked(hotspots=[_spot()]), 1)
    hidden = compile_deck.render_slide(_linked(hotspots=[_spot(icon=False)]), 1)
    assert 'class="hotspot-i"' in shown and 'class="hotspot-i"' not in hidden
    assert 'class="hotspot" tabindex="0"' in hidden and "Follow line A." in hidden
    for bad in (True, "none", [1], [1, "2"], 0, [10 ** 400, 1]):
        with pytest.raises(compile_deck.CompileError, match="or false for no mark"):
            compile_deck.render_slide(_linked(hotspots=[_spot(icon=bad)]), 1)


def test_a_hotspot_target_can_be_a_line() -> None:
    line = {"points": [[10, 20], [30.5, 40], [50, 10]], "width": 16}
    html = compile_deck.render_slide(_linked(hotspots=[_spot(targets=[line, [5, 5, 10, 10]])]), 1)
    assert ('<polyline points="10,20 30.5,40 50,10" fill="none" stroke="black" stroke-width="16" '
            'stroke-linecap="round" stroke-linejoin="round"/><rect x="5" y="5" width="10" height="10" fill="black"/></mask>') in html
    assert "hotspot--targets" in html


@pytest.mark.parametrize("target,message", [
    ({"points": [[1, 2]], "width": 4}, "at least two"),
    ({"points": [[1, 2], [3, "4"]], "width": 4}, "at least two"),
    ({"points": [[1, 2], [3, True]], "width": 4}, "at least two"),
    ({"points": [[1, 2], [3, 4, 5]], "width": 4}, "at least two"),
    ({"points": [[1, 2], [3, 10 ** 400]], "width": 4}, "at least two"),
    ({"points": [[1, 2], [3, 4]], "width": 10 ** 400}, "width above zero"),
    ({"points": [[1, 2], [3, 4]], "width": 0}, "width above zero"),
    ({"points": [[1, 2], [3, 4]], "width": "4"}, "width above zero"),
    ({"points": [[1, 2], [3, 4]]}, "boxes or"),
    ({"points": [[1, 2], [3, 4]], "width": 4, "stroke": "url(#x)"}, "boxes or"),
    ([1, 2, 3], "boxes or"),
    ("1,2 3,4", "boxes or"),
])
def test_line_targets_fail_closed(target: object, message: str) -> None:
    with pytest.raises(compile_deck.CompileError, match=message):
        compile_deck.render_slide(_linked(hotspots=[_spot(targets=[target])]), 1)


def test_a_source_slide_cannot_set_the_compilers_own_fields(tmp_path: Path) -> None:
    for field, value in (("_deck_url", "javascript:alert(1)"), ("_figure_svg", "<script>x</script>"), ("_image", {})):
        playlist = _library(tmp_path, _story(**{field: value}), {"assets/a.svg": "<svg></svg>"})
        with pytest.raises(compile_deck.CompileError, match="build-only field"):
            compile_deck.resolve_playlist(compile_deck.load_playlist_file(playlist))
    # And the link writer checks every address itself, whoever calls it.
    for bad in ("javascript:alert(1)", "//evil.example/path", "http://example.com/"):
        with pytest.raises(compile_deck.CompileError, match="link"):
            compile_deck.link_tag(bad)
        with pytest.raises(compile_deck.CompileError, match="link"):
            compile_deck.render_slide(_story(art_side=True, body=["x"], artwork=dict(ART), _deck_url=bad), 1)


def test_terms_match_only_in_written_text_never_inside_another_terms_box() -> None:
    unit = {"terms": [{"term": "Map", "tip": "Shows each Position.", "_image": {"src": "assets/a.svg", "alt": "Example Position", "ratio": 1.6}, "image": {}},
                      {"term": "Position", "tip": "A position."}]}
    html = compile_deck.term_tips(compile_deck.escape("Map and Position"), unit)
    assert html.count('tabindex="0"') == 2
    assert 'aria-label="Map: Shows each Position. Example Position"' in html
    assert html.endswith('and <span class="term" tabindex="0" aria-label="Position: A position.">Position'
                         '<span class="hotspot-tip" role="tooltip"><strong>Position</strong><span class="term-line">A position.</span></span></span>')
    # Overlapping terms: the first listed wins, and the second takes the next free match.
    both = compile_deck.term_tips("Market Map and Map", {"terms": [{"term": "Market Map", "tip": "a"}, {"term": "Map", "tip": "b"}]})
    assert both.count('tabindex="0"') == 2 and both.startswith('<span class="term" tabindex="0" aria-label="Market Map: a">')
    # Emphasis markup around a term is left intact.
    marked = compile_deck.term_tips(compile_deck.emphasis("Open **Team View** now"), {"terms": [{"term": "hl", "tip": "x"}, {"term": "Team View", "tip": "y"}]})
    assert marked.count('tabindex="0"') == 1 and '<strong class="hl"><span class="term"' in marked


def test_terms_work_in_the_accent_part_of_a_title() -> None:
    unit = {"id": "a", "layout": "comp-attempts", "title": "T", "headline": "Find your", "headline_accent": "Map",
            "attempts": [{"heading": "One"}], "terms": [{"term": "Map", "tip": "The picture."}]}
    html = compile_deck.render_slide(unit, 1)
    assert '<span class="title-accent"><span class="term term--below" tabindex="0" aria-label="Map: The picture.">Map' in html


def test_titles_balance_and_supporting_text_fills_the_line() -> None:
    css = (PRESENTATIONS / "shared" / "deck" / "shell.css").read_text(encoding="utf-8")
    rule = lambda selector: re.search(r"(?m)^" + re.escape(selector) + r" \{([^}]*)\}", css).group(1)
    assert "text-wrap: balance" in rule(".slide-title") and "text-wrap: balance" in rule(".story-title")
    # The last text-wrap rule that reaches a story or card support line must not be balance.
    assert ".story-frame .support, .card-lede { text-wrap: pretty; }" in css
    assert css.rindex(".story-frame .support, .card-lede { text-wrap: pretty; }") > css.rindex("text-wrap: balance")


@pytest.mark.parametrize("master", [
    "https://example.com/decks/probe/",
    "https://example.com/deck_%28overview%29/",
    "https://example.com/a&b/decks/",
    "https://example.com/deck//",
    "https://byrondarlison.github.io/coaching-slides/",
    "https://byrondarlison.github.io/coaching-slides/metronomics/probe/extra/",
])
def test_freezing_rewrites_every_link_on_the_qr_slide(tmp_path: Path, master: str) -> None:
    slide = _story(id="qr", art_side=True, deck_qr=True, body=["{deck_url}"])
    playlist = _library(tmp_path, slide, {"assets/a.svg": "<svg></svg>"})
    data = json.loads(playlist.read_text(encoding="utf-8"))
    playlist.write_text(json.dumps({**data, "id": "probe", "public_url": master}), encoding="utf-8")
    site = tmp_path / "site"
    compile_deck.compile_playlist("probe", site / "custom", playlist)
    built = (site / "custom" / "index.html").read_text(encoding="utf-8")
    assert built.count(f'href="{compile_deck.escape(master)}"') == 2
    target = compile_deck.freeze_copy(site, "probe", "2026-11-24", False, source_rel="custom", today="2026-11-24")
    page = (target / "index.html").read_text(encoding="utf-8")
    copy_url = compile_deck.frozen_url("probe", "2026-11-24")
    section = re.search(r'<section[^>]*data-deck-qr="true".*?</section>', page, re.S).group(0)
    # Every destination on the slide is the frozen address, exactly: both links, the text shown, the description, the code.
    assert re.findall(r'href="([^"]*)"', section) == [copy_url, copy_url]
    assert f'rel="noopener">{compile_deck.display_url(copy_url)}</a></p>' in section
    assert f'alt="{compile_deck.deck_qr_alt(copy_url)}"' in section
    assert f'aria-label="{compile_deck.display_url(copy_url)}, opens in a new tab"' in section
    import qr_svg
    assert (target / "assets" / "deck-qr.svg").read_text(encoding="utf-8") == qr_svg.svg(copy_url, compile_deck.deck_qr_alt(copy_url))


def test_freeze_reads_the_master_address_from_the_slide_and_never_from_other_text(tmp_path: Path) -> None:
    # The playlist declares its own address, and the slide's support text names the default one.
    master = "https://example.com/deck_%28overview%29/"
    decoy = "byrondarlison.github.io/coaching-slides/metronomics/probe"
    slide = _story(id="qr", art_side=True, deck_qr=True, support=f"Not the address: {decoy}", body=["{deck_url}"])
    playlist = _library(tmp_path, slide, {"assets/a.svg": "<svg></svg>"})
    data = json.loads(playlist.read_text(encoding="utf-8"))
    playlist.write_text(json.dumps({**data, "id": "probe", "public_url": master}), encoding="utf-8")
    site = tmp_path / "site"
    compile_deck.compile_playlist("probe", site / "metronomics" / "probe", playlist)
    target = compile_deck.freeze_copy(site, "probe", "2026-11-24", False, today="2026-11-24")  # the default route
    section = re.search(r'<section[^>]*data-deck-qr="true".*?</section>', (target / "index.html").read_text(encoding="utf-8"), re.S).group(0)
    copy_url = compile_deck.frozen_url("probe", "2026-11-24")
    assert re.findall(r'href="([^"]*)"', section) == [copy_url, copy_url]
    assert f"Not the address: {decoy}</p>" in section  # ordinary text is left alone


def test_freeze_fails_when_a_qr_slide_link_would_still_open_the_master(tmp_path: Path) -> None:
    section = ('<section data-deck-qr="true"><a class="deck-link" href="https://example.com/other/" target="_blank" rel="noopener">example.com/other</a>'
               '<a class="deck-link art-link-img" href="https://example.com/deck/" target="_blank" rel="noopener" aria-label="example.com/deck, opens in a new tab">'
               '<img alt="QR code that opens these slides at example.com/deck."></a></section>')
    with pytest.raises(compile_deck.CompileError, match="do not all open the frozen copy"):
        compile_deck.requote_qr_slide(section, "https://example.com/deck/", "https://example.com/copy/")


def test_a_deck_address_with_brackets_is_refused_before_anything_is_built(tmp_path: Path) -> None:
    playlist = _library(tmp_path, _story(id="qr", art_side=True, deck_qr=True, body=["{deck_url}"]), {"assets/a.svg": "<svg></svg>"})
    data = json.loads(playlist.read_text(encoding="utf-8"))
    for address, message in (("https://example.com/deck_(overview)/", "%28"), ("https://example.com/deck/?v=1", "folder address"),
                             ("https://example.com/deck/#top", "folder address"), ("https://example.com/deck", "folder address")):
        playlist.write_text(json.dumps({**data, "public_url": address}), encoding="utf-8")
        with pytest.raises(compile_deck.CompileError, match=message):
            compile_deck.compile_playlist("about", tmp_path / "out", playlist)

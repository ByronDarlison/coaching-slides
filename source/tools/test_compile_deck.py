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
    assert "byrondarlison.github.io/coaching-slides/metronomics/kickoff</p>" in section
    import qr_svg
    assert (dest / "assets" / "deck-qr.svg").read_text(encoding="utf-8") == qr_svg.svg(MASTER_URL, compile_deck.deck_qr_alt(MASTER_URL))


def test_freezing_repoints_the_qr_to_the_frozen_copy(tmp_path: Path) -> None:
    build = compile_deck.compile_playlist("kickoff", tmp_path / "deck", KICKOFF_FILE)
    site = tmp_path / "site"
    compile_deck.copy_publish(build, site, "kickoff", False)
    target = compile_deck.freeze_copy(site, "kickoff", "2026-11-17-k1", False, today="2026-11-17")
    copy_url = "https://byrondarlison.github.io/coaching-slides/delivered/kickoff/2026-11-17-k1/"
    page = (target / "index.html").read_text(encoding="utf-8")
    assert "coaching-slides/delivered/kickoff/2026-11-17-k1</p>" in page
    assert "metronomics/kickoff</p>" not in page
    import qr_svg
    assert (target / "assets" / "deck-qr.svg").read_text(encoding="utf-8") == qr_svg.svg(copy_url, compile_deck.deck_qr_alt(copy_url))
    assert json.loads((target / "FROZEN.json").read_text(encoding="utf-8"))["qr_opens"] == copy_url
    # The master is untouched and still opens itself.
    assert "metronomics/kickoff</p>" in (site / "metronomics" / "kickoff" / "index.html").read_text(encoding="utf-8")


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

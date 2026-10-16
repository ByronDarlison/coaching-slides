"""Tests for narration extraction, fingerprints and workflow safety (Work Card ai-config#1382)."""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import narration  # noqa: E402
import run  # noqa: E402

ROOT = narration.REPO_ROOT
WORKFLOW = ROOT / ".github/workflows/narrated-video.yml"
PRON = narration.load_pronunciations()


def deck_html(slides: str) -> str:
    return f"<html><body><main id='presentation'>{slides}</main></body></html>"


def slide(n: int, notes: str | None, extra: str = "") -> str:
    aside = f'<aside class="speaker-notes">{notes}</aside>' if notes is not None else ""
    return f'<section class="slide" id="slide-{n}" {extra}><div class="slide-content"><img src="a.png"/><h1>T</h1></div>{aside}</section>'


class Extraction(unittest.TestCase):
    def test_marker_cut_entities_whitespace_and_paragraphs(self):
        html = deck_html(slide(1, "<p>Hello &amp; welcome,\n   friends.</p><p>Second   line.</p><p>In the room: 3:15 PM. Facilitator only.</p>"))
        self.assertEqual(narration.extract(html, PRON), [{"slide": 1, "text": "Hello & welcome, friends.\n\nSecond line."}])

    def test_skip_missing_empty_and_duplicate_notes(self):
        html = deck_html(slide(1, "<p>Keep.</p>") + slide(2, "<p>Skip me.</p>", 'data-narration="skip"')
                         + slide(3, None) + slide(4, "<p>In the room: only this.</p>"))
        self.assertEqual([i["slide"] for i in narration.extract(html, PRON)], [1])
        with self.assertRaises(narration.NarrationError):
            narration.extract(deck_html(slide(1, "<p>a</p>") .replace("</section>", '<aside class="speaker-notes"><p>b</p></aside></section>')), PRON)

    def test_slide_ids_must_be_sequential(self):
        with self.assertRaises(narration.NarrationError):
            narration.extract(deck_html(slide(2, "<p>x</p>")), PRON)

    def test_oversized_slide_refused(self):
        with self.assertRaises(narration.NarrationError):
            narration.extract(deck_html(slide(1, "<p>" + "x" * 5001 + "</p>")), PRON)

    def test_pronunciations_whole_token_longest_first(self):
        text = narration.apply_pronunciations("Your BHAG, 3HAG, 1HAG and QHAG. EOA is SMART. BHAGS 13HAG", PRON)
        self.assertEqual(text, "Your Bee-hag, Three-hag, One-hag and Queue-hag. E-O-A is smart. BHAGS 13HAG")


class RealDecks(unittest.TestCase):
    def test_discovery_finds_both_noted_decks_recursively(self):
        decks = narration.discover()
        self.assertIn("eoa/meeting-4", decks)
        self.assertIn("metronomics/kickoff", decks)
        self.assertFalse(any(d.startswith("tests") for d in decks))

    def test_real_decks_extract_self_contained(self):
        counts = {}
        for deck in narration.discover():
            narration.check_self_contained(deck)
            items = narration.extract((ROOT / deck / "index.html").read_text(encoding="utf-8"))
            counts[deck] = items
            for i in items:
                self.assertNotIn("In the room:", i["text"])
                self.assertNotRegex(i["text"], r"(?<![A-Za-z0-9])(BHAG|3HAG|1HAG|QHAG)(?![A-Za-z0-9])")
        self.assertEqual(len(counts["metronomics/kickoff"]), 105)
        m4 = [i["slide"] for i in counts["eoa/meeting-4"]]
        self.assertEqual(m4, list(range(3 if self._m4_skips() else 1, 15)))

    def _m4_skips(self) -> bool:
        return 'data-narration="skip"' in (ROOT / "eoa/meeting-4/index.html").read_text(encoding="utf-8")


class Fingerprint(unittest.TestCase):
    settings = {"voice_id": "v", "model_id": "m", "output_format": "f"}

    def test_stable_and_sensitive(self):
        items = [{"slide": 1, "text": "a"}]
        files = [["d/index.html", "abc"], ["d/shell.css", "def"]]
        fp = narration.fingerprint("d", items, self.settings, files)
        self.assertEqual(fp, narration.fingerprint("d", items, self.settings, files))
        self.assertNotEqual(fp, narration.fingerprint("d", [{"slide": 1, "text": "b"}], self.settings, files))
        self.assertNotEqual(fp, narration.fingerprint("d", items, {**self.settings, "voice_id": "w"}, files))
        self.assertNotEqual(fp, narration.fingerprint("d", items, self.settings, [["d/index.html", "abd"], files[1]]))
        self.assertRegex(fp, r"^[0-9a-f]{64}$")

    def test_markdown_files_excluded(self):
        files = narration.deck_files("eoa/meeting-4")
        self.assertTrue(files)
        self.assertFalse(any(p.endswith(".md") for p, _ in files))

    def test_video_name(self):
        self.assertEqual(narration.video_name("eoa/meeting-4", "2026-10-16", "fb9c18d3133b"),
                         "eoa-meeting-4-2026-10-16-fb9c18d.mp4")


class Inputs(unittest.TestCase):
    def test_unknown_deck_refused(self):
        with self.assertRaises(run.RunError):
            run.resolve_decks("eoa/meeting-4; rm -rf /")
        self.assertEqual(run.resolve_decks("eoa/meeting-4"), ["eoa/meeting-4"])

    def test_child_processes_never_see_the_key(self):
        os.environ["NARRATION_BROKER_KEY"] = "test-only"
        try:
            self.assertNotIn("NARRATION_BROKER_KEY", run.child_env())
        finally:
            del os.environ["NARRATION_BROKER_KEY"]

    def test_broker_sends_its_own_user_agent(self):
        seen = {}

        class Res:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"{}"

        def fake_urlopen(req, timeout=0):
            seen.update({k.lower(): v for k, v in req.header_items()})
            return Res()
        original = run.urllib.request.urlopen
        run.urllib.request.urlopen = fake_urlopen
        try:
            run.Broker("https://example.com", "k").post_json("/v1/speech", {"mode": "preflight"})
        finally:
            run.urllib.request.urlopen = original
        self.assertEqual(seen.get("user-agent"), run.USER_AGENT)
        self.assertNotIn("python", run.USER_AGENT.lower())

    def test_broker_requires_https_and_key(self):
        with self.assertRaises(run.RunError):
            run.Broker("http://example.com", "k")
        with self.assertRaises(run.RunError):
            run.Broker("https://example.com", "")


class FakeBroker:
    def __init__(self, cap=0, exists=False):
        self.cap, self.exists, self.spoken, self.uploads = cap, exists, [], []

    def post_json(self, path, payload):
        if path == "/v1/speech":
            return 200, {"voice_id": "v", "model_id": "m", "output_format": "f", "cap": self.cap, "remaining": self.cap}
        return 200, {"exists": self.exists}

    def speak(self, text):
        self.spoken.append(text)
        return (429, b"") if self.cap == 0 else (200, b"")

    def upload(self, *args):
        self.uploads.append(args)
        return 200, {"created": True}


class Modes(unittest.TestCase):
    def test_cap_probe_needs_cap_zero_and_a_refusal(self):
        run.cap_probe(FakeBroker(cap=0))
        with self.assertRaises(run.RunError):
            run.cap_probe(FakeBroker(cap=110000))

    def test_unchanged_deck_spends_nothing(self):
        b = FakeBroker(cap=110000, exists=True)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run.process_deck(b, "eoa/meeting-4", b.post_json("/v1/speech", {})[1], "f" * 40, False, Path(tmp)), 0)
        self.assertEqual(b.spoken, [])
        self.assertEqual(b.uploads, [])

    def test_unaffordable_deck_fails_before_speech(self):
        b = FakeBroker(cap=100)
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(run.RunError):
            run.process_deck(b, "eoa/meeting-4", b.post_json("/v1/speech", {})[1], "f" * 40, False, Path(tmp))
        self.assertEqual(b.spoken, [])


TOOLS = all(shutil.which(t) for t in ("ffmpeg", "ffprobe", "node")) and (HERE / "node_modules").exists()


@unittest.skipUnless(TOOLS or os.environ.get("REQUIRE_TOOLS"), "ffmpeg, node and npm ci needed")
class Rehearsal(unittest.TestCase):
    """Captures every narrated slide at 1920x1080 and assembles a silent video; no speech, no upload."""

    def test_both_decks_rehearse(self):
        for deck in narration.discover():
            b = FakeBroker(cap=0)
            with tempfile.TemporaryDirectory() as tmp:
                run.process_deck(b, deck, b.post_json("/v1/speech", {})[1], "f" * 40, True, Path(tmp))
                items = narration.extract((ROOT / deck / "index.html").read_text(encoding="utf-8"))
                frames = list((Path(tmp) / deck.replace("/", "-") / "frames").glob("slide-*.png"))
                self.assertEqual(len(frames), len(items), deck)
            self.assertEqual(b.spoken, [])
            self.assertEqual(b.uploads, [])


class WorkflowSafety(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text()

    def test_triggers_only_push_main_and_dispatch(self):
        on = self.text.split("\non:", 1)[1].split("\npermissions:", 1)[0]
        for bad in ("pull_request", "workflow_run", "issue_comment", "schedule"):
            self.assertNotIn(bad, on)
        self.assertIn("workflow_dispatch", on)
        self.assertRegex(on, r"push:\s*\n\s*branches:\s*\[main\]")

    def test_permissions_environment_pins_and_no_artifacts(self):
        self.assertRegex(self.text, r"\npermissions:\s*\n\s*contents: read\s*\n")
        self.assertIn("environment: narration", self.text)
        self.assertIn("persist-credentials: false", self.text)
        for uses in re.findall(r"uses:\s*(\S+)", self.text):
            self.assertRegex(uses, r"@[0-9a-f]{40}$")
        self.assertNotIn("upload-artifact", self.text)
        self.assertNotIn("set -x", self.text)
        self.assertIn("npm ci", self.text)

    def test_inputs_and_key_only_through_step_env(self):
        for line in self.text.splitlines():
            stripped = line.strip()
            if stripped.startswith("run:") or (stripped and not stripped.startswith(("-", "#")) and ":" not in stripped):
                self.assertNotIn("${{", stripped, line)
        key_lines = [l for l in self.text.splitlines() if "NARRATION_BROKER_KEY" in l]
        self.assertEqual(len(key_lines), 1)
        self.assertGreaterEqual(len(key_lines[0]) - len(key_lines[0].lstrip()), 10, "key set at step level only")
        self.assertNotIn("curl", self.text)


if __name__ == "__main__":
    unittest.main()

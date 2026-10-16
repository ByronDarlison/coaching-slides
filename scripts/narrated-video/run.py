"""Build and deliver narrated slide videos (Work Card ai-config#1382).

Run by .github/workflows/narrated-video.yml on main. Environment:
  NARRATION_BROKER_URL   broker base URL (not secret)
  NARRATION_BROKER_KEY   caller key (secret; read once, removed from the
                         environment before any child process starts)
  NARRATION_DECK         optional: one deck path to process
  NARRATION_MODE         normal | rehearse | cap_probe

Order per deck, so nothing is spent before every free check passes:
  speech preflight (settings) -> fingerprint -> delivery preflight ->
  affordability -> capture -> speech -> assemble -> upload.
Rehearse replaces speech with silence and stops before upload.
Logs carry deck names, counts, sizes and file names only.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import narration  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO_ROOT = narration.REPO_ROOT
MAX_VIDEO = 95_000_000
CHARS_PER_SECOND = 14
LEAD_MS = 500
USER_AGENT = "coaching-slides-narration/1"
TRAIL_S = 0.75


class RunError(Exception):
    pass


def log(message: str) -> None:
    print(message, flush=True)


class Broker:
    def __init__(self, url: str, key: str):
        if not url.startswith("https://"):
            raise RunError("broker URL must be https")
        if not key:
            raise RunError("broker key missing")
        self.url = url.rstrip("/")
        self._key = key

    def _request(self, path: str, body: bytes, content_type: str, extra: dict | None = None):
        # Cloudflare refuses the default Python-urllib user agent (error 1010).
        headers = {"x-broker-secret": self._key, "content-type": content_type,
                   "user-agent": USER_AGENT, **(extra or {})}
        req = urllib.request.Request(self.url + path, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=600) as res:
                return res.status, res.read()
        except urllib.error.HTTPError as exc:
            return exc.code, b""
        except urllib.error.URLError as exc:
            raise RunError("broker unreachable") from exc

    def post_json(self, path: str, payload: dict):
        status, raw = self._request(path, json.dumps(payload).encode(), "application/json")
        try:
            return status, json.loads(raw) if raw else {}
        except ValueError:
            return status, {}

    def speak(self, text: str):
        return self._request("/v1/speech", json.dumps({"mode": "speak", "text": text}).encode(), "application/json")

    def upload(self, video: Path, name: str, fp: str, deck: str, commit: str):
        data = video.read_bytes()
        status, raw = self._request("/v1/deliver?mode=upload", data, "video/mp4", {
            "x-file-name": name, "x-fingerprint": fp, "x-deck": deck, "x-commit": commit[:7],
            "content-length": str(len(data)),
        })
        return status, (json.loads(raw) if raw else {})


def child_env() -> dict:
    env = dict(os.environ)
    env.pop("NARRATION_BROKER_KEY", None)
    return env


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, env=child_env(), capture_output=True, text=True, **kw)
    if result.returncode != 0:
        raise RunError(f"{Path(cmd[0]).name} failed")
    return result


def speech_settings(broker: Broker) -> dict:
    status, body = broker.post_json("/v1/speech", {"mode": "preflight"})
    if status != 200 or not all(k in body for k in ("voice_id", "model_id", "output_format", "cap", "remaining")):
        raise RunError(f"speech preflight failed ({status})")
    return body


def probe_seconds(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)]).stdout
    return float(json.loads(out)["format"]["duration"])


def silence(path: Path, seconds: float) -> None:
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{seconds:.2f}",
         "-c:a", "libmp3lame", "-b:a", "64k", str(path)])


def segment(frame: Path, audio: Path, out: Path) -> float:
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(frame), "-i", str(audio),
         "-filter_complex", f"[1:a]aresample=44100,aformat=channel_layouts=mono,adelay={LEAD_MS}:all=1,apad=pad_dur={TRAIL_S}[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
         "-crf", "23", "-r", "30", "-c:a", "aac", "-b:a", "96k", "-ar", "44100", "-ac", "1",
         "-shortest", str(out)])
    return probe_seconds(out)


def assemble(segments: list[Path], out: Path) -> None:
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{s.as_posix()}'\n" for s in segments))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
         "-movflags", "+faststart", str(out)])


def validate_video(path: Path, expected_seconds: float) -> float:
    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration",
                           "-of", "json", str(path)]).stdout)
    kinds = sorted(s["codec_type"] for s in info["streams"])
    if kinds != ["audio", "video"]:
        raise RunError("video must have one video and one audio stream")
    duration = float(info["format"]["duration"])
    if abs(duration - expected_seconds) > 1.0 + 0.05 * len(kinds):
        raise RunError("video duration does not match its segments")
    if path.stat().st_size > MAX_VIDEO:
        raise RunError("video larger than 95 MB")
    return duration


def capture(deck: str, slides: list[int], out_dir: Path) -> None:
    server = subprocess.Popen([sys.executable, "-u", "-m", "http.server", "0", "--bind", "127.0.0.1",
                               "--directory", str(REPO_ROOT)], env=child_env(),
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        line = server.stdout.readline()  # "Serving HTTP on 127.0.0.1 port N ..."
        port = line.split(" port ")[1].split()[0]
        run(["node", str(HERE / "capture.mjs"), f"http://127.0.0.1:{port}", deck,
             ",".join(map(str, slides)), str(out_dir)], cwd=HERE)
    finally:
        server.terminate()
        server.wait(timeout=10)
        server.stdout.close()
    for n in slides:
        frame = out_dir / f"slide-{n}.png"
        if not frame.exists() or frame.stat().st_size < 10_000:
            raise RunError(f"{deck}: capture missing slide {n}")


def resolve_decks(requested: str) -> list[str]:
    decks = narration.discover()
    if not requested:
        return decks
    if requested not in decks:
        raise RunError("requested deck is not a narrated deck")
    return [requested]


def process_deck(broker: Broker, deck: str, settings: dict, commit: str, rehearse: bool, work: Path) -> int:
    """Returns characters spoken (0 when skipped or rehearsed)."""
    narration.check_self_contained(deck)
    items = narration.extract((REPO_ROOT / deck / "index.html").read_text(encoding="utf-8"))
    if not items:
        log(f"{deck}: no narrated slides")
        return 0
    chars = sum(len(i["text"]) for i in items)
    fp = narration.fingerprint(deck, items, settings, narration.deck_files(deck))
    status, body = broker.post_json("/v1/deliver", {"mode": "preflight", "fingerprint": fp})
    if status != 200 or "exists" not in body:
        raise RunError(f"{deck}: delivery preflight failed ({status})")
    log(f"{deck}: {len(items)} narrated slides, {chars} characters")
    if body["exists"] and not rehearse:
        log(f"{deck}: unchanged, nothing to do")
        return 0
    if not rehearse:
        latest = speech_settings(broker)
        if chars > latest["remaining"]:
            raise RunError(f"{deck}: needs {chars} characters, {latest['remaining']} left this month")
    deck_dir = work / deck.replace("/", "-")
    frames = deck_dir / "frames"
    capture(deck, [i["slide"] for i in items], frames)
    segments, total = [], 0.0
    for i in items:
        audio = deck_dir / f"slide-{i['slide']}.mp3"
        if rehearse:
            silence(audio, max(1.0, len(i["text"]) / CHARS_PER_SECOND))
        else:
            status, data = broker.speak(i["text"])
            if status != 200 or not data:
                raise RunError(f"{deck}: speech refused on slide {i['slide']} ({status})")
            audio.write_bytes(data)
        seg = deck_dir / f"seg-{i['slide']:04d}.mp4"
        total += segment(frames / f"slide-{i['slide']}.png", audio, seg)
        segments.append(seg)
    name = narration.video_name(deck, datetime.now(ZoneInfo("America/Toronto")).strftime("%Y-%m-%d"), commit)
    video = deck_dir / name
    assemble(segments, video)
    duration = validate_video(video, total)
    log(f"{deck}: video {duration:.0f} s, {video.stat().st_size / 1e6:.1f} MB")
    if rehearse:
        log(f"{deck}: rehearsal passed, nothing spent or uploaded")
        return 0
    status, result = broker.upload(video, name, fp, deck, commit)
    if status != 200 or not (result.get("created") or result.get("exists")):
        raise RunError(f"{deck}: upload failed ({status})")
    log(f"delivered {name}" if result.get("created") else f"{deck}: already delivered")
    return chars


def cap_probe(broker: Broker) -> None:
    settings = speech_settings(broker)
    if settings["cap"] != 0:
        raise RunError("cap probe runs only while the broker cap is 0")
    status, _ = broker.speak("0123456789")
    if status != 429:
        raise RunError(f"cap probe expected 429, got {status}")
    log("cap probe passed: speech refused at cap 0")


def main() -> int:
    key = os.environ.pop("NARRATION_BROKER_KEY", "")
    mode = os.environ.get("NARRATION_MODE", "normal") or "normal"
    try:
        if mode not in ("normal", "rehearse", "cap_probe"):
            raise RunError("unknown mode")
        broker = Broker(os.environ.get("NARRATION_BROKER_URL", ""), key)
        if mode == "cap_probe":
            cap_probe(broker)
            return 0
        decks = resolve_decks(os.environ.get("NARRATION_DECK", "").strip())
        for tool in ("ffmpeg", "ffprobe", "node"):
            if not shutil.which(tool):
                raise RunError(f"{tool} not installed")
        settings = speech_settings(broker)
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True,
                                text=True, check=True).stdout.strip()
        with tempfile.TemporaryDirectory() as tmp:
            spent = sum(process_deck(broker, d, settings, commit, mode == "rehearse", Path(tmp)) for d in decks)
        log(f"done: {len(decks)} deck(s), {spent} characters spoken")
        return 0
    except (RunError, narration.NarrationError) as exc:
        log(f"failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

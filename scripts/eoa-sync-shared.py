#!/usr/bin/env python3
"""
eoa-sync-shared.py - push the canonical shared slides from
eoa_shared_slides.py out to every EOA meeting deck.

Idempotent. Only touches the four shared slides (Rules of Engagement,
Homework pull-latest reminder, Feedback, One Phrase Close) plus the
browser <title> and footer brand. Per-meeting frameworks, business
updates, and housekeeping dates are preserved untouched.

Usage:
    python3 ~/coaching-slides/scripts/eoa-sync-shared.py
    python3 ~/coaching-slides/scripts/eoa-sync-shared.py --check   # dry-run

Run after editing eoa_shared_slides.py so all 10 decks + onboarding +
owners-outcome-primer pick up the new canonical versions.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from eoa_shared_slides import (
    FOOTER,
    HOMEWORK_CTA_CSS,
    HOMEWORK_DEADLINE_CTA,
    HOMEWORK_PULL_LATEST_REMINDER,
    feedback_slide,
    opc_slide,
    rules_slide,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EOA_DIR = REPO_ROOT / "eoa"


def deck_paths() -> list[Path]:
    return sorted(
        [p for p in EOA_DIR.glob("*/index.html") if p.is_file()],
        key=lambda p: _sort_key(p.parent.name),
    )


def _sort_key(name: str) -> tuple[int, str]:
    if name.startswith("meeting-"):
        try:
            return (1, f"{int(name.split('-')[1]):03d}")
        except (IndexError, ValueError):
            return (1, name)
    return (0, name)


def sync_rules_of_engagement(html: str) -> tuple[str, bool]:
    """Replace the entire Rules of Engagement slide if present."""
    pattern = re.compile(
        r'<section class="slide" aria-label="Rules of Engagement">'
        r'(?:(?!</section>).)*?</section>',
        re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return html, False
    old = match.group(0)
    time_match = re.search(
        r'<span class="time-indicator">([^<]+)</span>\s*</section>', old
    )
    time_indicator = time_match.group(1) if time_match else "(5 min / 10)"
    new = rules_slide(time_indicator).lstrip()
    if old == new:
        return html, False
    return html.replace(old, new, 1), True


def sync_feedback(html: str) -> tuple[str, bool]:
    pattern = re.compile(
        r'<section class="slide" aria-label="Feedback">'
        r'(?:(?!</section>).)*?</section>',
        re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return html, False
    old = match.group(0)
    time_match = re.search(
        r'<span class="time-indicator">([^<]+)</span>\s*</section>', old
    )
    time_indicator = time_match.group(1) if time_match else "(3 min / 0)"
    new = feedback_slide(time_indicator).lstrip()
    if old == new:
        return html, False
    return html.replace(old, new, 1), True


def sync_one_phrase_close(html: str) -> tuple[str, bool]:
    pattern = re.compile(
        r'<section class="slide" aria-label="One Phrase Close">'
        r'(?:(?!</section>).)*?</section>',
        re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return html, False
    old = match.group(0)
    time_match = re.search(
        r'<span class="time-indicator">([^<]+)</span>\s*</section>', old
    )
    time_indicator = time_match.group(1) if time_match else "(3 min / 240)"
    new = opc_slide(time_indicator).lstrip()
    if old == new:
        return html, False
    return html.replace(old, new, 1), True


def sync_homework_reminder(html: str) -> tuple[str, bool]:
    """Ensure the pull-latest reminder is present inside the Homework
    slide's col-image. No-op if already present."""
    if "Pull the current version each time" in html:
        return html, False
    hw_match = re.search(
        r'(<section class="slide" aria-label="Homework">'
        r'(?:(?!</section>).)*?'
        r')(<div class="col-image reveal">)(\s*<img[^>]*alt="[^"]*[Hh]omework[^"]*"[^>]*>)(\s*</div>)'
        r'((?:(?!</section>).)*?</section>)',
        html,
        re.DOTALL,
    )
    if not hw_match:
        return html, False
    before, col_open, img_tag, col_close, after = hw_match.groups()
    new_col_open = (
        '<div class="col-image reveal" '
        'style="display: flex; flex-direction: column; gap: 1rem; align-items: center;">'
    )
    replacement = (
        before
        + new_col_open
        + img_tag
        + "\n                "
        + HOMEWORK_PULL_LATEST_REMINDER
        + col_close
        + after
    )
    return html.replace(hw_match.group(0), replacement), True


_MURAL_LINE = (
    r"Add finalized artifacts to Mural and email byron@darlison\.com "
    r"at least five business days before next meeting"
)


def sync_homework_cta_css(html: str) -> tuple[str, bool]:
    """Ensure the .homework-cta highlight CSS is in the <style>. No-op if present."""
    if "li.homework-cta {" in html:
        return html, False
    pattern = re.compile(r"(\n[ \t]*\.homework-list \.link-prompt \{[^\n]*\})")
    m = pattern.search(html)
    if not m:
        return html, False
    return html.replace(m.group(1), m.group(1) + "\n" + HOMEWORK_CTA_CSS, 1), True


def sync_homework_cta(html: str) -> tuple[str, bool]:
    """Inject the deadline CTA at the top of the Homework slide. No-op if present."""
    if '<li class="homework-cta">' in html:
        return html, False
    pattern = re.compile(
        r'(<section class="slide" aria-label="Homework">\s*<div class="slide-content">)'
        r'(\s*<div class="two-col">)'
    )
    m = pattern.search(html)
    if not m:
        return html, False
    replacement = m.group(1) + "\n            " + HOMEWORK_DEADLINE_CTA + m.group(2)
    return html.replace(m.group(0), replacement, 1), True


def sync_homework_drop_mural(html: str) -> tuple[str, bool]:
    """Remove the now-redundant 'Add finalized artifacts to Mural...' deadline text
    (the top CTA carries the deadline). Handles three shapes:
      1. a standalone submission <ul> whose only child is the Mural line,
      2. a bare <li> Mural line inside a larger list,
      3. the deadline sentence appended to a deliverable bullet
         (e.g. 'Function Scorecards. Add finalized artifacts to Mural ... meeting.')."""
    changed = False
    # Form 1: a ul whose only child is the Mural submission line
    new, n = re.subn(
        r'\n[ \t]*<ul class="homework-list"[^>]*>\s*<li>' + _MURAL_LINE + r"</li>\s*</ul>",
        "",
        html,
    )
    if n:
        html, changed = new, True
    # Form 2: a bare li that is only the Mural line
    new, n = re.subn(r"\n[ \t]*<li>" + _MURAL_LINE + r"</li>", "", html)
    if n:
        html, changed = new, True
    # Form 3: the deadline sentence appended to a deliverable bullet
    new, n = re.subn(r"\.\s*" + _MURAL_LINE + r"\.", "", html)
    if n:
        html, changed = new, True
    return html, changed


def sync_homework_trim_eoa_prep(html: str) -> tuple[str, bool]:
    """Trim 'Run the EOA Prep Prompt and email it...' down to 'Run the EOA Prep Prompt.'"""
    pattern = re.compile(
        r'(<li>Run the <a href="https://www\.darlison\.com/eoa-prep-prompt/"[^>]*>'
        r"EOA Prep Prompt</a>) and email it to byron@darlison\.com "
        r"at least five business days before next meeting(</li>)"
    )
    new, n = pattern.subn(r"\1\2", html)
    return (new, True) if n else (html, False)


# Homework-slide CTA pipeline — meeting-N decks only (not onboarding / primer).
CTA_SYNCS = [
    ("homework-cta-css", sync_homework_cta_css),
    ("homework-cta", sync_homework_cta),
    ("drop-mural", sync_homework_drop_mural),
    ("trim-eoa-prep", sync_homework_trim_eoa_prep),
]


def sync_footer_brand(html: str) -> tuple[str, bool]:
    """Normalize all slide footers to the canonical EOA string."""
    canonical = f'<span class="slide-footer">{FOOTER}</span>'
    pattern = re.compile(r'<span class="slide-footer">[^<]*</span>')
    new_html, n = pattern.subn(canonical, html)
    return new_html, new_html != html


def sync_browser_title(html: str, meeting_label: str) -> tuple[str, bool]:
    """Normalize <title> to 'EOA Meeting N' (or leave as-is for non-meeting decks)."""
    match = re.match(r"^meeting-(\d+)$", meeting_label)
    if not match:
        return html, False
    n = int(match.group(1))
    canonical = f"<title>EOA Meeting {n}</title>"
    new_html, subs = re.subn(r"<title>[^<]*</title>", canonical, html, count=1)
    return new_html, subs > 0 and new_html != html


SYNCS = [
    ("rules-of-engagement", sync_rules_of_engagement),
    ("feedback", sync_feedback),
    ("one-phrase-close", sync_one_phrase_close),
    ("homework-reminder", sync_homework_reminder),
    ("footer-brand", sync_footer_brand),
]


def main(check_only: bool = False) -> int:
    changed_decks = 0
    for path in deck_paths():
        deck_name = path.parent.name
        html = path.read_text()
        original = html
        applied: list[str] = []
        for label, fn in SYNCS:
            html, did_change = fn(html)
            if did_change:
                applied.append(label)
        if re.match(r"meeting-\d+$", deck_name):
            for label, fn in CTA_SYNCS:
                html, did_change = fn(html)
                if did_change:
                    applied.append(label)
        html, title_changed = sync_browser_title(html, deck_name)
        if title_changed:
            applied.append("browser-title")
        if html == original:
            print(f"CLEAN {deck_name}")
            continue
        changed_decks += 1
        if check_only:
            print(f"DRIFT {deck_name}: {', '.join(applied)}")
        else:
            path.write_text(html)
            print(f"SYNC  {deck_name}: {', '.join(applied)}")
    print()
    if check_only:
        print(f"{changed_decks} deck(s) would change. Re-run without --check to apply.")
        return 1 if changed_decks else 0
    print(f"{changed_decks} deck(s) updated.")
    return 0


if __name__ == "__main__":
    check = "--check" in sys.argv
    sys.exit(main(check_only=check))

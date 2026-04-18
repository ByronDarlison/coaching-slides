#!/usr/bin/env python3
"""
eoa_shared_slides.py - canonical HTML for every slide that is IDENTICAL
across all 10 EOA meeting decks. This is the single source of truth.

Use `eoa-sync-shared.py` to push changes from these functions out to
all meeting decks (idempotent; only touches the slides listed below).

Per-meeting content (framework slides, business-updates prompts,
housekeeping dates, homework specifics) lives in each deck's
`index.html` and is NOT touched by the sync.

Covered shared elements:
    - Rules of Engagement slide (with Rules 7+8)
    - Homework footer: green-bordered pull-latest reminder
    - Feedback slide (before One Phrase Close)
    - One Phrase Close slide
    - Browser <title> (genericized to "EOA Meeting N")
    - Footer brand ("darlison.com | Metronomics(TM) Coaching | EO Accelerator")

Not covered (intentionally per-meeting):
    - Title slide text and image
    - One Word Barometer subtitle (meeting-specific framing)
    - Business Updates prompts
    - Framework/deliverable slides
    - Homework slide contents (frameworks/books)
    - Housekeeping slide (cohort dates live here per design)
"""

from __future__ import annotations


FOOTER = "darlison.com | Metronomics&#8482; Coaching | EO Accelerator"


RULES_OF_ENGAGEMENT_SLIDE = '''    <section class="slide" aria-label="Rules of Engagement">
        <div class="slide-content">
            <div class="two-col">
            <div class="col-text">
            <h1 class="slide-title reveal">Rules of Engagement</h1>
            <ul class="rules-list">
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M12 2L15 8.5L22 9.5L17 14.5L18 21.5L12 18.5L6 21.5L7 14.5L2 9.5L9 8.5Z"/></svg></span>
                    Challenge yourself. Challenge each other.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>
                    Discussion and collaboration. Your best contribution.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span>
                    Be present in the room.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></span>
                    No blame, no shame. No dumb questions.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg></span>
                    Don't ignore the brutal facts. Bring them forward.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></span>
                    Confidentiality. What happens here stays here.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span>
                    Feedback runs both ways. Tell me what didn't land.
                </li>
                <li class="reveal">
                    <span class="rule-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#326AB5" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span>
                    Articles and prompts are living. Always pull the latest from darlison.com, not a saved copy.
                </li>
            </ul>
            </div>
            <div class="col-image reveal">
                <img src="../../shared/assets/rules-of-engagement.png" alt="Rules of Engagement">
            </div>
            </div>
        </div>
        <span class="slide-footer">{footer}</span>
        <span class="time-indicator">{time}</span>
    </section>'''


HOMEWORK_PULL_LATEST_REMINDER = '''<p style="margin-top: 0.25rem; padding: 0.55rem 0.8rem; background: rgba(84, 181, 112, 0.08); border-left: 3px solid #54B570; border-radius: 4px; font-style: italic; font-size: var(--small-size); color: var(--text-primary); max-width: 90%;">Reminder: everything on darlison.com updates continuously. Pull the current version each time. Don't work from a saved copy.</p>'''


FEEDBACK_SLIDE = '''    <section class="slide" aria-label="Feedback">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
                    <h1 class="slide-title reveal">Feedback</h1>
                    <p class="slide-subtitle reveal">30 seconds each.</p>
                    <ol class="reveal" style="padding-left: 1.5rem; display: flex; flex-direction: column; gap: clamp(0.6rem, 1.4vh, 1.1rem); margin-top: var(--content-gap); font-size: var(--body-size); line-height: 1.45; color: var(--text-primary);">
                        <li>What landed today?</li>
                        <li>What confused you, or where did the materials fail you?</li>
                        <li>What would have made this session more useful?</li>
                    </ol>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/feedback.png" alt="Feedback">
                </div>
            </div>
        </div>
        <span class="slide-footer">{footer}</span>
        <span class="time-indicator">{time}</span>
    </section>'''


ONE_PHRASE_CLOSE_SLIDE = '''    <section class="slide" aria-label="One Phrase Close">
        <div class="slide-content">
            <div class="two-col">
                <div class="col-text">
                    <h1 class="slide-title reveal">One Phrase Close</h1>
                    <p class="close-instruction reveal">5 words or less.</p>
                    <p class="close-question reveal">How do you feel right now?</p>
                </div>
                <div class="col-image reveal">
                    <img src="../../shared/assets/one-phrase-close.png" alt="One Phrase Close">
                </div>
            </div>
        </div>
        <span class="slide-footer">{footer}</span>
        <span class="time-indicator">{time}</span>
    </section>'''


def rules_slide(time_indicator: str) -> str:
    return RULES_OF_ENGAGEMENT_SLIDE.format(footer=FOOTER, time=time_indicator)


def feedback_slide(time_indicator: str) -> str:
    return FEEDBACK_SLIDE.format(footer=FOOTER, time=time_indicator)


def opc_slide(time_indicator: str) -> str:
    return ONE_PHRASE_CLOSE_SLIDE.format(footer=FOOTER, time=time_indicator)

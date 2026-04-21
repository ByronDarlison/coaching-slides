#!/usr/bin/env python3
"""
slide-test.py — Tier 1 static test runner for coaching slide decks.

Runs a suite of no-rendering static checks against a single deck HTML:

    1. Image audit: every <img src> resolves (local file exists / HTTP 200).
    2. Link audit: every <a href> works.
    3. Time chain: per-slide times sum to the cumulative, no drift.
    4. Structure: every <section class="slide"> has required elements.
    5. Style: no em dashes, no British spelling, OBT spelled out.
    6. Cohort-generic: no specific group numbers, dates, or day references.
    7. Homework deadline: Homework slide carries the canonical deadline phrase.

Usage:
    python3 ~/ai-config/scripts/slide-test.py <path/to/deck/index.html>

Exit code 0 on all-pass, 1 on any failure.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

TIMEOUT_SECONDS = 6
USER_AGENT = "slide-test/1.0"

# Style rules. Pattern → human-readable violation.
STYLE_RULES: list[tuple[str, str]] = [
    (r"—", "em dash (use period, comma, colon, parens, or conjunction)"),
    (r"\bcolour\b", "British spelling 'colour' (use 'color')"),
    (r"\bcentre\b", "British spelling 'centre' (use 'center')"),
    (r"\borganisation\b", "British spelling 'organisation' (use 'organization')"),
    (r"\brealise\b", "British spelling 'realise' (use 'realize')"),
    (r"\bfavourite\b", "British spelling 'favourite' (use 'favorite')"),
    (r"\bbehaviour\b", "British spelling 'behaviour' (use 'behavior')"),
]

# Cohort-generic rules. Pattern → human-readable violation.
# Applied to HTML with comments stripped (so the comment block at top doesn't trip it).
COHORT_PATTERNS: list[tuple[str, str]] = [
    (r"Group\s+\d+\b", "specific group number"),
    (
        r"\b(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+\d",
        "specific month + day",
    ),
    (r"on the \d+(st|nd|rd|th)\b", "specific day reference ('on the 21st')"),
    (r"by (Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", "specific weekday reference"),
]

HOMEWORK_DEADLINE_PHRASE = "at least five business days before next meeting"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def fetch_ok(url: str) -> tuple[bool, str]:
    """Return (ok, status-or-error) for an HTTP/HTTPS URL, trying HEAD then GET."""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as r:
                status = r.status
                if 200 <= status < 400:
                    return True, f"HTTP {status}"
                # Redirects are usually followed by urlopen; a 4xx/5xx is real.
                if method == "GET":
                    return False, f"HTTP {status}"
        except Exception as e:
            if method == "GET":
                return False, f"{type(e).__name__}: {e}"
            # else HEAD failed; fall through to GET
    return False, "unreachable"


def check_images(html: str, base_dir: Path) -> tuple[list[str], list[str]]:
    oks, issues = [], []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        if src.startswith(("http://", "https://")):
            ok, detail = fetch_ok(src)
            (oks if ok else issues).append(f"{src}  ({detail})")
        else:
            path = (base_dir / src).resolve()
            if path.is_file():
                oks.append(f"{src}  →  {path}")
            else:
                issues.append(f"{src}  →  file missing at {path}")
    return oks, issues


def check_links(html: str, base_dir: Path) -> tuple[list[str], list[str]]:
    oks, issues = [], []
    # <a ... href="..."> — be strict about the opening tag to avoid <link> hits.
    hrefs = set(re.findall(r'<a\s[^>]*href="([^"]+)"', html))
    for href in sorted(hrefs):
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        if href.startswith(("http://", "https://")):
            ok, detail = fetch_ok(href)
            (oks if ok else issues).append(f"{href}  ({detail})")
        else:
            path = (base_dir / href).resolve()
            if path.is_file() or path.is_dir():
                oks.append(f"{href}  →  {path}")
            else:
                issues.append(f"{href}  →  file missing at {path}")
    return oks, issues


def check_time_chain(html: str) -> tuple[int, list[str]]:
    issues: list[str] = []
    indicators = re.findall(
        r'<span class="time-indicator">\(([^)]+)\)</span>', html
    )
    last_cum = 0
    for i, t in enumerate(indicators, 1):
        if "/" in t:
            per_s, cum_s = [x.strip() for x in t.split("/", 1)]
            per_m = re.search(r"\d+", per_s)
            cum_m = re.search(r"\d+", cum_s)
            if not (per_m and cum_m):
                issues.append(f"Indicator {i}: cannot parse '{t}'")
                continue
            per_min = int(per_m.group())
            cum_val = int(cum_m.group())
        else:
            cum_m = re.search(r"\d+", t)
            if not cum_m:
                issues.append(f"Indicator {i}: cannot parse '{t}'")
                continue
            cum_val = int(cum_m.group())
            per_min = cum_val - last_cum  # inferred
        expected = last_cum + per_min
        # Special case: the final "ceremonial" close often holds the same
        # cumulative as the preceding slide ("in the last minute"). Allow that.
        if expected != cum_val and not (i == len(indicators) and cum_val == last_cum):
            issues.append(
                f"Indicator {i}: +{per_min} → {cum_val} (expected {expected})"
            )
        last_cum = cum_val
    return len(indicators), issues


def check_structure(html: str) -> tuple[int, list[str]]:
    issues: list[str] = []
    sections = re.findall(
        r'<section class="slide"[^>]*>(.*?)</section>', html, re.DOTALL
    )
    if len(sections) < 3:
        issues.append(f"Only {len(sections)} slides (expected ≥3)")
    for i, sec in enumerate(sections, 1):
        if "slide-content" not in sec:
            issues.append(f"Slide {i}: missing .slide-content")
        if "slide-title" not in sec and "<h1" not in sec:
            issues.append(f"Slide {i}: missing .slide-title / <h1>")
    return len(sections), issues


def check_style(html: str) -> list[str]:
    issues: list[str] = []
    for pattern, desc in STYLE_RULES:
        for m in re.finditer(pattern, html):
            start = max(0, m.start() - 35)
            end = min(len(html), m.end() + 35)
            ctx = html[start:end].replace("\n", " ")
            issues.append(f"{desc}: …{ctx}…")
    # OBT check: if "OBT" appears at all, ensure "one big thing (OBT)" is spelled
    # out at least once in the document.
    if re.search(r"\bOBT\b", html) and "one big thing (OBT)" not in html:
        issues.append(
            "OBT used without expanding it as 'one big thing (OBT)' somewhere in the deck"
        )
    return issues


def check_cohort_generic(html: str) -> list[str]:
    issues: list[str] = []
    # Strip comments so the "cohort-independent" header comment doesn't trigger.
    scrubbed = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # Whitelist the Housekeeping slide — that is the canonical home for
    # per-cohort dates (Learning Day, next meeting, etc.) so those references
    # should not fail this check.
    scrubbed = re.sub(
        r'<section class="slide"[^>]*aria-label="Housekeeping[^"]*"[^>]*>.*?</section>',
        "",
        scrubbed,
        flags=re.DOTALL,
    )
    for pattern, desc in COHORT_PATTERNS:
        for m in re.finditer(pattern, scrubbed):
            start = max(0, m.start() - 25)
            end = min(len(scrubbed), m.end() + 25)
            ctx = scrubbed[start:end].replace("\n", " ")
            issues.append(f"{desc}: …{ctx}…")
    return issues


def check_homework_deadline(html: str) -> list[str]:
    issues: list[str] = []
    # Find every slide with aria-label containing "Homework" and check each.
    for m in re.finditer(
        r'<section class="slide"[^>]*aria-label="Homework[^"]*"[^>]*>.*?</section>',
        html,
        re.DOTALL,
    ):
        slide = m.group()
        if HOMEWORK_DEADLINE_PHRASE not in slide:
            issues.append(
                f"Homework slide missing required phrase: '{HOMEWORK_DEADLINE_PHRASE}'"
            )
    return issues


# Deliverable-slide titles that DON'T need article+prompt links.
# Structural slides that carry a symbol-badge but don't map to a
# darlison.com article/prompt pair.
NO_LINK_REQUIRED = {
    "Standing Review Block",
    "Constitution",
    "Business Lifelines",
    "Owner's Outcome Reflection",
    "Personal Outcome",
    "Share Your Conclusions",
    "Synthesis & Conclusions",
    "Metronomics Operating System",
    "Meeting Cadence",
}

# Deliverables where the darlison.com article and/or AI prompt has not
# yet been written. These slides are allowed to lack the article/prompt
# links for now. Remove entries here as the articles ship; the test
# will then enforce link presence.
PENDING_ARTICLE = {
    "Market Map",
    "Attribution Map",
    "Activity Fit Map",
    "Activity Fit Map (Differentiators)",
    "Swimlanes",
    "12-Month Widget-Based Forecast",
    "Quarterly Coaching Reviews",
    "Positioning Statement (Moore)",
    "Value Proposition (Moore)",
    "36-Month Rolling Forecast",
    "Flywheel",
    "Brand Promise with Guarantee",
    "Secret Sauce",
    "Skip-Level Reviews",
    "Business Model Canvas",
    "BrandScript",
    "Porter's Five Forces",
    "Consumption Chain Mapping",
    # Function Scorecards has an article but no prompt yet.
    "Function Scorecards",
}


def check_deliverable_links(html: str) -> tuple[list[str], int]:
    """Every slide that carries a symbol-badge (★ Introduced, ▲ Coach and
    finalize, ✓ Review and confirm, ■ Rebuilt) should also carry a
    slide-links block with article + AI prompt links, unless the slide is
    structurally exempt (NO_LINK_REQUIRED) or pending article creation
    (PENDING_ARTICLE). Returns (issues, pending_count)."""
    issues: list[str] = []
    pending_count = 0
    for m in re.finditer(
        r'<section class="slide"[^>]*>(?:(?!</section>).)*?</section>',
        html,
        re.DOTALL,
    ):
        block = m.group(0)
        if "symbol-badge" not in block:
            continue
        title_match = re.search(r'<h1 class="slide-title[^>]*>([^<]+)</h1>', block)
        title = title_match.group(1).strip() if title_match else "?"
        if title in NO_LINK_REQUIRED:
            continue
        has_article = 'class="link-article"' in block or re.search(
            r'href="[^"]*darlison\.com[^"]*"[^>]*>Article<', block
        )
        has_prompt = 'class="link-prompt"' in block
        if has_article and has_prompt:
            continue
        if title in PENDING_ARTICLE:
            pending_count += 1
            continue
        missing = []
        if not has_article:
            missing.append("Article")
        if not has_prompt:
            missing.append("AI Prompt")
        issues.append(
            f"Deliverable slide '{title}' missing: {', '.join(missing)}"
        )
    return issues, pending_count


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    deck_path = Path(sys.argv[1]).expanduser().resolve()
    if not deck_path.is_file():
        print(f"ERROR: deck not found: {deck_path}")
        return 2

    html = deck_path.read_text()
    base_dir = deck_path.parent

    print(f"Testing: {deck_path}")
    print("=" * 78)

    all_pass = True

    def report(title: str, issues: list[str], ok_summary: str) -> None:
        nonlocal all_pass
        print(f"\n[{title}]")
        if issues:
            all_pass = False
            for issue in issues:
                print(f"  FAIL  {issue}")
            print(f"  ({len(issues)} issue(s))")
        else:
            print(f"  PASS  {ok_summary}")

    img_ok, img_issues = check_images(html, base_dir)
    report("1/8 Image audit", img_issues, f"all {len(img_ok)} image(s) resolve")

    link_ok, link_issues = check_links(html, base_dir)
    report("2/8 Link audit", link_issues, f"all {len(link_ok)} link(s) resolve")

    n_ind, time_issues = check_time_chain(html)
    report(
        "3/8 Time chain",
        time_issues,
        f"all {n_ind} time indicator(s) form a clean chain",
    )

    n_slides, struct_issues = check_structure(html)
    report(
        "4/8 Structure",
        struct_issues,
        f"{n_slides} slide(s), all structurally complete",
    )

    style_issues = check_style(html)
    report(
        "5/8 Style rules",
        style_issues,
        "no em dashes, British spelling, or OBT spell-out issues",
    )

    cohort_issues = check_cohort_generic(html)
    report(
        "6/8 Cohort-generic",
        cohort_issues,
        "no cohort-specific dates, months, or group numbers",
    )

    hw_issues = check_homework_deadline(html)
    report(
        "7/8 Homework deadline phrase",
        hw_issues,
        "Homework slide carries the canonical deadline phrase",
    )

    link_req_issues, pending = check_deliverable_links(html)
    ok_msg = "every deliverable slide carries article and AI prompt links"
    if pending:
        ok_msg += f" ({pending} slide(s) pending article - skipped)"
    report(
        "8/8 Deliverable article + AI prompt links",
        link_req_issues,
        ok_msg,
    )

    print()
    print("=" * 78)
    print("RESULT:", "PASS" if all_pass else "FAIL")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

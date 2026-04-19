#!/usr/bin/env python3
"""
article-shipped.py - propagate a newly-shipped darlison.com article or
AI prompt into every slide that references the deliverable.

Usage:
    python3 scripts/article-shipped.py "<Deliverable>" \\
        --article <article_url> \\
        [--prompt <prompt_url>]

Example:
    python3 scripts/article-shipped.py "Core Customer Analysis" \\
        --article https://www.darlison.com/who-is-your-most-valuable-customer/ \\
        --prompt https://www.darlison.com/core-customer-discovery-prompt/

What it does:
    1. Updates DELIVERABLES entry in build_new_slideshows.py.
    2. Adds article= / prompt= kwargs to the first D("<Deliverable>", ...)
       call in build_slideshows.py that doesn't already have them.
    3. Regenerates monthly M3-M23 via both build scripts.
    4. Patches every eoa/meeting-*/index.html that has a deliverable
       slide matching the name but no slide-links block, injecting
       the canonical <div class="slide-links"> block.
    5. Removes the deliverable from PENDING_ARTICLE in slide-test.py
       (only when both article AND prompt are now present, unless
       --force-unpend is passed).
    6. Runs Tier 1 slide-test on every deck and reports pass/fail.

After the script completes successfully:
    git add -A
    git commit -m "Add links for <Deliverable> [baseline-refresh]"
    git push

The [baseline-refresh] marker tells visual-regression CI to auto-refresh
Linux baselines in the same workflow run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD_MONTHLY = REPO / "build_slideshows.py"
BUILD_NEW = REPO / "build_new_slideshows.py"
SLIDE_TEST = REPO / "scripts" / "slide-test.py"
EOA_DIR = REPO / "eoa"


def update_build_new(name: str, article: str, prompt: str | None) -> str:
    """Update the DELIVERABLES entry in build_new_slideshows.py.

    Finds the `"<name>":` key, locates the matching `},` that closes the
    entry, and replaces the article/prompt URL values line-by-line.

    Returns "updated", "no-change" (entry found but URLs already match),
    or "not-found" (no entry for that name).
    """
    src = BUILD_NEW.read_text()
    key_line = f'"{name}":'
    start = src.find(key_line)
    if start == -1:
        return "not-found"
    end = src.find("},", start)
    if end == -1:
        return "not-found"
    end += 2
    block = src[start:end]
    new_block = re.sub(
        r'("article":\s*)"[^"]*"',
        f'\\1"{article}"',
        block,
        count=1,
    )
    if prompt:
        new_block = re.sub(
            r'("prompt":\s*)"[^"]*"',
            f'\\1"{prompt}"',
            new_block,
            count=1,
        )
    if new_block == block:
        return "no-change"
    BUILD_NEW.write_text(src[:start] + new_block + src[end:])
    return "updated"


def _find_d_call(src: str, start: int) -> int:
    """Starting from just past `D("<name>"`, return the index one past
    the matching closing `)`. Raises ValueError if unbalanced."""
    depth = 1
    i = start
    in_string = False
    string_char = ""
    while i < len(src) and depth > 0:
        c = src[i]
        if in_string:
            if c == "\\" and i + 1 < len(src):
                i += 2
                continue
            if c == string_char:
                in_string = False
        else:
            if c in ('"', "'"):
                in_string = True
                string_char = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
        i += 1
    if depth != 0:
        raise ValueError("unbalanced parens")
    return i


def update_build_monthly(name: str, article: str, prompt: str | None) -> int:
    """Add article= and prompt= kwargs to every D("<name>", ...) call in
    build_slideshows.py that doesn't already have them. Returns the
    number of calls updated."""
    src = BUILD_MONTHLY.read_text()
    count = 0
    pattern = re.compile(r'D\(\s*"' + re.escape(name) + r'"')
    parts: list[str] = []
    cursor = 0
    for m in pattern.finditer(src):
        start = m.start()
        call_end = _find_d_call(src, m.end())  # one past the final ')'
        call_block = src[start:call_end]
        insertion = ""
        if article and "article=" not in call_block:
            insertion += f',\n          article="{article}"'
        if prompt and "prompt=" not in call_block:
            insertion += f',\n          prompt="{prompt}"'
        if not insertion:
            parts.append(src[cursor:call_end])
            cursor = call_end
            continue
        # Insert just before the final ')' of this D() call.
        parts.append(src[cursor:call_end - 1])
        parts.append(insertion)
        parts.append(src[call_end - 1:call_end])
        cursor = call_end
        count += 1
    parts.append(src[cursor:])
    if count > 0:
        BUILD_MONTHLY.write_text("".join(parts))
    return count


def regenerate_monthly() -> None:
    for script in [BUILD_MONTHLY, BUILD_NEW]:
        subprocess.run(
            ["python3", str(script)],
            cwd=REPO,
            check=True,
            capture_output=True,
        )


SLIDE_LINKS_BLOCK = '''                    <div class="slide-links reveal">
                        <a href="{article}" target="_blank" rel="noopener" class="link-article">Article</a>
                        <a href="{prompt}" target="_blank" rel="noopener" class="link-prompt">&#10022; AI Prompt</a>
                    </div>'''


def patch_eoa_decks(name: str, article: str, prompt: str | None) -> list[str]:
    """Inject slide-links block into every EOA deck that has a deliverable
    slide matching the name but no existing links block. Returns the list
    of decks patched."""
    if not prompt:
        # Without a prompt URL, the canonical block can't be rendered.
        # The EOA decks can still be updated by hand later.
        return []
    patched: list[str] = []
    for deck_path in sorted(EOA_DIR.glob("*/index.html")):
        html = deck_path.read_text()
        changed = False
        # Locate each section with the deliverable title.
        for m in re.finditer(
            r'<section class="slide"[^>]*>(?:(?!</section>).)*?</section>',
            html,
            re.DOTALL,
        ):
            block = m.group(0)
            title_match = re.search(
                r'<h1 class="slide-title[^>]*>([^<]+)</h1>', block
            )
            if not title_match:
                continue
            if title_match.group(1).strip() != name:
                continue
            if "slide-links" in block:
                continue
            # Insert the links block just before the closing </ul> or the
            # first </div> that closes the col-text column. Safest: just
            # before the closing </div> of the col-text.
            col_text_close = re.search(
                r'(<ul[^>]*>.*?</ul>\s*)(\s*</div>\s*<div class="col-image)',
                block,
                re.DOTALL,
            )
            if col_text_close:
                links = SLIDE_LINKS_BLOCK.format(article=article, prompt=prompt)
                new_block = block[:col_text_close.end(1)] + "\n" + links + block[col_text_close.end(1):]
                html = html.replace(block, new_block, 1)
                changed = True
        if changed:
            deck_path.write_text(html)
            patched.append(deck_path.parent.name)
    return patched


def unpend(name: str, have_article: bool, have_prompt: bool, force: bool) -> str:
    """Remove `name` from PENDING_ARTICLE in slide-test.py.

    Returns one of: "removed", "not-in-list", "still-pending", "no-change".
    """
    src = SLIDE_TEST.read_text()
    pattern = re.compile(
        r'(\nPENDING_ARTICLE\s*=\s*\{[^}]*?)\n\s*"' + re.escape(name) + r'",?\s*(?=\n)',
        re.DOTALL,
    )
    match = pattern.search(src)
    if not match:
        return "not-in-list"
    if not force and not (have_article and have_prompt):
        return "still-pending"
    new_src = pattern.sub(r'\1', src, count=1)
    if new_src == src:
        return "no-change"
    SLIDE_TEST.write_text(new_src)
    # Keep the ai-config dev copy in sync if it exists.
    ai_config_copy = Path.home() / "ai-config" / "scripts" / "slide-test.py"
    if ai_config_copy.is_file():
        ai_config_copy.write_text(new_src)
    return "removed"


def run_tier1() -> tuple[int, int]:
    passes = fails = 0
    for deck in sorted(list((REPO / "monthly").glob("*/index.html")) + list((REPO / "eoa").glob("*/index.html"))):
        r = subprocess.run(
            ["python3", str(SLIDE_TEST), str(deck)],
            capture_output=True,
            text=True,
        )
        if "RESULT: PASS" in r.stdout:
            passes += 1
        else:
            fails += 1
            print(f"  FAIL  {deck.relative_to(REPO)}")
    return passes, fails


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("name", help="Deliverable name (must match slide title exactly)")
    p.add_argument("--article", required=True, help="Article URL on darlison.com")
    p.add_argument("--prompt", help="AI prompt URL on darlison.com (optional if only article shipped)")
    p.add_argument(
        "--force-unpend",
        action="store_true",
        help="Remove from PENDING_ARTICLE even if only one of article/prompt is provided",
    )
    args = p.parse_args()

    print(f"Deliverable: {args.name}")
    print(f"Article:     {args.article}")
    print(f"Prompt:      {args.prompt or '(not shipped)'}")
    print()

    print("1. Updating build_new_slideshows.py DELIVERABLES...")
    status = update_build_new(args.name, args.article, args.prompt)
    msg = {
        "updated": "   OK",
        "no-change": "   SKIP  entry already has these URLs",
        "not-found": f"   SKIP  no DELIVERABLES entry matched '{args.name}'",
    }
    print(msg.get(status, f"   {status}"))

    print("2. Updating build_slideshows.py D() calls...")
    n = update_build_monthly(args.name, args.article, args.prompt)
    if n > 0:
        print(f"   OK  updated {n} D() call(s)")
    else:
        print("   SKIP  no D() calls needed updating")

    print("3. Regenerating monthly M3-M23...")
    regenerate_monthly()
    print("   OK")

    print("4. Patching EOA decks...")
    patched = patch_eoa_decks(args.name, args.article, args.prompt)
    if patched:
        print(f"   OK  patched: {', '.join(patched)}")
    elif not args.prompt:
        print("   SKIP  no prompt URL; EOA decks need manual update")
    else:
        print("   SKIP  no EOA decks matched or all already have links")

    print("5. Removing from PENDING_ARTICLE skip-list...")
    status = unpend(args.name, bool(args.article), bool(args.prompt), args.force_unpend)
    messages = {
        "removed": "   OK",
        "not-in-list": f"   SKIP  '{args.name}' not in PENDING_ARTICLE (already enforced)",
        "still-pending": "   SKIP  still pending (need both article and prompt, or --force-unpend)",
        "no-change": "   SKIP  no change",
    }
    print(messages.get(status, f"   {status}"))

    print("6. Tier 1 verification...")
    passes, fails = run_tier1()
    print(f"   {passes} pass / {fails} fail")
    print()
    if fails > 0:
        print("Tier 1 failures above. Review and fix before committing.")
        return 1
    print("All decks pass. Next steps:")
    print("    cd ~/coaching-slides")
    print(f'    git add -A && git commit -m "Add links for {args.name} [baseline-refresh]"')
    print("    git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())

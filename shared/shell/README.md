# Shared slideshow shell

An earlier copy of the shell in [`source/shared/deck`](../../source/shared/deck/), used by the EOA meeting decks.

GitHub Pages serves this copy with the coaching decks. A deck loads nothing from another repository at runtime.

## Files

- `shell.css` is the stage, tokens, and controls.
- `shell.js` is navigation, notes, and full screen.
- `fonts/` is local Geist Sans and Geist Mono.

## Use it

New EOA meeting decks link this folder from the deck page.

EOA Meeting 4 is the first deck on this shell:

https://byrondarlison.github.io/coaching-slides/eoa/meeting-4/

From `eoa/meeting-4/index.html` the links are:

- `../../shared/shell/shell.css`
- `../../shared/shell/shell.js`
- `../../shared/shell/fonts/geist-latin.woff2`
- `../../shared/shell/fonts/geist-mono-latin.woff2`

Set `data-title` on every slide. Set `data-group` on the first slide of each section. Put presenter words in `speaker-notes`.

## Visual rules

Appearance follows the house standard:

[`source/SLIDE-VISUAL-STANDARD.md`](../../source/SLIDE-VISUAL-STANDARD.md)

Shell how-to:

[`source/shared/README.md`](../../source/shared/README.md)

Do not load fonts from the network.

## Notes panel and video script (17-Oct-2026)

Press N to open the notes. The panel pushes the slide aside instead of covering it. When a slide has `<aside class="video-script">`, the panel shows it under the notes, headed "Video script".

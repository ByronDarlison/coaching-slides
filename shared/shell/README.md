# Shared slideshow shell

Vendored from [ByronDarlison/ai-config](https://github.com/ByronDarlison/ai-config) `darlison/presentations/shared/deck` at `efd9a15` (the shared shell landing on main).

GitHub Pages serves this copy with the coaching decks. A deck does not request ai-config at runtime.

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

https://github.com/ByronDarlison/ai-config/blob/main/darlison/presentations/SLIDE-VISUAL-STANDARD.md

Shell how-to:

https://github.com/ByronDarlison/ai-config/blob/main/darlison/presentations/shared/README.md

Do not load fonts from the network.

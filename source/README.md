# Reusable presentations

The shared visual template, source slides, and ordered playlists are separate parts of one system.
Use [SLIDE-VISUAL-STANDARD.md](SLIDE-VISUAL-STANDARD.md) for the approved visual rules.

## Single-source slides

Byron defined these rules on 16-Nov-2026. They apply to every deck built from now on.

1. **One slide, one place.** Every slide lives once, in a slide library. A slideshow is an ordered playlist of references to library slides, never a copy.
2. **Masters stay live.** Each master deck has one fixed web address and always shows the current slides. A change to a shared slide reaches every master that uses it on its next build.
3. **Delivered copies freeze.** At delivery, freeze a dated copy for that client. It never changes unless Byron specifically asks. The client's follow-up email, board and records point to it. Freeze it just before the session and present from the frozen copy, so the deck's QR code opens exactly what the room sees.
4. **Decks move when next used.** The quarterly, EOA and monthly decks join the library the next time each is used. Any slide a deck shares with a deck already in the library becomes a reference to that slide.
5. **Variants.** A small wording difference is an `override` in the playlist; everything else still comes from the original. A different teaching point is a new slide with its own id. Never copy a slide to edit it. Client names, numbers and board links stay on the Mural board, because decks are public.
6. **See what a change touches.** Before Byron approves a change to a shared slide, show him `compile-deck impact`: every master deck it changes, with slide counts before and after. Link to slides by name, never by number.

### Slide names

Every compiled slide has a name: `<unit>-<slide>`, or just `<unit>` when the two ids match. A slide used twice in one deck gets `-2`. The name is on each section as `data-name` and in the build manifest's `slides` list. A link such as `kickoff/#bhag-definition` opens that slide wherever it sits. Old `#slide-N` links still open by number.

### Deck QR codes

A slide with `"deck_qr": true` shows a QR code that opens the deck it sits in. The compiler draws the code (`tools/qr_svg.py`, standard library only) from the deck's public address, and a body line of `{deck_url}` shows that address as text. Do not add `artwork` to that slide. The deck's address must be a plain folder address: `https`, ending in `/`, with no `?` or `#`, and no parentheses, angle brackets or braces. The code and the address beside it are both real links to the deck. Freezing a delivered copy repoints the code to the copy, so a phone that scans it during the session opens the frozen version, not a later edit of the master.

### Impact report

```sh
./source/tools/compile-deck impact --base origin/main
```

It lists every master playlist the working tree changes against the base, the slides whose content changed, slides added or removed, and the slide counts before and after. It also says when the shared deck shell changed, because that changes every master. Frozen copies never appear: they are not rebuilt.

### Frozen client copies

```sh
./source/tools/compile-deck freeze --deck kickoff --label 2026-11-17-k1 --dest ~/coaching-slides
```

This copies the published master (`metronomics/<deck>/`) to `delivered/<deck>/<label>/` in coaching-slides and writes `FROZEN.json`. If the deck has a QR slide, the copy's code and the address shown beside it are rewritten to open the frozen copy; the master's code keeps opening the master. The label is the delivery date with an optional short code. Use a code, not the client's name: the coaching-slides repository and its pages are public. A second freeze of the same label fails. Pass `--replace` only when Byron asks; the record keeps the earlier dates. Publishing never writes into a frozen copy.

## Libraries and reusable units

Each local library contains JSON units identified by filename and `id`.
A unit can be one slide or an artifact containing a `slides` array.
Each slide has its own stable `id`, `layout`, `title`, and `headline`.
Optional fields include `support`, `body`, `eyebrow`, `group`, `tags`, `notes`, `seed`, and `artifact`.
Connected causal sequences accept up to three panels; decision layouts accept up to four.
`panels` contains objects with `role`, `heading`, `support`, and `mark` (structure, action, or gap).
For causal slides, `arrows: false` produces a summary row without connectors.
`artwork` supplies a library-relative `src` and descriptive `alt`.
Images must stay inside that library. Build output bundles assets and fonts locally.
A populated title requires artwork.
`headline_accent` adds a blue second clause to a `comp-attempts` or `comp-figure` headline.
`about-timeline` takes `role`, `body`, `timeline_label` and `timeline`, a list of rows with `year`, `age`, `text`, `kind` (photo, logo or illustration), optional `portrait`, and `media` (one or two images, each with `src` and `alt`).
`comp-attempts` takes `attempts`: one to four objects with `year`, `heading`, `support`, `outcome` and optional `win`.
`comp-figure` takes `figure` with a library-relative `.svg` `src` and descriptive `alt`.

### Drawing slides, hotspots, links and hover terms

A `comp-story` slide with artwork shows its title and picture. `art_side: true` puts the title, `support` and `body` beside the picture. The copy takes about 45% of the width. Add `art_large: true` when the picture is a drawing the room must read (a plan page, a chart): it keeps the wide picture column. Add `art_small: true` for a names-only focus picture: it takes about 45%. `art_full: true` gives the picture the full width, and `art_fit: true` lets a short wide drawing set its own height.

**Instruction line.** An `art_full` slide shows `support` as one line under the title, above the drawing. It cannot show `body`. Text a drawing slide cannot show prints a `WARNING` naming the slide. Pass `--fail-on-dropped-text` to make it stop the build. Stopping is the intended default; it is a switch for now only because published slides still carry such text.

```json
{"layout": "comp-story", "art_full": true, "headline": "Does every function have an owner?",
 "support": "In Metronome: open Team View. Check it against your chart.",
 "artwork": {"src": "assets/team-view.svg", "alt": "The Team View page."}}
```

**Hotspots.** `artwork.hotspots` is a list of hover areas. All positions are in the picture's own units, so `artwork.viewbox` (`[width, height]`) is required. Each hotspot takes `x`, `y`, `w`, `h`, `term` and `tip`. Optional fields:

- `icon`: `[x, y]` moves the small "i" mark. `false` hides the mark; the area still answers hover, focus and tap.
- `targets`: the parts that stay bright while the rest of the picture dims. A target is a box `[x, y, w, h]`, or a line `{"points": [[x, y], ...], "width": 16}` with at least two points and a width above zero. Use a line to keep one line of a chart bright.
- `dim`: `[x, y, w, h]`, the part of the picture that dims. The default is the whole picture.

```json
{"x": 90, "y": 520, "w": 250, "h": 56, "term": "Line A", "tip": "Line A stays bright.", "icon": false,
 "targets": [{"points": [[80, 420], [300, 330], [920, 90]], "width": 22}, [90, 520, 250, 56]]}
```

**Links and QR codes.** `artwork.links` makes parts of a picture clickable. Each link takes `x`, `y`, `w`, `h` (same units as hotspots, inside the viewbox), `href`, and an optional `label`. The compiler draws a real link over that part of the picture and a text link under the picture. The text shows `label`, or the address without `https://` when there is no label. Only plain `https` addresses are allowed: no other scheme, no sign-in part, no port, no spaces, quotes, backslashes, parentheses, angle brackets or braces (write `(` and `)` as `%28` and `%29`; square brackets in the path are fine). Every link opens in a new tab. Links work on `comp-story` slides.

Mark a picture that holds a QR code with `"qr": true`. The compiler cannot see inside a picture, so this mark is how it knows. A picture marked `qr` with no `links` fails the build. Record one link per code.

```json
"artwork": {"src": "assets/cash-links.svg", "alt": "Two QR codes for the cash templates.", "viewbox": [1200, 520], "qr": true,
  "links": [{"x": 40, "y": 40, "w": 520, "h": 440, "href": "https://example.com/templates/one", "label": "12 month template"}]}
```

A compiled deck still loads nothing from the network. These links are the one place an address may appear, and `check-shell.py` enforces that.

**Hover terms.** `terms` on a slide is a list of words that show a definition box on hover, on keyboard focus, and as a tap-to-open sheet on a small screen. Each entry takes `term` and `tip` (one line or a list of lines). The first match is wrapped in each of these places: the slide title (and its `headline_accent`), `support` and each `body` line on a `comp-story` or `about-timeline` slide, and each card's `support` and `items`. The line under a card slide's title and the line on a `comp-rule` slide are not wrapped. A term is matched in the text as written, never inside another term's box. A term can also show a library picture with `image`, which takes a library-relative `src` and descriptive `alt`. With `image`, `tip` is optional. The picture is sized to stay inside the slide.

```json
"terms": [{"term": "Market Map", "tip": "Where each competitor sits.",
           "image": {"src": "assets/market-map-example.svg", "alt": "An example Market Map with four competitors."}}]
```

A worked example of every field above is in `tools/fixtures/deck-builder/`.

An artifact bundle inherits `artifact`, `seed`, and `tags` into its slides.
Source names qualify IDs, so different libraries can reuse a short ID without collisions.
Runtime slide numbers belong to the presentation, not the source identity.

## Playlists

A playlist is an ordered list of references, not copied slide content.
See [mixed-example.json](playlists/mixed-example.json) for three source libraries in one deck.

```json
{
  "id": "planning-session",
  "title": "Planning session",
  "sidebar_title": "Planning session",
  "sources": {"workshop": "../libraries/workshop"},
  "units": [
    "metronomics:01-title",
    "workshop:shared-plan",
    {"id": "workshop:shared-plan", "slides": ["commit"]}
  ]
}
```

Explicit playlist files resolve `sources` relative to the playlist file.
Registered folders may be in another local checkout; they must be available when compiling.
Remote presentation formats first need importing into the shared slide schema.
This compiler does not fetch remote URLs or import arbitrary HTML or PowerPoint.
A source can appear more than once. Selection order is preserved.
`override` changes presentation-specific copy without editing the reusable original.
It cannot change source identity or provenance.

The built-in `metronomics` source preserves existing library references.
Legacy named playlists remain under `metronomics/playlists/`.
Playlist `branding` accepts `domain` and `logo` (`metronomics` or `none`).

## Build

From the repository root:

```sh
./source/tools/compile-deck kickoff-sample --check
./source/tools/compile-deck --playlist-file source/playlists/mixed-example.json --check
```

`--out` chooses an empty directory or a prior compiler-owned build.
The compiler refuses to erase an arbitrary directory, traverse an output symlink, or overlap a source library.
Legacy builds without the compiler marker need a fresh output directory; keep the previous build as an archive.
It stages a build before replacing output, so invalid sources preserve the previous deck.
The output manifest records ordered source references and content hashes.
There are no machine-specific source paths in the output manifest.

Rebuilding incorporates source changes. Existing published presentations remain unchanged until republished.
A delivered presentation stays fixed as a frozen copy; see [Frozen client copies](#frozen-client-copies).

## Strategy matrix use

The implementation matrix will produce playlists from artifact references in column order.
An artifact link will open its slide bundle; a quarter-heading link will open the complete quarter playlist.
Both use the same source units. The matrix is one playlist producer, not a restriction on the template.
Website links and automatic matrix extraction are a separate implementation step.

## Approved example and checks

`kickoff-sample` preserves Byron’s reviewed 13-slide visual sample.
Its coaching copy is illustrative, not approval of a production session outline.
`kickoff` remains the empty compatibility seed.
The shared HTML preview is a generated snapshot of `kickoff-sample`; edit the JSON source and rebuild it.
Review evidence for the standard is kept in Byron's private records.

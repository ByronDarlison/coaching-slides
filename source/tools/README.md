# Presentation compile tools

## compile-deck

Compose a Metronomics playlist onto the shared house shell.

```
./source/tools/compile-deck
./source/tools/compile-deck kickoff --check
python3 source/tools/compile_deck.py --list
```

The CLI copies `../shared/deck` CSS, JS, and fonts, then writes `index.html` from resolved unit ids.

## publish-deck

Copy a compiled deck into a local `ByronDarlison/coaching-slides` checkout.

```
./source/tools/publish-deck --dest /path/to/coaching-slides
```

For a deck in `../playlists/` (Kick Off, Q1, Q2 and later), compile it first and pass the build with `--from`. Without `--from`, the command looks only in the old `metronomics/playlists/` seed and fails, or copies a stale build with no artwork (17-Nov-2026).

```
./source/tools/compile-deck --playlist-file source/playlists/q2.json --out /tmp/q2 --check
./source/tools/publish-deck --playlist q2 --dest /path/to/coaching-slides --from /tmp/q2
```

Run `git status` in the coaching-slides checkout before committing. A publish that deletes artwork is wrong: restore it and publish again with `--from`.

Path convention:

```
<coaching-slides>/metronomics/kickoff/  ->  https://byrondarlison.github.io/coaching-slides/metronomics/kickoff/
```

The helper uses ordinary git-ready file copy. It does not create tokens, remotes, or Pages sites.

## compile-deck impact

List every master deck a slide-library change alters, before Byron approves it.

```
./source/tools/compile-deck impact --base origin/main
./source/tools/compile-deck impact --json
```

## compile-deck freeze

Freeze the delivered copy of a published master deck in a coaching-slides checkout.

```
./source/tools/compile-deck freeze --deck kickoff --label 2026-11-17-k1 --dest ~/coaching-slides
```

The copy lands in `delivered/<deck>/<label>/` and is never rebuilt. `--replace` replaces it, only when Byron asks.

## Tests

```
python3 -m pytest -q source/tools/test_compile_deck.py
node --test source/tools/test_shell.cjs
```

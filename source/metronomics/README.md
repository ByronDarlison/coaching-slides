# Metronomics presentation framework

The reusable multi-source contract is now documented in [Reusable presentations](../README.md).
The approved populated example is `kickoff-sample`; `kickoff` remains the empty compatibility seed.


Durable slide units, session playlists, and a compile CLI live here.

The shared house shell stays in `../shared/deck`.

This tree does not rewrite the legacy coaching-slides generators.

## Tree

- `library/` slide units. Includes the approved visual sample and an empty compatibility seed
- `playlists/` ordered source references; `kickoff-sample` builds the 13-slide visual reference
- `compiled/` local compile output; not the public source of truth
- `../tools/compile-deck` reusable CLI; `../tools/publish-deck` copies the built deck

## Seed

Kickoff is one empty template unit, `blank-template`.

One unit is the standard empty shell. It is not a session outline.

Leave title, headline, group, and eyebrow empty. Do not invent session titles.

The populated `kickoff-sample` is a visual reference, not an approved production coaching agenda.

## Compile

From the repository root:

```
python3 source/tools/compile_deck.py --check
./source/tools/compile-deck --check
```

Default playlist is `kickoff`.

Output lands in `compiled/kickoff/` unless `--out` is set.

`compiled/` is gitignored except this README. Recompile when you need the deck.

## Public path convention (coaching-slides Pages)

Units, playlists and the compiler live in this repository under `source/`.

GitHub Pages serves the built decks from the repository root. Copy the compiled folder there:

```
compiled/<playlist>/  ->  coaching-slides/metronomics/<playlist>/
```

Kickoff v1:

```
compiled/kickoff/  ->  coaching-slides/metronomics/kickoff/
```

Public URL after that repo deploys Pages:

```
https://byrondarlison.github.io/coaching-slides/metronomics/kickoff/
```

That path sits beside `monthly/mN/` and `eoa/`. It does not change `build_slideshows.py`.

## Publish helper

Ordinary filesystem copy. No extra credentials.

```
./source/tools/publish-deck --dest /path/to/coaching-slides
./source/tools/publish-deck --dest /path/to/coaching-slides --dry-run
```

Then in the coaching-slides checkout: add `metronomics/kickoff/`, commit, and push to the branch that Pages serves.

Publication is a separate, explicitly authorized action in the destination repository. Compiling does not publish a deck.

## Check

```
python3 source/shared/check-shell.py
python3 source/shared/check-shell.py --deck source/metronomics/compiled/kickoff
```

## Agent front door

Byron's agents use a private skill that wraps this command. The command is the real tool.

# Metronomics playlists

The reusable multi-source contract is now documented in [Reusable presentations](../../README.md).
The approved populated example is `kickoff-sample`; `kickoff` remains the empty compatibility seed.


One JSON file per session playlist. Basename is the playlist id.

`kickoff` remains one empty template unit. `kickoff-sample` contains the approved 13-slide visual reference.

## Fields

- `id` matches the filename stem
- `units` is an ordered list of unit ids, or objects `{ "id": "...", "override": { ... } }`
- `title` and `sidebar_title` become visible chrome. Leave them empty on the template playlist
- `stage` is the program stage tag, for example `kickoff`. It does not render on slides
- `seed` names the template source. It does not invent session titles

Overrides may change headline, support, notes, or group. They may not change source identity or provenance; see the reusable contract for the complete restrictions.

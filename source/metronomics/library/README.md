# Metronomics slide units

The reusable multi-source contract is now documented in [Reusable presentations](../../README.md).
The approved populated example is `kickoff-sample`; `kickoff` remains the empty compatibility seed.


One JSON file per unit. Basename is the unit id.

The library contains 13 populated visual-reference units and the empty compatibility unit `blank-template`.

Do not add session stubs until real copy exists.

## Fields

- `id` matches the filename stem
- `artifact` is the `artifact-review-library/` slug when one exists, or null for a session ritual
- `title` is the sidebar label. Leave it empty on the template so the shell shows Slide N
- `tags` filter units into playlists (`kickoff`, `session-ritual`, `people-culture`). Tags are not slide copy
- `layout` is `title`, `comp-story`, `comp-causal`, `comp-decision`, or `comp-rule`
- `group` sets `data-group` on the first slide of a section. Omit it on the template
- `headline` is the visible takeaway title. Leave it empty on the template
- `eyebrow` is optional face chrome. Omit it on the template
- `support` and `body` are slide copy. Leave them empty on the template
- `notes` become speaker notes
- `seed` records the source. It does not render on the slide

Do not invent session titles, section titles, or stage labels on the empty template. The compiler must not fall back from an empty title to a headline or from an empty eyebrow to a title.

Playlist files may add an `override` object on one entry. Overrides cannot change source identity or provenance; see the reusable contract for the complete restrictions.

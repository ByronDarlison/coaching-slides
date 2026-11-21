# Shared slideshow shell

`deck/` contains the portable house CSS, navigation, fonts, logo, and generated visual preview.
The approved standard is [Slide Visual Standard](../SLIDE-VISUAL-STANDARD.md).

Author reusable JSON slides and compile playlists through the [presentation structure](../README.md).
Use `compile-deck kickoff-sample` to recreate the reviewed example.
Do not copy its coaching narrative into unrelated presentations.
`?review=template` reveals composition labels during template review.

The generated preview is refreshed from the compiled example as part of a standard change.
Its included images are preview assets. Production builds bundle their own referenced artwork.

Refresh the shared snapshot explicitly with `python3 source/tools/refresh_standard_preview.py` from the repository root.

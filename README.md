# Coaching slides

Browser-based slideshows used by Byron Darlison in founder coaching and Entrepreneurs' Organization Accelerator meetings.

The repository contains the rendered decks, their shared visual assets, the source used to build recurring slides, and automated checks that catch broken links, missing images, content drift, and visual regressions.

View the published collection at:

https://byrondarlison.github.io/coaching-slides/

## What is included

### Monthly coaching

The [`monthly`](monthly/) directory contains 23 meeting decks. The sequence introduces and then revisits the operating practices used throughout a multi-year coaching engagement.

### Entrepreneurs' Organization Accelerator

The [`eoa`](eoa/) directory contains:

- onboarding;
- an Owner's Outcome primer; and
- meeting decks 1 through 10.

These decks are designed for Byron's Entrepreneurs' Organization Accelerator accountability group. They include organization-specific meeting instructions and should be adapted before use in another setting.

### Coaching deliverables

[`metronomics-deliverables.html`](metronomics-deliverables.html) presents the coaching sequence and shows when each deliverable is introduced, coached, reviewed, or rebuilt.

### Build and verification tools

- [`build_slideshows.py`](build_slideshows.py) generates the recurring monthly decks.
- [`build_new_slideshows.py`](build_new_slideshows.py) supports newer deck patterns.
- [`scripts/slide-test.py`](scripts/slide-test.py) checks rendered deck structure and content rules.
- [`scripts/audit-decks.py`](scripts/audit-decks.py) checks source and sequence consistency.
- [`tests/visual`](tests/visual/) contains the browser-based visual-regression suite.

## Viewing the slides locally

The decks are static HTML. Most can be opened directly in a browser, but a local web server handles shared files and paths more reliably.

From the repository root:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

Use the arrow keys to move through a deck. Open the browser's print dialog when a PDF copy is needed.

## Repository structure

```text
coaching-slides/
├── index.html
├── monthly/
│   └── m1/ ... m23/
├── eoa/
│   ├── onboarding/
│   ├── owners-outcome-primer/
│   └── meeting-1/ ... meeting-10/
├── shared/
│   └── assets/
├── scripts/
├── tests/
├── build_slideshows.py
├── build_new_slideshows.py
├── PACING.md
├── SLIDE-RULES.md
└── metronomics-deliverables.html
```

## Making changes

Read [`SLIDE-RULES.md`](SLIDE-RULES.md) before changing a deck and [`PACING.md`](PACING.md) before changing the coaching sequence.

Run the structural checks from the repository root:

```bash
python3 scripts/audit-decks.py --repo .
```

Run the test against one deck:

```bash
python3 scripts/slide-test.py monthly/m1/index.html
```

Run it against every deck:

```bash
find monthly eoa -maxdepth 2 -name index.html -type f -print0 |
  xargs -0 -n1 python3 scripts/slide-test.py
```

The visual-regression setup is documented in [`tests/visual/README.md`](tests/visual/README.md).

## Using or adapting the decks

The decks are working coaching materials, not a stand-alone certification program. They assume the facilitator understands the referenced methods and can distinguish Byron's interpretation from the original frameworks.

Before using a deck:

1. Review every slide.
2. Replace Byron-specific links, contact details, and meeting instructions.
3. Confirm that you have the right to use any third-party framework, logo, image, quotation, or organization-specific material.
4. Preserve the attribution supplied in the deck.
5. Test the adapted deck in the browser and at the presentation resolution you will use.

## Attribution and independence

The decks interpret and apply ideas from Metronomics and from the published work of Shannon Susko and other credited authors. Some decks also support Byron's work with Entrepreneurs' Organization Accelerator.

Metronomics, Entrepreneurs' Organization, their logos, and other third-party marks and materials belong to their respective owners. Their presence in this repository does not transfer ownership or imply that the repository is an official publication of those organizations.

See [`NOTICE.md`](NOTICE.md) for the licensing boundaries.

## License

This repository uses two licenses:

- Original presentation content, documentation, and Byron-created visual assets are licensed under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](LICENSE.md).
- Build scripts, test scripts, and other software are licensed under the [MIT License](LICENSE-CODE).

Third-party frameworks, trademarks, logos, images, quotations, and other identified third-party material are excluded from both licenses.

## Contributing and security

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing a change. Do not include client information, private meeting notes, credentials, or licensed source material that cannot be redistributed.

Report privacy and security concerns according to [`SECURITY.md`](SECURITY.md).

## More from Byron

- [Articles and tools](https://www.darlison.com/)
- [Coaching](https://www.darlison.com/coaching/)
- [GitHub profile](https://github.com/ByronDarlison)


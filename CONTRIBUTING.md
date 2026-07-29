# Contributing

Corrections and focused improvements are welcome.

## Before proposing a change

- Read [`SLIDE-RULES.md`](SLIDE-RULES.md).
- Read [`PACING.md`](PACING.md) if the change affects the coaching sequence.
- Do not add client information, private meeting notes, credentials, or restricted source material.
- Preserve attribution and licensing notices.
- Keep generated decks and their source consistent.

## Required checks

Run:

```bash
python3 scripts/audit-decks.py --repo .
```

Then run the structural slide test against every changed deck:

```bash
python3 scripts/slide-test.py path/to/index.html
```

For visual changes, follow [`tests/visual/README.md`](tests/visual/README.md).

## Pull requests

Explain:

- what changed;
- why it changed;
- which decks are affected;
- which checks were run; and
- whether visual baselines need to change.

By contributing, you agree that your contribution may be distributed under the applicable repository license.


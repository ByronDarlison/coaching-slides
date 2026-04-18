# Tier 2 visual regression

Screenshots every slide in every deck with headless Chromium, diffs against a pinned baseline with pixelmatch, fails CI on divergence beyond a pixel threshold.

## First-time setup

```bash
cd ~/coaching-slides/tests/visual
npm install
npm run install-browsers
npm run baseline      # seed baselines/ from the current decks
```

Commit `baselines/` to the repo.

## Regular use

```bash
cd ~/coaching-slides/tests/visual
npm test              # diff current decks against baselines
npm run test:one -- monthly/m6    # one deck only
```

- Pass: exit 0
- Regression: exit 1, diff PNGs written to `diffs/<deck>/slide-NN.png`

## Updating baselines

When a change is intentional (new slide, layout tweak, pattern deployment), refresh baselines from Linux CI so they match the environment that actually runs the test:

```bash
gh workflow run visual-baseline.yml
```

The `visual-baseline.yml` workflow runs the baseline on Linux Chromium and commits the fresh PNGs back to `main`. You don't do this locally because macOS and Linux Chromium anti-alias text differently — local baselines would diverge from CI by thousands of pixels per slide.

Local macOS runs still work for quick checks:

```bash
npm run baseline   # overwrite with local baselines
npm test           # verify
```

But don't commit macOS baselines; trigger `visual-baseline.yml` instead.

## What it catches that slide-test.py doesn't

| slide-test.py (Tier 1) | visual regression (Tier 2) |
|---|---|
| Broken images, missing alt | Images that render blank |
| Em dashes, British spelling | Text that overflows its container |
| Missing deadline phrase | CSS regression that changes visible layout |
| Time-chain arithmetic | Font loading fallbacks |
| Cohort-specific content | Image aspect ratio regressions |

Tier 1 runs in seconds on every pre-commit. Tier 2 takes ~30-60 seconds and runs in CI (and locally before deploying a pattern change).

## Thresholds

- `--threshold` (0.15 default): pixelmatch color sensitivity per pixel
- `MAX_DIFF_PIXELS` (500): total differing pixels allowed before fail

Tune these if anti-aliasing flake becomes noisy. Start strict, loosen only if needed.

## CI

`.github/workflows/visual-regression.yml` runs `npm test` on every push that touches a deck, a build script, or the visual test harness.

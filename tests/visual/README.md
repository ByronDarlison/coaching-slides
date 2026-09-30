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

When a layout change is intentional, capture candidate baselines on Linux using the manual `visual-baseline` workflow at the PR branch. The `decks` input accepts space-separated repository paths, for example `eoa/meeting-4`. Download the `visual-baseline-candidates` artifact and inspect the changed screenshots before copying the selected deck directories into `baselines/` and explicitly committing them. The workflow never commits or pushes.

```bash
gh workflow run visual-baseline.yml --ref <pr-branch> -f decks='eoa/meeting-4'
```

A `[baseline-refresh]` commit marker does not update baselines. Regression CI continues to fail until reviewed reference images are committed.

Local macOS runs are still useful for quick checks, but don't commit macOS baselines — they diverge from Linux Chromium by thousands of pixels per slide due to anti-aliasing differences.

```bash
npm run baseline   # overwrite with local baselines
npm test           # verify
```

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

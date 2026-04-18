#!/usr/bin/env node
/**
 * visual-regression.js - screenshot every slide in every deck and
 * diff against a pinned baseline.
 *
 * First run (seed):
 *     npm run baseline
 *
 * CI/local verify:
 *     npm run test
 *
 * Single-deck debug:
 *     npm run test:one -- monthly/m6
 *
 * Flags:
 *     --update-baseline    overwrite baselines with current screenshots
 *     --deck <path>        limit to one deck (relative to repo root)
 *     --threshold <float>  pixelmatch threshold (default 0.15)
 *
 * Exit code 0 = no diffs beyond threshold, 1 = regression detected.
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { PNG } = require('pngjs');
const pixelmatch = require('pixelmatch');

const REPO_ROOT = path.resolve(__dirname, '..', '..');
const TESTS_DIR = __dirname;
const BASELINE_DIR = path.join(TESTS_DIR, 'baselines');
const CURRENT_DIR = path.join(TESTS_DIR, 'current');
const DIFF_DIR = path.join(TESTS_DIR, 'diffs');

const VIEWPORT = { width: 1440, height: 900 };
const MAX_DIFF_PIXELS = 500;

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    updateBaseline: false,
    deck: null,
    threshold: 0.15,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--update-baseline') opts.updateBaseline = true;
    else if (args[i] === '--deck') opts.deck = args[++i];
    else if (args[i] === '--threshold') opts.threshold = parseFloat(args[++i]);
  }
  return opts;
}

function listDecks(filterDeck) {
  const patterns = ['monthly', 'eoa'];
  const decks = [];
  for (const pattern of patterns) {
    const base = path.join(REPO_ROOT, pattern);
    if (!fs.existsSync(base)) continue;
    for (const entry of fs.readdirSync(base)) {
      const indexPath = path.join(base, entry, 'index.html');
      if (fs.existsSync(indexPath)) {
        const relPath = `${pattern}/${entry}`;
        if (!filterDeck || filterDeck === relPath) {
          decks.push({ name: relPath, indexPath });
        }
      }
    }
  }
  return decks.sort((a, b) => a.name.localeCompare(b.name));
}

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

async function captureDeck(browser, deck) {
  const context = await browser.newContext({ viewport: VIEWPORT });
  const page = await context.newPage();
  const fileUrl = 'file://' + deck.indexPath;
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 30000 });
  // Wait for fonts + initial animations
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);

  const slideCount = await page.evaluate(
    () => document.querySelectorAll('section.slide').length
  );

  const screenshots = [];
  for (let i = 0; i < slideCount; i++) {
    await page.evaluate((idx) => {
      const slides = document.querySelectorAll('section.slide');
      slides[idx].scrollIntoView({ behavior: 'instant', block: 'start' });
    }, i);
    await page.waitForTimeout(300);
    // Force all reveal animations to their final state so screenshots
    // are deterministic across runs.
    await page.evaluate(() => {
      document.querySelectorAll('.reveal').forEach((el) => {
        el.style.opacity = '1';
        el.style.transform = 'none';
        el.style.transition = 'none';
      });
    });
    await page.waitForTimeout(100);
    const buf = await page.screenshot({ fullPage: false });
    screenshots.push({ index: i, buffer: buf });
  }
  await context.close();
  return screenshots;
}

function diff(baselineBuf, currentBuf, threshold) {
  const baseline = PNG.sync.read(baselineBuf);
  const current = PNG.sync.read(currentBuf);
  if (baseline.width !== current.width || baseline.height !== current.height) {
    return { mismatch: -1, diffPng: null, sizeMismatch: true };
  }
  const { width, height } = baseline;
  const diffPng = new PNG({ width, height });
  const mismatch = pixelmatch(
    baseline.data,
    current.data,
    diffPng.data,
    width,
    height,
    { threshold }
  );
  return { mismatch, diffPng: PNG.sync.write(diffPng), sizeMismatch: false };
}

function writeFileSafe(p, buf) {
  ensureDir(path.dirname(p));
  fs.writeFileSync(p, buf);
}

async function main() {
  const opts = parseArgs();
  const decks = listDecks(opts.deck);
  if (decks.length === 0) {
    console.error('No decks to test.');
    process.exit(1);
  }

  console.log(
    `Playwright visual ${opts.updateBaseline ? 'baseline' : 'test'} on ${decks.length} deck(s)`
  );

  const browser = await chromium.launch();
  let totalDecks = 0;
  let failingDecks = 0;
  let failingSlides = 0;

  try {
    for (const deck of decks) {
      totalDecks += 1;
      console.log(`\n--- ${deck.name} ---`);
      const screenshots = await captureDeck(browser, deck);
      const baselineDir = path.join(BASELINE_DIR, deck.name);
      const currentDir = path.join(CURRENT_DIR, deck.name);
      const diffDir = path.join(DIFF_DIR, deck.name);

      if (opts.updateBaseline) {
        if (fs.existsSync(baselineDir)) {
          fs.rmSync(baselineDir, { recursive: true, force: true });
        }
        ensureDir(baselineDir);
        for (const s of screenshots) {
          writeFileSafe(
            path.join(baselineDir, `slide-${String(s.index).padStart(2, '0')}.png`),
            s.buffer
          );
        }
        console.log(`  baseline: wrote ${screenshots.length} slide(s)`);
        continue;
      }

      if (!fs.existsSync(baselineDir)) {
        console.log(`  SKIP  no baseline for ${deck.name}; run --update-baseline first`);
        continue;
      }

      ensureDir(currentDir);
      ensureDir(diffDir);

      let deckFailed = false;
      for (const s of screenshots) {
        const baseName = `slide-${String(s.index).padStart(2, '0')}.png`;
        const baselinePath = path.join(baselineDir, baseName);
        const currentPath = path.join(currentDir, baseName);
        const diffPath = path.join(diffDir, baseName);
        writeFileSafe(currentPath, s.buffer);
        if (!fs.existsSync(baselinePath)) {
          console.log(`  NEW   slide ${s.index} has no baseline`);
          deckFailed = true;
          failingSlides += 1;
          continue;
        }
        const baseBuf = fs.readFileSync(baselinePath);
        const { mismatch, diffPng, sizeMismatch } = diff(baseBuf, s.buffer, opts.threshold);
        if (sizeMismatch) {
          console.log(`  FAIL  slide ${s.index}: viewport/render size mismatch`);
          deckFailed = true;
          failingSlides += 1;
          continue;
        }
        if (mismatch > MAX_DIFF_PIXELS) {
          console.log(`  FAIL  slide ${s.index}: ${mismatch} pixel(s) differ`);
          writeFileSafe(diffPath, diffPng);
          deckFailed = true;
          failingSlides += 1;
        } else {
          process.stdout.write(`  PASS slide ${s.index} (${mismatch}px) `);
        }
      }
      if (deckFailed) failingDecks += 1;
      console.log('');
    }
  } finally {
    await browser.close();
  }

  console.log('\n==============================');
  if (opts.updateBaseline) {
    console.log(`Baselines written for ${totalDecks} deck(s)`);
    process.exit(0);
  }
  if (failingDecks > 0) {
    console.log(`FAIL: ${failingDecks}/${totalDecks} deck(s), ${failingSlides} slide(s) diverged`);
    console.log(`Diffs written to ${DIFF_DIR}`);
    process.exit(1);
  }
  console.log(`PASS: ${totalDecks} deck(s) match baseline`);
  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(2);
});

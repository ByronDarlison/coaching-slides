// Capture narrated slides at 1920x1080 for the narrated-video pipeline.
// Usage: node capture.mjs <base-url> <deck> <slide,slide,...> <out-dir>
// Writes <out-dir>/slide-<N>.png for each requested slide, in order.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const [base, deck, list, outDir] = process.argv.slice(2);
if (!base || !deck || !list || !outDir) {
  console.error('usage: capture.mjs <base-url> <deck> <slides> <out-dir>');
  process.exit(2);
}
const slides = list.split(',').map(Number);
if (!slides.every(n => Number.isInteger(n) && n > 0)) {
  console.error('bad slide list');
  process.exit(2);
}
fs.mkdirSync(outDir, { recursive: true });

// Presentation view: no sidebar, no control bar, no notes, final reveal state.
const PRESENT_CSS = `
  .slide-sidebar, .controls, #sidebarToggle, #notesPanel, #sidebarBackdrop { display: none !important; }
  body { --deck-nav-space: 0px !important; }
  #presentation { width: 100vw !important; margin-left: 0 !important; }
  .reveal { opacity: 1 !important; transform: none !important; transition: none !important; }
  *, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }
`;

const browser = await chromium.launch();
try {
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(`${base}/${deck}/index.html#slide-${slides[0]}`, { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  await page.addStyleTag({ content: PRESENT_CSS });
  await page.evaluate(() => document.body.classList.add('sidebar-hidden'));
  for (const n of slides) {
    await page.evaluate(num => { window.location.hash = `#slide-${num}`; }, n);
    await page.waitForFunction(num => {
      const el = document.getElementById(`slide-${num}`);
      if (!el) return false;
      const r = el.getBoundingClientRect();
      return Math.abs(r.top) < 2;
    }, n, { timeout: 10000 }).catch(async () => {
      await page.evaluate(num => document.getElementById(`slide-${num}`)?.scrollIntoView({ block: 'start', behavior: 'instant' }), n);
    });
    await page.evaluate(num => {
      const el = document.getElementById(`slide-${num}`);
      el?.classList.add('visible');
      el?.querySelectorAll('.reveal').forEach(r => r.classList.add('visible'));
    }, n);
    await page.waitForTimeout(250);
    const present = await page.evaluate(num => Boolean(document.getElementById(`slide-${num}`)), n);
    if (!present) throw new Error(`slide ${n} missing`);
    await page.screenshot({ path: path.join(outDir, `slide-${n}.png`), fullPage: false });
  }
  await context.close();
} finally {
  await browser.close();
}

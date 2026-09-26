// Render prerecorded results. No benchmark execution or timing takes place here.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import assert from 'node:assert/strict';

const out = path.resolve(process.argv[2]);
const modules = path.resolve(process.argv[3]);
const preview = process.argv.includes('--preview');
const require = createRequire(path.join(modules, 'package.json'));
const { chromium } = require('playwright-core');
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', headless: true });
const errors = [], clipping = [];
try {
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => errors.push(String(e)));
  const url = pathToFileURL(path.join(out, 'index.html')).href;
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  const data = JSON.parse(await fs.readFile(path.join(out, 'data.json'), 'utf8'));
  assert.deepEqual(await page.evaluate(() => window.filmData), data);
  const ms = v => v.toFixed(3) + ' ms';
  const change = r => ((r - 1) * 100 >= 0 ? '+' : '') + ((r - 1) * 100).toFixed(2) + '%';
  assert.equal(await page.locator('#everyday-rows tr').count(), 19);
  assert.equal(await page.locator('#all-rows tr').count(), 117);
  await page.locator('summary').click();
  for (const session of ['A', 'B']) {
    await page.locator('#session-' + session.toLowerCase()).click();
    for (const [id, cases, all] of [
      ['everyday-rows', data.cases.filter(c => c.directory && c.group === 'everyday'), false],
      ['all-rows', data.cases, true]
    ]) {
      const actual = await page.locator(`#${id} tr`).evaluateAll(rows => rows.map(r => [...r.children].map(c => c.textContent)));
      const expected = cases.map(c => {
        const s = c[session], a = s.system, r = s.reference;
        return [c.id, ms(a.baseline_ms), ms(a.candidate_ms), change(a.elapsed_ratio),
          ...(all ? [ms(r.baseline_ms), change(r.elapsed_ratio)] : [a.ratio_ci95.map(change).join(' to ')]), s.verdict];
      });
      assert.deepEqual(actual, expected);
    }
  }
  await page.locator('#session-a').click();
  await page.locator('summary').click();
  await page.locator('.tab').nth(2).click();
  assert.equal(await page.locator('.tab').nth(2).getAttribute('aria-pressed'), 'true');
  const before = Number(await page.locator('#seek').inputValue());
  await page.locator('#play').click();
  await page.waitForTimeout(250);
  assert.equal(await page.locator('#play').textContent(), 'Pause');
  assert(Number(await page.locator('#seek').inputValue()) > before);
  await page.locator('#play').click();
  assert.equal(await page.locator('#play').textContent(), 'Play');
  await page.evaluate(() => window.renderFilmFrame(8.5));
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: path.join(out, 'web-preview.png') });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: path.join(out, 'mobile-preview.png') });
  await page.setViewportSize({ width: 1600, height: 900 });
  await page.goto(url + '?film');
  await page.evaluate(() => document.fonts.ready);
  // Inspect every scene in both sessions, not just the selected poster.
  for (const session of ['A', 'B']) {
    await page.evaluate(s => document.getElementById('session-' + s.toLowerCase()).click(), session);
    for (let t = .5; t < data.duration; t += .5) {
      const overflow = await page.evaluate(t => { window.renderFilmFrame(t); return window.filmOverflow; }, t);
      if (overflow.length) clipping.push({ session, t, overflow });
    }
  }
  assert.deepEqual(clipping, [], 'Canvas labels must fit their declared regions');
  await page.evaluate(() => document.getElementById('session-a').click());
  for (const [name, t] of [['intro', 3], ['poster', 8.7], ['tools', 14.7], ['files', 20.7],
    ['proof', 27.5], ['how', 33.5], ['tradeoffs', 42], ['outro', 49.5]]) {
    await page.evaluate(t => window.renderFilmFrame(t), t);
    await page.screenshot({ path: path.join(out, name + '.png') });
  }
  assert.deepEqual(errors, []);
  console.log('Verified all 272 displayed table rows across A/B, chapter navigation, playback, mobile layout and canvas text bounds.');
  const fps = 24, frames = data.duration * fps;
  if (!preview) {
    const encoder = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe',
      '-framerate', String(fps), '-vcodec', 'png', '-i', '-', '-an', '-c:v', 'libx264', '-threads', '2',
      '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
      path.join(out, 'my-grep-everyday.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
    const completed = once(encoder, 'close');
    let failure;
    encoder.on('error', e => { failure = e; });
    encoder.stdin.on('error', e => { failure = e; });
    try {
      for (let frame = 0; frame < frames; frame++) {
        if (failure) throw failure;
        await page.evaluate(t => window.renderFilmFrame(t), frame / fps);
        const png = await page.screenshot({ type: 'png' });
        if (!encoder.stdin.write(png)) await once(encoder.stdin, 'drain');
        if (frame % 120 === 0) console.log(`Rendered ${frame}/${frames} frames`);
      }
      encoder.stdin.end();
      const [code] = await completed;
      assert.equal(code, 0);
      assert.deepEqual(errors, []);
    } catch (e) {
      encoder.kill('SIGTERM');
      throw e;
    }
  }
  await fs.writeFile(path.join(out, 'render-validation.json'), JSON.stringify({
    browser: await browser.version(), node: process.version,
    playwright: require('playwright-core/package.json').version,
    sourceSha256: data.sources, pageErrors: errors, clipping,
    verified: ['Data equality with generated JSON', '272 table rows across both sessions',
      'Chapter navigation', 'Playback advances and pauses', 'No mobile page overflow',
      'Text bounds for every scene in both sessions'],
    video: preview ? null : { frames, fps, durationSeconds: data.duration, width: 1600, height: 900, audio: false }
  }, null, 2) + '\n');
  console.log(preview ? 'Preview complete.' : 'Finished: my-grep-everyday.mp4');
} finally {
  await browser.close();
}

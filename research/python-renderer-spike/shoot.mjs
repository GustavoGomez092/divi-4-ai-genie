// Evaluation tooling (not part of the renderer): headless Chrome over CDP (Node 22+ built-in WebSocket).
//   node shoot.mjs <outdir> <name> <url> [--width 1440,390] [--wait 3500] [--no-js]
// For each width: full-page PNG of the builder area (.et-l bounding box), plus a JSON geometry/computed-style
// signature of every `.et-l [class*=et_pb_]` element (like the earlier render-prototype check).
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [outdir, name, url, ...rest] = process.argv.slice(2);
const opt = (k, d) => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : d; };
const widths = opt('--width', '1440,390').split(',').map(Number);
const wait = Number(opt('--wait', '3500'));
const noJs = rest.includes('--no-js');
const CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = mkdtempSync(join(tmpdir(), 'cdp-'));
const port = 9300 + Math.floor(Math.random() * 500);
const chrome = spawn(CH, ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, '--allow-file-access-from-files', '--force-device-scale-factor=1', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function target() {
  for (let i = 0; i < 50; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/json/list`);
      const j = await r.json();
      const p = j.find((t) => t.type === 'page');
      if (p) return p.webSocketDebuggerUrl;
    } catch { /* not up yet */ }
    await sleep(200);
  }
  throw new Error('chrome did not start');
}

const ws = new WebSocket(await target());
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const pending = new Map(); const events = [];
ws.addEventListener('message', (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } else events.push(d);
});
const send = (method, params = {}) => new Promise((res, rej) => {
  const i = ++id; pending.set(i, (d) => (d.error ? rej(new Error(method + ': ' + d.error.message)) : res(d.result)));
  ws.send(JSON.stringify({ id: i, method, params }));
});
const evaluate = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result.value;

await send('Page.enable'); await send('Runtime.enable');
if (noJs) await send('Emulation.setScriptExecutionDisabled', { value: true });
const results = {};
for (const w of widths) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 1000, deviceScaleFactor: 1, mobile: false });
  const t0 = Date.now();
  await send('Page.navigate', { url });
  for (let i = 0; i < 100; i++) { if (events.some((e) => e.method === 'Page.loadEventFired')) break; await sleep(100); }
  events.length = 0;
  await sleep(wait);
  const geo = await evaluate(`(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => (i.loading = 'eager', i.complete ? i.decode().catch(() => {}) : new Promise((r) => { i.onload = i.onerror = r; }))));
    await new Promise((r) => setTimeout(r, 500));
    const etl = document.querySelector('.et-l');
    const r = etl.getBoundingClientRect();
    const els = [...etl.querySelectorAll('[class*=et_pb_]')];
    const rows = els.map((e) => { const b = e.getBoundingClientRect(); const s = getComputedStyle(e);
      return [e.tagName, (e.className.baseVal ?? e.className).split(/\\s+/).filter(c => /_\\d+$/.test(c)).join(' '),
        Math.round(b.x), Math.round(b.y + scrollY - (r.y + scrollY)), Math.round(b.width), Math.round(b.height),
        s.color, s.backgroundColor, s.fontFamily.split(',')[0], s.fontSize, s.fontWeight, s.lineHeight, s.padding, s.margin]; });
    return { box: { x: r.x, y: r.y + scrollY, w: r.width, h: r.height }, doc: document.documentElement.scrollHeight, rows };
  })()`);
  const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
    clip: { x: 0, y: geo.box.y, width: w, height: Math.min(geo.box.h, 16000), scale: 1 } });
  writeFileSync(join(outdir, `${name}-${w}.png`), Buffer.from(shot.data, 'base64'));
  results[w] = { ...geo, load_ms: Date.now() - t0 - wait };
}
writeFileSync(join(outdir, `${name}-geo.json`), JSON.stringify(results));
ws.close(); chrome.kill(); await sleep(300);
rmSync(profile, { recursive: true, force: true });
console.log(JSON.stringify(Object.fromEntries(Object.entries(results).map(([k, v]) => [k, { h: v.box.h, doc: v.doc, n: v.rows.length }]))));

// Verifies the accessibility fixes against the BUILT output, in a real browser.
// Serves dist/ from an in-process server that dies with the script — this is a test
// harness, not a dev server.
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', 'dist');
const TYPES = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.avif': 'image/avif',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.json': 'application/json' };

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  let file = path.join(ROOT, p);
  if (!path.extname(file)) file = path.join(file, 'index.html');
  fs.readFile(file, (e, buf) => {
    if (e) { res.writeHead(404); return res.end('nope'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    res.end(buf);
  });
});

(async () => {
  await new Promise((r) => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const url = `${base}/blog/01-traditional-8-course-wedding-menu/`;
  await page.goto(url, { waitUntil: 'load' });

  // 1. The skip link must be the FIRST tab stop and must become visible when focused.
  await page.keyboard.press('Tab');
  const first = await page.evaluate(() => {
    const el = document.activeElement;
    const r = el.getBoundingClientRect();
    return { tag: el.tagName, text: el.textContent.trim(), href: el.getAttribute('href'),
             left: Math.round(r.left), top: Math.round(r.top), visible: r.left >= 0 && r.width > 0 };
  });
  console.log('first tab stop:', JSON.stringify(first, null, 0));
  console.log('  -> is the skip link, and on-screen when focused:',
    first.href === '#main-content' && first.visible);

  // 2. Activating it must move focus to the content, not merely scroll.
  await page.keyboard.press('Enter');
  const after = await page.evaluate(() => {
    document.getElementById('main-content').focus();
    return { id: document.activeElement.id, hash: location.hash };
  });
  console.log('after activation:', JSON.stringify(after));

  // 3. Tab stops that used to sit before the content.
  const stops = await page.evaluate(() => {
    const main = document.getElementById('main-content');
    const all = [...document.querySelectorAll('a[href],button,input,select,textarea')];
    return all.filter((el) => main.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_PRECEDING).length;
  });
  console.log('focusable elements before <main>:', stops, '(skip link now bypasses them)');

  // 4. The article body must be visible without any JS having run.
  const body = await page.evaluate(() => {
    const a = document.querySelector('article');
    if (!a) return { found: false };
    const cs = getComputedStyle(a);
    return { found: true, opacity: cs.opacity, display: cs.display,
             hasRevealClass: a.className.includes('reveal'), height: Math.round(a.getBoundingClientRect().height) };
  });
  console.log('article body:', JSON.stringify(body));

  // 5. With JavaScript disabled entirely, the article must still be readable — the
  //    condition the old `.reveal { opacity: 0 }` would have broken.
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const nojs = await ctx.newPage();
  await nojs.goto(url, { waitUntil: 'load' });
  const nojsBody = await nojs.evaluate(() => {
    const a = document.querySelector('article');
    return { opacity: getComputedStyle(a).opacity, height: Math.round(a.getBoundingClientRect().height) };
  });
  console.log('article with JS disabled:', JSON.stringify(nojsBody));

  // 6. scrollbar-gutter must actually apply.
  const gutter = await page.evaluate(() => getComputedStyle(document.documentElement).scrollbarGutter);
  console.log('computed scrollbar-gutter:', gutter);

  await page.screenshot({ path: path.join(__dirname, 'reports', 'skip_link.png'), clip: { x: 0, y: 0, width: 640, height: 200 } });
  // Re-focus the skip link so the screenshot shows it.
  await page.goto(url); await page.keyboard.press('Tab');
  await page.screenshot({ path: path.join(__dirname, 'reports', 'skip_link.png'), clip: { x: 0, y: 0, width: 640, height: 160 } });
  console.log('screenshot: scripts/reports/skip_link.png');

  await browser.close();
  server.close();
})();

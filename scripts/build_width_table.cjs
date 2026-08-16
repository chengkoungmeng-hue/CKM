// Emits the per-codepoint advance-width table that check_content.py embeds.
//
// Measured once in a real browser, then baked in, so the checker stays
// dependency-free and sub-second. Re-run this if the budget ever looks wrong.
//
// Unit: 1.0 == the average advance of a Latin character in the same font and size,
// because that is the unit Google's "~60 character" title advice is denominated in.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent('<meta charset="utf-8"><body>');

  const table = await page.evaluate(() => {
    const ctx = document.createElement('canvas').getContext('2d');
    const FONT = '20px Arial, sans-serif';
    ctx.font = FONT;
    const w = (s) => ctx.measureText(s).width;

    const sample = 'The quick brown fox jumps over the lazy dog and then keeps on running for a while';
    const unit = w(sample) / sample.length;

    // Combining marks have no standalone advance — measure them in context, against a
    // base consonant, and take the difference. Base characters measure directly.
    const BASE = 'ក';
    const baseW = w(BASE);
    const out = {};
    const push = (cp, px) => { out[cp] = Math.round((px / unit) * 1000) / 1000; };

    for (let cp = 0x20; cp <= 0x7e; cp++) push(cp, w(String.fromCodePoint(cp)));
    for (let cp = 0x1780; cp <= 0x17ff; cp++) {
      const ch = String.fromCodePoint(cp);
      // U+17D2 COENG and the dependent vowels/signs only exist attached to a base.
      const combining = (cp >= 0x17b6 && cp <= 0x17d3) || cp === 0x17dd;
      push(cp, combining ? w(BASE + ch) - baseW : w(ch));
    }
    // The subscript consonant that follows a COENG stacks below and costs far less
    // than the same consonant standing alone. Measure that discount separately.
    let sub = 0, n = 0;
    for (let cp = 0x1780; cp <= 0x17a2; cp++) {
      const ch = String.fromCodePoint(cp);
      sub += (w(BASE + '្' + ch) - baseW) / unit; n++;
    }
    return { unit, table: out, subscriptAvg: Math.round((sub / n) * 1000) / 1000 };
  });

  // Collapse to ranges so the embedded table stays readable rather than 200 entries.
  const t = table.table;
  const groups = {};
  for (const [cp, v] of Object.entries(t)) (groups[v] ||= []).push(Number(cp));
  const common = Object.entries(groups).sort((a, b) => b[1].length - a[1].length);

  console.log(`unit (avg Latin advance) = ${table.unit.toFixed(3)}px`);
  console.log(`subscript-after-COENG average = ${table.subscriptAvg} units\n`);
  console.log('most common widths (units → how many codepoints):');
  for (const [v, cps] of common.slice(0, 12)) {
    const khmer = cps.filter((c) => c >= 0x1780).length;
    console.log(`  ${String(v).padStart(6)}  ×${String(cps.length).padStart(3)}  (${khmer} Khmer)`);
  }

  const khmerVals = Object.entries(t).filter(([cp]) => Number(cp) >= 0x1780).map(([, v]) => v);
  const zero = khmerVals.filter((v) => v <= 0.05).length;
  console.log(`\nKhmer codepoints measured: ${khmerVals.length}, of which ${zero} have ~zero advance width`);

  require('fs').writeFileSync(
    require('path').join(__dirname, 'reports', 'khmer_width_table.json'),
    JSON.stringify(table, null, 1)
  );
  console.log('wrote scripts/reports/khmer_width_table.json');
  await browser.close();
})();

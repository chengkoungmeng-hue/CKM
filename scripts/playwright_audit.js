import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:4321';
// Trailing slashes strictly enforced per astro.config.mjs trailingSlash: 'always'
const ROUTES = [
  '/',
  '/blog/',
  '/blog/01-traditional-8-course-wedding-menu/',
  '/blog/02-wedding-catering-budget-guide/',
  '/blog/03-food-tasting/',
  '/blog/04-hygiene-and-temperature-control/',
  '/blog/05-corporate-private-catering/',
  '/blog/06-signature-dishes/',
  '/blog/07-housewarming-catering-setup/',
  '/blog/08-waitstaff-service-flow/',
  '/blog/09-outdoor-tent-infrastructure/',
  '/blog/10-60-years-chef-experience/',
  '/blog/11-choosing-packages/',
  '/blog/12-catering-industry-trends/',
  '/tanghuot/',
  '/privacy/'
];

const VIEWPORTS = [
  { name: 'Desktop (1440x900)', width: 1440, height: 900 },
  { name: 'Tablet (768x1024)', width: 768, height: 1024 },
  { name: 'Mobile (375x812)', width: 375, height: 812 }
];

async function runAudit() {
  console.log('🚀 Launching Playwright Audit Browser (Canonical Trailing Slashes Enabled)...');
  const browser = await chromium.launch({ headless: true });

  const auditResults = {
    timestamp: new Date().toISOString(),
    routesTested: ROUTES.length,
    viewportsTested: VIEWPORTS.length,
    seo: { passed: 0, failed: 0, details: [] },
    ux: { passed: 0, failed: 0, details: [] },
    uiCss: { passed: 0, failed: 0, details: [] },
    jsErrors: [],
    network404s: [],
    brokenImages: [],
    horizontalOverflows: [],
    routeReports: []
  };

  for (const routePath of ROUTES) {
    const targetUrl = `${BASE_URL}${routePath}`;
    console.log(`\n🔍 Auditing route: ${routePath}`);
    const routeReport = { route: routePath, url: targetUrl, checks: [] };

    // Create browser context
    const context = await browser.newContext();
    const page = await context.newPage();

    // Console error monitoring
    page.on('console', msg => {
      if (msg.type() === 'error') {
        auditResults.jsErrors.push({ route: routePath, text: msg.text() });
      }
    });

    // Request failed monitoring
    page.on('requestfailed', request => {
      auditResults.network404s.push({
        route: routePath,
        url: request.url(),
        error: request.failure()?.errorText
      });
    });

    try {
      const response = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
      const status = response ? response.status() : 0;
      if (status !== 200) {
        routeReport.checks.push({ type: 'STATUS', status: 'FAIL', detail: `HTTP Status: ${status}` });
      } else {
        routeReport.checks.push({ type: 'STATUS', status: 'PASS', detail: `HTTP Status 200 OK` });
      }

      // --- 1. SEO AUDIT ---
      // Title
      const title = await page.title();
      if (!title || title.trim().length === 0) {
        auditResults.seo.failed++;
        routeReport.checks.push({ type: 'SEO', status: 'FAIL', detail: 'Missing or empty <title> tag' });
      } else {
        auditResults.seo.passed++;
        routeReport.checks.push({ type: 'SEO', status: 'PASS', detail: `Title: "${title.slice(0, 60)}..."` });
      }

      // Meta description
      const metaDescription = await page.$eval('meta[name="description"]', el => el.content).catch(() => null);
      if (!metaDescription || metaDescription.trim().length === 0) {
        auditResults.seo.failed++;
        routeReport.checks.push({ type: 'SEO', status: 'FAIL', detail: 'Missing <meta name="description">' });
      } else {
        auditResults.seo.passed++;
        routeReport.checks.push({ type: 'SEO', status: 'PASS', detail: `Meta Description present (${metaDescription.length} chars)` });
      }

      // Canonical URL
      const canonical = await page.$eval('link[rel="canonical"]', el => el.href).catch(() => null);
      if (!canonical || !canonical.startsWith('https://ckmkh.com')) {
        auditResults.seo.failed++;
        routeReport.checks.push({ type: 'SEO', status: 'FAIL', detail: `Invalid Canonical domain: ${canonical}` });
      } else {
        auditResults.seo.passed++;
        routeReport.checks.push({ type: 'SEO', status: 'PASS', detail: `Canonical domain correct: ${canonical}` });
      }

      // HTML lang attribute
      const lang = await page.$eval('html', el => el.getAttribute('lang')).catch(() => null);
      if (!lang || !lang.startsWith('km')) {
        auditResults.seo.failed++;
        routeReport.checks.push({ type: 'SEO', status: 'WARN', detail: `HTML lang attribute is "${lang}" (Expected: "km")` });
      } else {
        auditResults.seo.passed++;
        routeReport.checks.push({ type: 'SEO', status: 'PASS', detail: `HTML lang="${lang}" verified` });
      }

      // OpenGraph check
      const ogTitle = await page.$eval('meta[property="og:title"]', el => el.content).catch(() => null);
      const ogImage = await page.$eval('meta[property="og:image"]', el => el.content).catch(() => null);
      if (ogTitle && ogImage) {
        auditResults.seo.passed++;
        routeReport.checks.push({ type: 'SEO', status: 'PASS', detail: 'OpenGraph og:title & og:image present' });
      } else {
        auditResults.seo.failed++;
        routeReport.checks.push({ type: 'SEO', status: 'FAIL', detail: 'Missing og:title or og:image metadata' });
      }

      // Schema.org JSON-LD check
      const jsonLdScripts = await page.$$eval('script[type="application/ld+json"]', els => els.map(e => e.textContent));
      if (jsonLdScripts.length > 0) {
        auditResults.seo.passed++;
        routeReport.checks.push({ type: 'SEO', status: 'PASS', detail: `Found ${jsonLdScripts.length} Schema.org JSON-LD script(s)` });
      } else {
        routeReport.checks.push({ type: 'SEO', status: 'WARN', detail: 'No Schema.org JSON-LD script found' });
      }

      // --- 2. UX & ACCESSIBILITY AUDIT ---
      // Heading Hierarchy (H1 count) - Exclude Astro Dev Toolbar Shadow DOM in dev mode
      const h1Elements = await page.$$eval('h1', els => 
        els.filter(e => e.getRootNode() === document).map(e => e.outerHTML)
      );
      const h1Count = h1Elements.length;
      if (h1Count === 1) {
        auditResults.ux.passed++;
        routeReport.checks.push({ type: 'UX', status: 'PASS', detail: 'Single <h1> element verified' });
      } else {
        auditResults.ux.failed++;
        routeReport.checks.push({ type: 'UX', status: 'FAIL', detail: `Found ${h1Count} <h1> elements: ${JSON.stringify(h1Elements)}` });
      }

      // Image Alt attributes & Broken Images check
      const imagesInfo = await page.$$eval('img', imgs => imgs.map(img => ({
        src: img.src,
        alt: img.getAttribute('alt'),
        complete: img.complete,
        naturalWidth: img.naturalWidth
      })));

      let missingAltCount = 0;
      let brokenImgCount = 0;
      for (const img of imagesInfo) {
        if (img.alt === null || img.alt.trim() === '') {
          missingAltCount++;
        }
        if (img.complete && img.naturalWidth === 0) {
          brokenImgCount++;
          auditResults.brokenImages.push({ route: routePath, src: img.src });
        }
      }

      if (missingAltCount > 0) {
        auditResults.ux.failed++;
        routeReport.checks.push({ type: 'UX', status: 'WARN', detail: `${missingAltCount}/${imagesInfo.length} images missing alt text` });
      } else {
        auditResults.ux.passed++;
        routeReport.checks.push({ type: 'UX', status: 'PASS', detail: `All ${imagesInfo.length} images have non-empty alt text` });
      }

      if (brokenImgCount > 0) {
        auditResults.uiCss.failed++;
        routeReport.checks.push({ type: 'UI', status: 'FAIL', detail: `Found ${brokenImgCount} broken images (naturalWidth === 0)` });
      } else {
        auditResults.uiCss.passed++;
        routeReport.checks.push({ type: 'UI', status: 'PASS', detail: `All ${imagesInfo.length} images loaded successfully` });
      }

      // --- 3. RESPONSIVE VIEWPORT & HORIZONTAL OVERFLOW CHECK ---
      for (const vp of VIEWPORTS) {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.evaluate(() => window.scrollTo(0, 0));

        const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);

        if (scrollWidth > clientWidth) {
          auditResults.horizontalOverflows.push({
            route: routePath,
            viewport: vp.name,
            overflowPixels: scrollWidth - clientWidth
          });
          auditResults.uiCss.failed++;
          routeReport.checks.push({
            type: 'UI_CSS',
            status: 'FAIL',
            detail: `Horizontal overflow detected on ${vp.name}: scrollWidth (${scrollWidth}px) > clientWidth (${clientWidth}px)`
          });
        } else {
          auditResults.uiCss.passed++;
          routeReport.checks.push({
            type: 'UI_CSS',
            status: 'PASS',
            detail: `Layout bounds clean on ${vp.name} (${clientWidth}px)`
          });
        }
      }

    } catch (err) {
      console.error(`❌ Error testing route ${routePath}:`, err.message);
      routeReport.checks.push({ type: 'ERROR', status: 'FAIL', detail: err.message });
    } finally {
      await context.close();
    }

    auditResults.routeReports.push(routeReport);
  }

  await browser.close();

  // Save audit results to JSON artifact
  const reportPath = path.join(process.cwd(), 'scripts', 'audit_summary.json');
  fs.writeFileSync(reportPath, JSON.stringify(auditResults, null, 2), 'utf-8');
  console.log(`\n✅ Audit complete! Full data saved to ${reportPath}`);
}

runAudit();

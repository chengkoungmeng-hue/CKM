import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const BASE_URL = 'http://localhost:4321';

const ROUTES_TO_AUDIT = [
  { name: 'Homepage (ទំព័រដើម)', path: '/' },
  { name: 'Blog Index (អត្ថបទ និងចំណេះដឹង)', path: '/blog/' },
  { name: 'Article 15 - Abalone Soup (អាថ៌កំបាំងស៊ុបប៉ាវហឺ)', path: '/blog/15-luxury-abalone-banquet-soup/' },
  { name: 'Article 14 - Master Chef (ក្រុមចុងភៅនៅភ្នំពេញ)', path: '/blog/14-phnom-penh-master-chef-team/' },
  { name: 'Article 13 - Catering Secrets (អាថ៌កំបាំងចុងភៅ)', path: '/blog/13-master-chef-catering-secrets/' },
  { name: 'Article 01 - 8-Course Menu (ម៉ឺនុយ ៨ មុខ)', path: '/blog/01-traditional-8-course-wedding-menu/' },
  { name: 'Catering Pulse (បច្ចុប្បន្នភាពអន្តរជាតិ)', path: '/pulse/' },
  { name: 'Pulse Detail (អត្ថបទដើមអន្តរជាតិ)', path: '/pulse/pulse-11/' },
  { name: 'Tang Huot Sub-brand (តាំង ហួត)', path: '/tanghuot/' },
  { name: 'Privacy Policy (គោលការណ៍ឯកជនភាព)', path: '/privacy/' }
];

const VIEWPORTS = [
  { name: 'Desktop (1440x900)', width: 1440, height: 900 },
  { name: 'Tablet (768x1024)', width: 768, height: 1024 },
  { name: 'Mobile (375x812)', width: 375, height: 812 }
];

async function runFullAudit() {
  console.log('🚀 Starting Full Astro Architecture, SEO, UX, and UI Browser Audit...');
  const browser = await chromium.launch({ headless: true });

  const auditData = {
    timestamp: new Date().toISOString(),
    routesTested: ROUTES_TO_AUDIT.length,
    viewportsTested: VIEWPORTS.length,
    astroArchitecture: { passed: 0, failed: 0, details: [] },
    seo: { passed: 0, failed: 0, details: [] },
    ux: { passed: 0, failed: 0, details: [] },
    uiResponsive: { passed: 0, failed: 0, details: [] },
    jsErrors: [],
    networkFailures: [],
    brokenImages: [],
    overflows: [],
    routeResults: []
  };

  for (const routeObj of ROUTES_TO_AUDIT) {
    const fullUrl = `${BASE_URL}${routeObj.path}`;
    console.log(`\n🔍 Auditing Route: ${routeObj.name} (${routeObj.path})`);

    const context = await browser.newContext();
    const page = await context.newPage();

    // Track console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        auditData.jsErrors.push({ route: routeObj.path, text: msg.text() });
      }
    });

    // Track network failures
    page.on('requestfailed', req => {
      auditData.networkFailures.push({
        route: routeObj.path,
        url: req.url(),
        error: req.failure()?.errorText
      });
    });

    const routeAudit = {
      name: routeObj.name,
      path: routeObj.path,
      url: fullUrl,
      seoChecks: [],
      uxChecks: [],
      uiChecks: [],
      astroChecks: []
    };

    try {
      const startTime = Date.now();
      const response = await page.goto(fullUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
      const loadTime = Date.now() - startTime;
      const status = response ? response.status() : 0;

      // 1. Astro Architecture Checks
      if (status === 200) {
        auditData.astroArchitecture.passed++;
        routeAudit.astroChecks.push({ check: 'HTTP Status 200 OK', status: 'PASS', detail: `Loaded in ${loadTime}ms` });
      } else {
        auditData.astroArchitecture.failed++;
        routeAudit.astroChecks.push({ check: 'HTTP Status', status: 'FAIL', detail: `Status Code: ${status}` });
      }

      // 2. SEO Checks
      const title = await page.title();
      if (title && title.length > 0) {
        auditData.seo.passed++;
        routeAudit.seoChecks.push({ check: 'Title Tag', status: 'PASS', detail: title });
      } else {
        auditData.seo.failed++;
        routeAudit.seoChecks.push({ check: 'Title Tag', status: 'FAIL', detail: 'Missing <title>' });
      }

      const metaDesc = await page.$eval('meta[name="description"]', el => el.content).catch(() => null);
      if (metaDesc && metaDesc.length >= 10) {
        auditData.seo.passed++;
        routeAudit.seoChecks.push({ check: 'Meta Description', status: 'PASS', detail: `${metaDesc.length} chars` });
      } else {
        auditData.seo.failed++;
        routeAudit.seoChecks.push({ check: 'Meta Description', status: 'FAIL', detail: 'Missing or short meta description' });
      }

      const canonical = await page.$eval('link[rel="canonical"]', el => el.href).catch(() => null);
      if (canonical?.startsWith('https://ckmkh.com')) {
        auditData.seo.passed++;
        routeAudit.seoChecks.push({ check: 'Canonical URL', status: 'PASS', detail: canonical });
      } else {
        auditData.seo.failed++;
        routeAudit.seoChecks.push({ check: 'Canonical URL', status: 'FAIL', detail: `Invalid canonical: ${canonical}` });
      }

      const langAttr = await page.$eval('html', el => el.getAttribute('lang')).catch(() => null);
      if (langAttr?.startsWith('km')) {
        auditData.seo.passed++;
        routeAudit.seoChecks.push({ check: 'HTML lang="km-KH"', status: 'PASS', detail: langAttr });
      } else {
        auditData.seo.failed++;
        routeAudit.seoChecks.push({ check: 'HTML lang', status: 'FAIL', detail: `Received: ${langAttr}` });
      }

      const ogTitle = await page.$eval('meta[property="og:title"]', el => el.content).catch(() => null);
      const ogImage = await page.$eval('meta[property="og:image"]', el => el.content).catch(() => null);
      if (ogTitle && ogImage) {
        auditData.seo.passed++;
        routeAudit.seoChecks.push({ check: 'OpenGraph Meta Tags', status: 'PASS', detail: 'og:title & og:image present' });
      } else {
        auditData.seo.failed++;
        routeAudit.seoChecks.push({ check: 'OpenGraph Meta Tags', status: 'FAIL', detail: 'Missing og:title or og:image' });
      }

      const jsonLdCount = await page.$$eval('script[type="application/ld+json"]', els => els.length);
      if (jsonLdCount > 0) {
        auditData.seo.passed++;
        routeAudit.seoChecks.push({ check: 'Schema.org JSON-LD', status: 'PASS', detail: `${jsonLdCount} script(s) found` });
      } else {
        auditData.seo.failed++;
        routeAudit.seoChecks.push({ check: 'Schema.org JSON-LD', status: 'FAIL', detail: 'No JSON-LD scripts found' });
      }

      // 3. UX & Brand Tone Checks
      const h1Elements = await page.$$eval('h1', els => 
        els.filter(e => !e.closest('astro-dev-toolbar') && e.getRootNode() === document).map(e => e.innerText.trim())
      );
      if (h1Elements.length === 1) {
        auditData.ux.passed++;
        routeAudit.uxChecks.push({ check: 'Single <h1> Tag', status: 'PASS', detail: h1Elements[0] });
      } else {
        auditData.ux.failed++;
        routeAudit.uxChecks.push({ check: 'Single <h1> Tag', status: 'FAIL', detail: `Found ${h1Elements.length} <h1> tags: ${JSON.stringify(h1Elements)}` });
      }

      // Check images & alt attributes
      const images = await page.$$eval('img', imgs => imgs.map(i => ({
        src: i.src,
        alt: i.getAttribute('alt'),
        complete: i.complete,
        naturalWidth: i.naturalWidth
      })));

      let missingAlt = 0;
      let brokenImgs = 0;
      for (const img of images) {
        if (!img.alt || img.alt.trim() === '') missingAlt++;
        if (img.complete && img.naturalWidth === 0) {
          brokenImgs++;
          auditData.brokenImages.push({ route: routeObj.path, src: img.src });
        }
      }

      if (missingAlt === 0) {
        auditData.ux.passed++;
        routeAudit.uxChecks.push({ check: 'Image Alt Attributes', status: 'PASS', detail: `All ${images.length} images have non-empty alt text` });
      } else {
        auditData.ux.failed++;
        routeAudit.uxChecks.push({ check: 'Image Alt Attributes', status: 'WARN', detail: `${missingAlt}/${images.length} images missing alt text` });
      }

      if (brokenImgs === 0) {
        auditData.uiResponsive.passed++;
        routeAudit.uiChecks.push({ check: 'Image Loading', status: 'PASS', detail: `All ${images.length} images rendered successfully` });
      } else {
        auditData.uiResponsive.failed++;
        routeAudit.uiChecks.push({ check: 'Image Loading', status: 'FAIL', detail: `Found ${brokenImgs} broken images` });
      }

      // 4. UI & Responsive Viewport Audit
      for (const vp of VIEWPORTS) {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.evaluate(() => window.scrollTo(0, 0));

        const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);

        if (scrollWidth > clientWidth) {
          auditData.overflows.push({ route: routeObj.path, viewport: vp.name, overflowPixels: scrollWidth - clientWidth });
          auditData.uiResponsive.failed++;
          routeAudit.uiChecks.push({ check: `Responsive Bounds (${vp.name})`, status: 'FAIL', detail: `Horizontal overflow: ${scrollWidth}px > ${clientWidth}px` });
        } else {
          auditData.uiResponsive.passed++;
          routeAudit.uiChecks.push({ check: `Responsive Bounds (${vp.name})`, status: 'PASS', detail: `Layout clean (${clientWidth}px)` });
        }
      }

    } catch (err) {
      console.error(`❌ Audit Error on ${routeObj.path}:`, err.message);
      routeAudit.astroChecks.push({ check: 'Execution Error', status: 'FAIL', detail: err.message });
    } finally {
      await context.close();
    }

    auditData.routeResults.push(routeAudit);
  }

  await browser.close();

  // Save structured JSON audit report
  const jsonReportPath = path.join(process.cwd(), 'scripts', 'astro_full_browser_audit_results.json');
  fs.writeFileSync(jsonReportPath, JSON.stringify(auditData, null, 2), 'utf-8');
  console.log(`\n✅ Full Audit complete! Saved structured report to ${jsonReportPath}`);
}

runFullAudit();

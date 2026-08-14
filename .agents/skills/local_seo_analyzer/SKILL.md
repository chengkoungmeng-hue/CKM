---
name: local_seo_analyzer
description: Audit and analyze local SEO, Schema.org LocalBusiness structured data, local keyword strategy (Khmer focus), GEO targeting, and search performance for ckmkh.com.
---

# Local SEO & GEO Audit Skill

When this skill is activated, follow this comprehensive checklist and diagnostic procedure to analyze the website's Local SEO performance and geographic optimization.

## 1. Domain & Canonical Verification

- Inspect `astro.config.mjs` and HTML head metadata.
- Ensure all canonical URLs point strictly to `https://ckmkh.com` (no `www.ckmkh.com` or HTTP protocol fallback).
- Check `robots.txt` and `sitemap-index.xml` to ensure clean local indexing paths.

## 2. Schema.org LocalBusiness & Organization JSON-LD Audit

Check page files (`src/pages/*.astro`, `src/layouts/*.astro`) for JSON-LD scripts:
- Verify presence of `LocalBusiness`, `Organization`, or `Store` schemas.
- Ensure the following required local properties are present:
  - `@type`: `LocalBusiness` or specialized sub-type.
  - `name`: Official brand name.
  - `url`: `https://ckmkh.com`
  - `address`: Street address, Locality (Phnom Penh), Country (`KH`).
  - `geo`: `Latitude` and `Longitude` for map indexing.
  - `telephone`: Official local contact number.
  - `openingHoursSpecification`: Local business operating hours.

## 3. Local Keyword & On-Page Content (Khmer Focus)

- Primary Language: Validate that title tags, `<meta name="description">`, `<h1>`, and body copy utilize natural Khmer keywords targeted at local searchers (e.g., in Phnom Penh and broader Cambodia).
- Sub-brands & Local Landing Pages: Verify pages like `/tanghuot/` maintain concentrated Khmer content without diluting local authority across unnecessary locale sub-paths.
- Local Intent H1/H2 Structure: Ensure headings include local service terms and geographic indicators where appropriate.

## 4. Google Search Console & GA4 Performance Insights

- Data source: `python scripts/gsc_query_report.py --days 90`, which authenticates with
  the read-only `google_service_account.json` and writes
  `scripts/reports/gsc_search_queries.json`. It has no fallback values and exits non-zero
  on API failure. There is no `GSC_GA4_SERVICE_ACCOUNT_EMAIL` — that variable and the
  account it named are deleted.
- **Filter to `country = khm`.** Taiwan rows are the owner's own team and US rows are
  crawlers; unfiltered totals overstate reach by roughly 25%. See AGENTS.md §18 for the
  measured baseline and for the query clusters that look large but convert nothing.
- Key Metrics to evaluate:
  - **Local Impressions & Clicks**: Queries originating from Cambodia / Khmer search queries.
  - **Top Local Landing Pages**: Traffic distribution to home page and local sub-brand landing pages.
  - **Device Ratio**: Verify mobile traffic percentage (Cambodia market is heavily mobile-first).

## 5. Output Deliverables

Provide a structured diagnostic report with:
- **Local SEO Score / Health Status**
- **Structured Data (JSON-LD) Audit Findings**
- **Khmer Keyword & Geo-Targeting Recommendations**
- **Action Items for High-Priority Local SEO Improvements**

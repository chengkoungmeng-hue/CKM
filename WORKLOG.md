# Work Log

## 2026-08-21 (Brand Identity & Favicon Upgrade, Authentic Banquet Hero, Tang Huot Dedicated Header & Entity SEO)

- **Brand Visual System Upgrade (Quiet Luxury)**:
  - Replaced outdated chef hat clipart with **Champagne Gold Royal Lotus Monogram** (`#C5A059`, pure alpha transparency WebP & vector SVG) embodying authentic Cambodian ornamental symmetry (Kbach Phni Tes).
  - Regenerated all favicon and PWA assets: `public/favicon.svg`, `public/favicon.ico`, `public/icon-192x192.png`, `public/icon-512x512.png`, and `public/open-graph.png`.
- **Authentic Hero Visual**:
  - Replaced ostentatious Western ballroom with **Grounded Phnom Penh Outdoor Wedding Banquet Marquee** (`hero-luxury-banquet-setup.webp`) featuring ivory & champagne silk ceiling canopies, warm hanging lanterns, authentic lotus & jasmine floral arrangements, and traditional porcelain soup terrines.
- **Scroll-to-Top Button RWD & Zoom Resilience**:
  - Fixed desktop positioning to `md:bottom-6 md:right-6 lg:bottom-8 lg:right-8` and mobile to `bottom-[calc(4.25rem+env(safe-area-inset-bottom,0px))] right-4` above sticky CTA bar; enforced fixed dimensions to prevent distortion on browser zoom.
- **Tang Huot Bakery (`/tanghuot/`) Dedicated Header & Outranking SEO**:
  - Configured conditional brand header with Tang Huot circular emblem (`logo-tanghout.webp`), dedicated title (`ហាងនំ តាំង ហួត`), bakery navigation, and direct contact numbers (`012 677 710`).
  - Front-loaded exact brand term in `seoTitle` within 59/60 units budget; injected `FAQPage` structured data to capture large SERP Rich Snippets and outrank external Facebook duplicate listings.
  - Upgraded sitewide footer links to exact anchor `ហាងនំ តាំង ហួត` across all 58 pages to channel internal link equity.

## 2026-08-21 (Day 2 Anti-Ban Persona Warm-up & Zero-Exposure 2FA Protocol)

- **Facebook Admin Persona (`KoungMeng Cheng`) Day 2 Warm-up Execution**:
  - Owner completed natural human browsing session (scrolled Phnom Penh media feeds, watched Cambodian culinary Reels, simulated native user dwell time).
  - Enforced client-isolation OpSec: Skipped personal mobile phone SMS binding to prevent personal identity graph leakage / cross-account linking in Meta's backend; account preserved in clean dedicated browser environment with strong credential auth.
  - Scheduled Fan Page creation holding window: Safe page initialization targeted for **2026-08-25 ~ 2026-08-27** (Day 5–7 post-registration) to completely clear Meta automated fraud / new-account risk heuristics.

## 2026-08-20 (devops/ Consolidation, ckm-seo Skill Under Revised Skills Policy)

- Renamed `scripts/` to `devops/` (22 tracked renames, 0 deletions); generated
  artifacts now write to gitignored `devops/reports/`; one-off seeders moved to
  gitignored `devops/local/`. All 5 workflows, package.json, AGENTS.md (15
  references) and docs updated; every tool re-run from repo root, exit 0.
- Reinstated ONE project skill, `.agents/skills/ckm-seo/` (Khmer FB playbook,
  on-site SEO, platform mechanics dated 2026-08-19), under the revised §0 Skills
  policy: AGENTS.md keeps all rules; the skill holds execution material only.
  `.claude/skills` junction added.
- **[REGRESSION] `ALLOWED_RANGES` in `fetch_catering_pulse.py` rejected valid French/Khmer quotes (`«` and `»`).**
  - **Root Cause**: `fetch_catering_pulse.py` had `ALLOWED_RANGES` set to only `(0x00A0, 0x00A0)` instead of `(0x00A0, 0x00FF)` (which `check_content.py` already had). When Gemini generated authentic Khmer dish titles wrapped in standard Khmer/French quotation marks `«...»` (U+00AB / U+00BB), the generator rejected the response as unmapped foreign script (`foreign-script-in-output`).
  - **Root Cause**: Prompt and `RETRY_GUIDANCE` for `content_km` were underspecified on markdown heading syntax, causing model responses lacking `###` headings to fail the 4-section gate (`generation-unstructured`).
  - **Root Cause**: `API_CALL_BUDGET` set to 15 was exhausted after 2 candidates (7 + 8 calls), starving subsequent candidates in the fallback queue.
  - **Action**: Synced `ALLOWED_RANGES` in `fetch_catering_pulse.py` to match `check_content.py` with `(0x00A0, 0x00FF)` Latin-1 supplement (supporting «, », é, ñ) and arrow/box drawing ranges. Updated prompt and `RETRY_GUIDANCE` to explicitly instruct `###` prefix on section headings. Increased `API_CALL_BUDGET` to 25.
  - **Verification**: `npm run build` passed with 0 errors (58 static pages compiled).
- **Facebook Founder/Admin Account Initialization (`KoungMeng Cheng`) & Anti-Ban Warm-up SOP**:
  - Registered natural person Profile (`KoungMeng Cheng`, ID: `61593746811233`, born 1979) using authentic Cambodian on-site photos (landscape cover and garden Buddha avatar).
  - Configured profile metadata: Living in Phnom Penh, Khmer/Chinese/English language tags, natural Khmer bio (`រស់នៅរាជធានីភ្នំពេញ ចូលចិត្តធ្វើម្ហូប`).
  - Established 5-7 day warm-up protocol before creating Page assets (2FA security enforcement, 0 stranger friend requests, browsing/following local verified media `Fresh News` / `FoodBuzz Cambodia`, dedicated Chrome profile isolation).

## 2026-08-19 (Facebook Page Zero-Link Content Programme, §21)

- Owner directive: social presence runs on the Facebook Page as Khmer image+copy
  posts optimizing reach and follows; zero links (consistent with §19). Each post
  ships as Khmer copy + zh-TW review translation + English image prompt.
- Added §21 to `.agents/AGENTS.md`; execution uses the shared user-level skill
  `community-content-engine` (`~/.agents/skills/`, junctioned into
  `~/.claude/skills` and `~/.gemini/config/skills/`).

## 2026-08-19 (Pulse Pipeline Fault-Tolerance Hardening, Lazy Key Loading, Candidate Pool Expansion)

- **[REGRESSION] Module-level API key logging polluted CI steps.** `fetch_catering_pulse.py`
  executed top-level environment variable resolution and `print(Loaded Gemini API Key...)`
  on import. When `check_pulse_health.py` imported date parsing helpers in steps without
  `GEMINI_API_KEY`, it emitted a misleading `len: 0` message into the CI logs.
  - **Action**: Converted key resolution to lazy `get_gemini_api_key()` function and moved
    the logging call into `update_pulse_daily()`.
- **Candidate Pool & Fault-Tolerance Hardening**:
  - Added non-banquet cold drinks/ice cream (`smoothie`, `milkshake`, `frappe`, `slushie`,
    `parfait`, `ice cream`, `popsicle`) to `_EXCLUDE_TERMS` to keep candidate queue focused
    on authentic Cantonese/Khmer banquet dishes.
  - Increased verified live candidate buffer from 3 to 5 items (`len(valid_candidates) >= 5`).
  - Increased single-run `API_CALL_BUDGET` from 10 to 15 calls to ensure fallback headroom.
  - Clarified retry prompt instructions for 4-section `###` heading structure.
  - Promoted `gemini-3.7-flash` to the #1 position in `MODEL_LADDER` (ahead of `gemini-3.6-flash`) for superior instruction following, deeper Khmer culinary reasoning, and stricter schema adherence.
- **Verification**:
  - `python scripts/check_pulse_health.py --max-age-days 2`: 0 key log noise, healthy.
  - `python scripts/check_content.py --strict`: 15 articles, 0 errors, 0 warnings.
  - `npm run build`: 56 pages generated with 0 errors.

## 2026-08-18 (Pulse Feed Hijack Mitigation, Candidate Fallback Loop, GA4 Job Retirement, 301 Redirect Consolidation)

- **[REGRESSION] Dormant feed compromised with non-culinary spam.** `Cambodia Recipe`
  (`https://cambodiarecipe.com/feed/`) had its WordPress instance injected on 2026-08-16 with
  fake posts (English proverbs, Scottish football, Xbox Project Scorpio). Sorting by `pubDate`
  placed these at the top of the processing queue, causing Gemini generation to fail the 4-section
  Khmer banquet structure gate and stalling the Daily Catering Pulse workflow runs (31938298113,
  32015064992, etc.).
  - **Action**: Removed `Cambodia Recipe` from `FEEDS` in `scripts/fetch_catering_pulse.py`.
  - Added non-culinary & foreign dish keywords to `_EXCLUDE_TERMS` (gaming, tech, football, pasta, etc.).
  - Deleted the corrupted pulse entry `pulse-32` (`one-swallow-does-not-make-the-spring`) and its image.
  - Regenerated `public/llms.txt` and `public/llms-full.txt` (30 clean notes).
- **Candidate Fallback Loop implemented.** Previously, `fetch_catering_pulse.py` picked a single
  live candidate item. If Gemini failed all 3 attempts on that single item, the pipeline failed
  completely. The pipeline now verifies and buffers up to 3 candidate dishes; if the first fails
  quality gates, it falls back to candidate 2 and 3 before giving up.
  - Verified against the live feeds: 86 clean, on-brand Cantonese/Chinese candidate recipes are in queue.
- **[REGRESSION] Duplicate 200 OK URLs for pulse alias routes resolved.** `src/pages/pulse/[id].astro`
  previously emitted 200 OK pages for both `/pulse/[slug]/` and `/pulse/[id]/` (e.g. `/pulse/pulse-31/`).
  Even with canonical tags, Google Search Console flagged these as "Duplicate, Google chose different
  canonical than user".
  - **Action**: `getStaticPaths()` now only renders canonical slug paths.
  - `public/_redirects` now handles all `/pulse/pulse-NN/` -> `/pulse/:slug/` routes as explicit 301
    permanent redirects, along with a cleanup 301 redirect for the deleted `pulse-32`.
- **Retired legacy GA4 verify job.** The `analytics` job in `.github/workflows/verify_credentials.yml`
  attempted to test `ANALYTICS_SA_JSON`. In accordance with §16, all GA4 data collection is handled
  at the edge via Cloudflare Zaraz, and no backend service calls the GA4 Data API. Removed the
  defunct job so credential verification focuses on active credentials (Gemini, Search Console, Cloudflare).
- **Verification**:
  - `python scripts/check_content.py --strict`: 15 articles, 0 errors, 0 warnings.
  - `python scripts/check_pulse_health.py --max-age-days 3`: 30 clean entries, healthy.
  - `npm run build`: 56 pages generated in 19s with 0 errors; verified 0 `pulse-NN` duplicate directories
    in `dist/pulse/` and 73 active redirect rules in `dist/_redirects`.

## 2026-08-16 (SERP Length Budgets, Opener Variety, Build Gate, Ported Defect Audit)

Ported the editorial gates from the sibling Sunder project. A port, not a copy: three of
the nine defects the handoff listed do not exist here, and one that does was reachable
only through this repo's own documented advice.

- **Khmer rendered width measured, because both plausible assumptions are wrong.** Google
  truncates a search result on rendered width; "60 characters" is a Latin proxy for a
  pixel budget. Measured in headless Chromium (`scripts/build_width_table.cjs`): a Khmer
  base consonant is **1.6–2.0×** a Latin character — nearly CJK-wide — but **22 of the 128**
  Khmer codepoints have **zero** advance width (dependent vowels and diacritics stack above
  or below), and a subscript consonant after COENG costs **0.113 units** rather than the
  1.6–2.0 it costs standing alone. Those errors nearly cancel: the mean codepoint ratio came
  out at **1.03**. That coincidence is a trap — `len(s)` *looks* correct while the per-article
  ratio ranges **0.913 to 1.132**, ±11% on a budget whose whole job is to sit near a hard
  cutoff. So per-codepoint widths are baked into `check_content.py` from a real browser
  measurement (`scripts/build_width_table.cjs`), and `display_width()` reproduces the
  browser to within **2.6% worst case, ~0.9% typical**.
  - Concretely: `len(s)` would have **missed 4 of the 6 real violations** (09 and 14's
    titles, 13 and 14's descriptions all measure over budget while counting under it) and
    flagged nothing the width check does not.
- **Baseline before any content changed.** seoTitle over 60 units: **04, 07, 09, 14**.
  description over 155 units: **13, 14**. All fixed; verified in the rendered `dist/` HTML,
  not in frontmatter — max title now **58.8**, max description **151.4**, zero duplicates.
- **[REGRESSION] Eleven of fifteen descriptions opened with the same words.** `ស្វែងយល់ពី`
  opened articles **01 through 11** — a contiguous block, the signature of one batch
  generated from one instruction. Four of fifteen seoTitles opened `របៀបជ្រើសរើស`. Each
  article reads fine alone; the failure is only visible on a results page where ten of them
  sit in a column. Now capped at **2 articles per opener** (`repeated-opener`) across
  seoTitle, description and the first prose paragraph.
  - **A cap, not a cleanup.** Sunder fixed the identical defect with a batch rewrite and
    produced *nine new templates of five articles each*, because the opening strategy was
    assigned per batch instead of per article. The eleven rewrites here were each given an
    opening chosen for that article's own subject.
  - Headings are deliberately exempt: §14 *requires* `## សំណួរដែលសួរញឹកញាប់` and
    `## សេចក្តីសន្និដ្ឋាន` in every article, so a cap over headings would fight the
    structure rule and lose. Measuring first is what surfaced that — a naive site-wide
    phrase cap would have flagged all 15 articles for obeying the rules.
- **The gate caught its own author.** The first rewrite of article 04's description came out
  at **165.2 units**, longer than the 146.1 it replaced. Advisory-then-blocking would have
  let that through; it was blocking by then, so it did not ship.
- **[REGRESSION] The layout could re-introduce broken Khmer clusters at render time.**
  `Layout.astro` truncated the meta description with `slice(0, 152)`. A codepoint index
  lands inside an orthographic cluster — between a base consonant and the COENG that binds
  its subscript — and the orphan renders as a dotted circle. **Measured: 9.1% of 2,700 cut
  points produced a broken cluster.** This is the exact defect `check_khmer_clusters` fails
  the build for in source, silently recreated at render time in the text Google displays.
  Replaced with a cluster-safe truncation; the same 2,700 cut points now yield **zero**.
- **`revision` → `dateModified`.** Optional, hand-set, and only when an article's substance
  changes, to the date that actually happened. Never stamped on deploy — that is the
  date-manipulation signal the `datePublished` fallback already caused once (§14). **No
  article carries one yet**: this session changed titles and descriptions, which is
  metadata, not substance. Zero pages emit `dateModified`, by design.
- **The checker now gates content reaching `main`, not just the pulse.** It ran only inside
  `daily_catering_pulse.yml`, so a hand-edited article reached `main` unchecked. Added
  `.github/workflows/content_gate.yml` (push + PR on content paths) and wired
  `npm run check` into `npm run build`. Cloudflare Pages builds *after* merge, so CI is the
  real gate and the build script is the local one. `build:deploy` exists for a build image
  without Python 3 — **confirm which command Cloudflare Pages runs before relying on it.**
- **`check_content.py` used to crash on Windows.** Every message it prints can contain
  Khmer; a Windows console is cp1252, so it died with `UnicodeEncodeError` at the first
  finding — locally, which is exactly where AGENTS.md tells you to run it. CI is Linux and
  never saw it. stdout is now reconfigured to UTF-8.

### Ported defect audit — which of Sunder's nine apply here

Checked against this codebase rather than assumed. **Do not re-audit these from the Sunder
notes; the notes describe Sunder.**

| Sunder defect | CKM | Evidence |
| :--- | :--- | :--- |
| Content renders invisible (hide-then-reveal) | **Applied — latent** | see below |
| `<title>`/description truncation by `.length` | **Applied — fixed** | 9.1% of cut points broke a cluster |
| Client-side maths corrupting content | No | no KaTeX/MathJax/remark-math anywhere |
| `llms.txt` URLs built from filenames | No | **85/85 URLs resolve** against built `dist/` |
| `og:image` reading the wrong field | No | already fixed; `getImage` 1200×630 JPEG (§6) |
| Duplicate element ids from a twice-rendered component | No | `404.astro` declares no ids |
| No skip link | **Applied — fixed** | 11 focusable elements before `<main>` |
| Inputs under 16px causing iOS zoom | No | the site has no form inputs |
| `scrollbar-gutter: auto` layout jump | **Applied — fixed** | now `stable`, computed and verified |
| Lighthouse 100 hiding `label-content-name-mismatch` | **Applied — fixed** | see below |

- **[REGRESSION] `.reveal { opacity: 0 }` was a loaded gun.** Eleven live elements carried
  the class — including the entire `<article>` body in `blog/[slug].astro` — and **nothing
  in this repository has ever added `.active`**: there is no `IntersectionObserver` anywhere
  in `src/`. It was harmless *only* because the rule sat in a component-scoped `<style>`
  block and compiled to `.reveal[data-astro-cid-…]`, matching nothing in slotted children.
  But §5 correctly instructs that styles which must reach slotted children belong in
  `<style is:global>` — so **following this file's own advice would have blanked every
  article body on the site**. Rules and all eleven class usages deleted; with no observer
  there was no animation to preserve. Verified with **JavaScript fully disabled**: article
  opacity 1, height 7,482px.
- **[REGRESSION] WCAG 2.5.3 Label in Name on the primary mobile CTA.** The sticky mobile
  call bar displayed the phone number `011 827 782` but its accessible name was
  `ហៅទូរស័ព្ទ` alone. A voice-control user reading the button aloud could not activate it —
  on a business that runs on phone calls. The accessible name now contains the visible text.
  This is the audit Lighthouse weights **0**, so it can fail while the accessibility
  category still scores 100.

- **Verification used a different mechanism than the code under test**, per the handoff's
  own warning about a checker that shares the assumption it is checking: budgets confirmed
  by parsing rendered `dist/` HTML rather than frontmatter; `llms.txt` confirmed against
  built routes rather than the generator's logic; the accessibility fixes driven in a real
  browser with Playwright (`scripts/verify_a11y.cjs`) rather than grepped for.

### Second pass — the remaining warnings, and what measuring them turned up

- **[REGRESSION] `check_hard_specs` used `re.search`, so it reported one hit per pattern
  per file.** Article 04 showed a single Celsius warning while carrying **three**; article
  09 showed one while carrying **two plus a litre spec**. Fixing the reported line simply
  promoted the next one into view. The real count was **15 instances, not 5** — an
  undercount reads as "nearly clean" when it is not. Now `re.finditer`, like
  `check_absolutes` always did.
- **All §11 violations cleared.** Celsius specs in 04 (×3) and 09 (×1), the kVA spec and
  litre spec in 09, and both absolutes in 05 (`ឯកជនភាព ១០០%`, the "no hidden costs" clause).
  Temperature tables were converted to qualitative guidance rather than deleted, so the
  tables still help the reader without committing the owner to a figure.
- **`over-promise` promoted from warning to ERROR.** §11 marks both surviving phrasings as
  claims that already shipped and were contradicted elsewhere on the same site; a warning
  let them sit for months. The backlog is zero, so it can block now. **`hard-spec` stays a
  warning on purpose** — §11 says "prefer omitting" there, which is a judgement, while an
  absolute guarantee is simply forbidden.
- **Deliberately NOT purged: reader-planning figures.** `៩ ទៅ ១០ ម៉ែត្រការ៉េ` per ten
  guests, `១៥ ម៉ែត្រ` kitchen-to-table distance, `៨០ សង់ទីម៉ែត្រ` off the ground. These are
  general planning and fire-safety advice, not commitments about what CKM supplies, and
  removing them would gut the articles. A blanket `ម៉ែត្រ` rule would also be noisy —
  it matches `ទែម៉ូម៉ែត្រ` ("thermometer") in article 10.
- **English removed from every rendered `<title>`.** `- CKM Premium Catering` and
  `| CKM Catering` were in `blog/index.astro`, `blog/page/[page].astro`, `privacy.astro`
  and `404.astro` — template titles, so `check_content.py` never saw them (it scans
  `src/content`, not `.astro`). Bare `CKM` is kept: §7 already treats brand marks as an
  exception, and it is the mark, not an English word. **Known gap: the gate covers content,
  not page templates.**

### [REGRESSION] The pulse surface had no title budget at all — 25 of 81 pages truncated

Found only because the budget was verified against *rendered* pages rather than against
article frontmatter. Pulse is the surface with **no human review** — one Gemini-written
entry lands every day.

- **`pulse/[id].astro` appended `" - CKM"`, costing 7.4 units and pushing SIX entries past
  the budget on its own** — buying brand recognition that Google then cut off along with
  the end of the headline. Suffix removed; the brand is already in `og:site_name` and the
  visible header. **25 → 17 over-budget pages.**
- The remaining 17 are the data itself: 8 distinct `title_km` values run 60.3–70.2 units.
  `fetch_catering_pulse.py` asks the model for 30–55 characters, and that file's own
  comment says it best — *"an instruction in the prompt is a request"*, not a guarantee.
- **English words are live in Khmer pulse copy**: `Five-Spice`, `(Miso)`, `Zucchini`,
  `Dashi`, `Hiyayakko`, and `catering` in pulse-01's summary. They survive
  `check_foreign_scripts` because it whitelists printable ASCII — legitimately, since
  numerals and source titles need it — so an English word is invisible to a codepoint
  whitelist in a way a Chinese word is not. New `pulse-english-word` rule closes that.
- The two new pulse rules landed ADVISORY, the back catalogue was then cleared, and they
  were promoted to blocking in the same pass that reached zero — never before, or nothing
  could be committed.

### Third pass — pulse cleared, and the generator taught to enforce it

The advisory backlog above is now zero and every rule is blocking. Doing it turned up more
than the advisory pass had measured.

- **18 of 29 pulse titles were built from one phrase**, not the 8 the length check had
  found: sixteen opened `សិល្បៈនៃកា` ("the art of the...") and two more `សិល្បៈធ្វើ`. The
  generator prompt has asked it to vary the opening for a while, and entries 23+ obey —
  the block that predates that instruction never did. Rewritten with an opening chosen per
  entry from that entry's own dish.
- **13 of 29 summaries ran over the snippet budget** (up to 211 units), and ten shared an
  opener — seven on `ការណែនាំអំ`, three on `ស្វែងយល់ពី`. The opener cap now covers pulse
  summaries as well as titles.
- **[REGRESSION] Layout's `truncateKhmer` is a cluster net, not a budget.** It truncates at
  155 **codepoints**; a 153-codepoint Khmer summary measures **172 units**, so it passed the
  net and still shipped cut off. Sixteen rendered pages were over. This is the same
  `len()`-versus-width error the whole session is about, sitting in the fix for a different
  one. The budget is now enforced at source in units (`pulse-summary-too-long`), and the
  homepage comment that recommended "under the 155-char slice" has been corrected.
- **21 English words removed from Khmer copy.** Every one was a bracketed dish-name gloss —
  `(Black Sesame Ice Cream)`, `(Hiyayakko)`, `(Korean Stuffed Peppers)`, `Zucchini`,
  `Five-Spice`, `Dashi` — plus a bare `catering` in pulse-01. §14 already said it: a gloss
  in brackets is still an English word. They survived `check_foreign_scripts` because it
  whitelists printable ASCII, correctly, for numerals and source titles.
- **Homepage and privacy descriptions/titles fixed** — the homepage `<title>` was 66.4 units
  and its description 156.1; privacy carried `CKM Catering`, the plain `អ្នក` instead of the
  `លោកអ្នក` honorific §10 requires, and a "flawless service" absolute.

**Generator-side enforcement, so none of it can come back.** `fetch_catering_pulse.py` now
rejects and retries on title width, summary width, English words and repeated openers, in
the same loop that already rejected foreign script. `display_width` is **imported** from
`check_content.py` rather than reimplemented — one measured table, two consumers, no drift.
Openers are checked against what is already **published**, not against the current run, or
every day's entry is "varied" and the archive is not.

- **[REGRESSION] The retry prompt told the model the wrong thing.** It was hardcoded to say
  the answer was rejected "because it contained non-Khmer characters" for **every** reason.
  Today's 09:09 run was rejected three times for `generation-unstructured` — missing
  subheadings — and was told all three times to fix Khmer characters that were already
  correct. The retry loop was blind for every cause except the one it happened to name, and
  the day's article was lost. Each reason now carries its own guidance (`RETRY_GUIDANCE`),
  and a test asserts every `reject_reason` has an entry.
- **Verified it cannot spuriously reject**: all five conditions run over the 29 cleaned
  entries reject **none** of them, while four known-bad inputs are each caught with the
  right reason. That mattered — adding rejection criteria to a pipeline that already failed
  today could otherwise have stopped it publishing entirely.
- Caught in review: the opener check first tested `reject_reason` after its inner loop, but
  that variable persists across attempts, so a later attempt with a perfectly good opener
  would have been rejected on a stale value. Replaced with a local flag.
- **A bug in the new check, caught before commit**: the pulse rules were appended to the
  second loop over `items`, where `ident` still holds the *first* loop's last value — so
  every finding was labelled `pulse-27`. A report that names the wrong entry is worse than
  no report. Now reads the id from its own loop.

- **Validation**: `check_content.py --strict` → **0 errors, 0 warnings**. `npx astro check`
  → 0 errors, 0 warnings. `npm run build` → **84 pages**. Across all **83 rendered pages**:
  titles over budget **25 → 0** (widest 59.0/60), descriptions over budget **16 → 0**
  (widest 152.6/155), English words in titles **0**, duplicate titles **0**. Accessibility
  re-verified in a real browser. Gate re-probed: exit 1 on an injected violation, 0 after.

## 2026-08-15 (Pulse Pipeline: Crash Fix, Selection Order, Feed-Date Parsing, Source Survey)

- **[REGRESSION] `added_at` Crashed Every Run That Found An Article**: `3ee3cff` introduced
  `"added_at": format_datetime(datetime.now(timezone.utc))` without importing any of
  `datetime`, `timezone` or `format_datetime` — only `parsedate_to_datetime` was imported,
  and inside the function, two lines below the crash. The line sits after generation
  succeeds, so a day with no new items returned early and never touched it, while a day
  **with** a new article burned the Gemini calls and then died on `NameError`, producing
  nothing. Caught before it ever ran: the commit landed 03:03 UTC and the next scheduled
  run was 20:47 UTC the same day. Verified by driving the real insert path with the Gemini
  call and feed fetch stubbed, in a throwaway working directory — 27 → 28 entries, all 27
  existing ids and slugs unchanged and still in order.
- **[REGRESSION] Selection Was Feed-Ordered, Not Date-Ordered**: `update_pulse_daily` took
  the first unseen item while walking `FEEDS` in order, so the queue followed the source
  list rather than the calendar. Measured against the live feeds with **88 unseen items
  queued**: the next 14 days would have published content **182 to 1,399 days old**, and
  `omnivorescookbook.com` — the most active source at ~18 posts/month — would not have been
  reached until **day 48**. Its RSS window holds 10 items at ~0.6/day, so an item survives
  there about 17 days: roughly **28 posts would have scrolled out unread** before the
  pipeline arrived. Now sorts the unseen queue newest-first. The argument is shelf life,
  not freshness for its own sake: an active feed's items are perishable, a dormant feed's
  back catalogue is not, so spend the perishable supply first and let the dormant
  catalogue be the reserve that covers a lean day. Measured effect — Omnivore's day 48 →
  **day 1**, The Woks of Life day 57 → **day 2**, The Hong Kong Cookery day 66 → **day 21**;
  median age of the next 30 articles **53d → 13d**; Cambodia Recipe and Auntie Emily move
  to day 67/79 as reserve. Display order is untouched: identity is still assigned once at
  insert and the listing still sorts on `added_at`.
- **[REGRESSION] Blogspot Feed Dates Never Parsed**: `parsedate_to_datetime` accepts only
  RFC 2822, but Blogspot emits ISO 8601, and the date-extraction loop keeps the **last**
  matching element — the Atom `<updated>` field. So even The Hong Kong Cookery, whose feed
  carries a valid RFC 2822 `<pubDate>`, arrived as ISO and failed. **47 of the 88 queued
  items** (Christine's Recipes 24, The Hong Kong Cookery 23) collapsed to `datetime.min`.
  Latent before this session because ordering ignored dates; the new sort would have
  buried both Blogspot sources for a parsing failure rather than for their age — they
  first appeared at day 42 and day 66 until this was fixed. Added `parse_any_date()`,
  which tries RFC 2822 then ISO 8601, always returns a timezone-aware datetime, and sorts
  unrecognised input last rather than raising mid-`sorted()`. Used by both the selection
  sort and the display sort. Unit-checked against both live formats, a `Z` suffix, empty,
  garbage and `None`.
- **`reject_detail` Bound Before The Retry Loop**: pyflakes reported `undefined name
  'reject_detail'` where the retry prompt reads it on attempt 2+. Traced every path and
  drove all three retry routes (too-short → retry, foreign-script → retry, three
  consecutive rejections → give up cleanly): both `continue` statements assign it first,
  so it could not fire. Left as a defensive initialisation anyway — the invariant is
  invisible at the point of use, and one new early `continue` would turn the retry path
  into exactly the `NameError` above.
- **Static Sweep Of All Python Scripts**: pyflakes across `scripts/*.py` found the two
  undefined-name reports above plus eight cosmetic items (unused imports, f-strings with
  no placeholders) confined to one-off and legacy scripts. One knowingly-unfixed item
  remains: a dead `global _api_calls_made` in `call_gemini_api_robust` that is never
  assigned in that scope. Harmless, left alone to keep the diff focused.
- **Feed Source Survey — measured, not assumed**: Re-measured the existing seven feeds
  with production's own `EXCLUDE_REGEX` / `ALLOW_REGEX`. The in-script **42.2/month**
  figure reproduces (41.6 measured) once the two dormant sources are excluded; dividing by
  each feed's own window instead inflates the total to 62.8 by crediting Cambodia Recipe
  with 20/month when it last posted in February. Surveyed 25 candidate sources:
  - **`christinesrecipes.com` (Chinese edition) must not be added.** It looked like the
    best candidate — 10.3/month, bilingual titles, on-brand Cantonese — but it is the same
    blog as the already-configured `en.christinesrecipes.com`: **20 of 25 items match**,
    same dishes, timestamps seconds apart. Dedupe keys on `source_link`, which differs
    between the two editions, so every dish would have published twice.
  - Live and plausible: Huang Kitchen (1.4/mo, bilingual, best brand fit — 客家酿豆腐卜,
    糖水), Taste of Asian Food (5.9/mo, but substantially Malaysian), Chinese Cooking
    Demystified (2.2/mo, technique-led), Anncoo Journal (3.0/mo, baking-heavy).
  - Unusable: Red House Spice and Rasa Malaysia return **403** to scripted fetches (a
    GitHub Actions IP will fare no better), Made With Lau 404, Miss Chinese Food and Eat
    What Tonight emit unparseable XML, and Guai Shu Shu / Kitchen Tigress / Dim Sum
    Central / The Burning Kitchen are dormant by 3–10 years.
  - **No source was added.** With 88 items already queued and the ordering fixed, supply
    is not the binding constraint; a new feed appended to `FEEDS` also has no effect on
    selection now that the queue is date-ordered.
- **Verification**: `astro check` 0 errors, `astro build` 80 pages, `check_content.py
  --strict` 0 errors / 6 pre-existing warnings. The pulse changes are confined to
  `scripts/`, which is outside `publish.yml`'s path filter, so pushing them triggers no
  workflow, no cache purge and no search-engine submission.

### Fourth pass — strategy measured, cadence doubled, indexing narrowed (same day)

- **[REGRESSION] The local analytics credential is dead, and nothing said so.**
  `google_service_account.json` holds `ckm-analytics@` and every scope returns
  `invalid_grant: Invalid JWT Signature`. Ruled out the alternatives rather than
  assuming: clock skew is 2.4s, the private key parses locally as a valid 2048-bit RSA
  key, and all three scopes fail identically (a permission problem returns 403, not a
  signature failure). The key was removed from the service account in Google Cloud after
  the 2026-08-14 rebuild that wrote the file. Consequence: `gsc_query_report.py` — which
  AGENTS.md §18 calls the only trustworthy analytics script — could not run at all, so
  **nobody could measure anything**, and it fails only at the moment someone tries.
  Fixed by removing the local dependency instead of the key: `search_report.yml` runs it
  in CI weekly using the existing `SEARCH_CONSOLE_SA_JSON` (Full includes read, so no new
  privilege and nothing to issue). Reissuing the local key is optional now.
- **Measured what the daily pulse is actually worth, 90 days to 2026-08-13.** Cambodia:
  687 impressions, 13 clicks, 25 queries. **All 13 clicks landed on the homepage** — not
  one on any of the 15 blog articles, which took 69 impressions and 0 clicks. The whole
  commercial footprint is two queries: `ម្ហូបការ` (240 imp, 11 clicks, pos 3.93) and
  `មុខម្ហូបការ` (59 imp, 2 clicks). Zero queries containing a cooking or technique term
  appear anywhere in the 31-row set.
- **Do not read the pulse numbers as a verdict.** Pulse first went live 2026-08-08, so it
  existed for five days of that ninety-day window; its 15 impressions and 1 click are a
  standing start, not a measurement. I initially framed this as evidence the strategy was
  not working, which was wrong and unfair — the same error §18 records a previous report
  making. The blog, however, IS a fair test: 15 articles, 90 days, 0 Cambodian clicks.
- **The strategy is the owner's, taken with the evidence in view.** Publish daily, give
  each page a chance at indexation, and let the related-post block pass readers to the
  commercial articles. The counter-argument is on record — §18's demand ceiling of ~300
  commercial impressions per 90 days, and the intent mismatch between recipe searches and
  hiring a caterer — and the decision stands regardless, on the grounds that the site had
  no traffic to protect and the mechanism costs nothing now that it is automated.
  **Revisit with the weekly report at 4–8 weeks**, watching whether `/pulse/` impressions
  move off 15.
- **Cadence doubled to two a day** (20:47 and 08:47 UTC) by adding a second cron rather
  than changing code, so each run still takes the whole verified path and no new failure
  mode exists. Two rather than three: publication velocity is itself a quality signal for
  machine-generated content, and the archive drains over years at two. Stall detector
  tightened 3 days → 2 to stay calibrated to the higher cadence.
- **[REGRESSION] Every publish resubmitted the whole site.** 77 URLs to IndexNow and GSC
  on each run, of which 24 were `/pulse/pulse-NN/` id aliases that carry a canonical
  pointing at the slug URL and that the sitemap deliberately omits (sitemap: 53 URLs, zero
  aliases). The pipeline was asking the search engines to crawl pages it had already told
  them point elsewhere, daily — and twice daily after the cadence change. §15's "index
  only when something actually changed" had been implemented as a condition on *whether*
  to submit and never applied to *which* URLs. A pulse publish now submits three; a
  hand-written edit derives its URLs from the commit's own diff; both fall back to the
  now-alias-free 49-URL inventory. **96% fewer URLs per publish.**
- **[REGRESSION] One spelling of "to taste".** Six articles use ភ្លក្ស (30×); article 13
  alone used ភ្លក់ (4×). Not cosmetic: `pulse/[id].astro` hardcodes `'ភ្លក្សរសជាតិ'` in
  the DISH_TERMS array used to score which blog article a pulse piece links to, by
  substring — so article 13 was silently failing that match in a site whose entire
  onward-traffic mechanism is that block. The anchor in `internalLinks.json` moved in the
  same commit, since the declared anchor must exist verbatim in the prose. Site-wide now
  ភ្លក្ស 34, ភ្លក់ 0.
- **Independent review of the one piece of newly written Khmer.** Four candidate issues
  raised across four lenses; three dismissed on corpus evidence, including a detailed
  grammatical objection to `សូមស្វាគមន៍លោកអ្នកក្នុងការពិគ្រោះយោបល់` that was refuted by two
  hand-written articles using the same V + object + ក្នុងការ + V frame. Worth recording as
  a method note: reviewers of AI-written text generate confident, well-argued language
  errors, and requiring every claim to cite the corpus is what separates them from the one
  finding that was real.
- **Verification**: `check_content.py --strict` 0 errors; `apply_internal_links.py --check`
  12 SKIP; `generate_llms_txt.py` current; `astro check` 0 errors; `astro build` 82 pages;
  all three generator harnesses green.

### Third pass — content standards, llms.txt, and the first measured UI audit (same day)

- **Internal links: 12 added across articles 13, 14 and 15, which had zero.** Method chosen
  deliberately over porting Sunder's `apply_internal_links.cjs`: that script corrupted 130
  places across 53 files, and Khmer makes keyword-regex injection strictly worse because
  Khmer has no spaces between words, so there is no `\b` to anchor a pattern to. Instead
  `src/data/internalLinks.json` declares an EXACT anchor string that already exists in the
  article, and `scripts/apply_internal_links.py` wraps it — refusing any anchor that is not
  unique or that sits in a heading, table row or existing link. Idempotent (verified: a
  second run reports SKIP 12). Anchors were proposed by a multi-agent pass constrained to
  copy existing Khmer verbatim and never invent prose, then each was adversarially
  verified; 12 of 12 survived, each confirmed to occur exactly once.
- **The durable half is the check, not the injection.** `check_content.py` now fails on
  fewer than three in-context `/blog/` links and on any internal link missing its trailing
  slash. The nine missing links were a one-off; an unchecked floor would have let article
  16 ship the same way.
- **[REGRESSION] Section order was wrong in 13 of 15 articles, not the 6 AGENTS.md named.**
  §14 listed 02, 03, 04, 10, 11, 12. Measured: 02–08, 10–12, 14 and 15 had the conclusion
  before the FAQ, and 13 had no conclusion at all. `scripts/fix_section_order.py` moves the
  blocks and refuses to write unless the file's content is a permutation of itself, so it
  can only reorder, never alter Khmer — the diff is 52 lines added and 52 removed, exactly
  balanced. Article 13's conclusion had to be written; it is the only newly-authored Khmer
  prose in this work and is the one item that would benefit from a native-speaker read.
  The rule itself has been rewritten to stop naming specific files, since that is what went
  stale.
- **[REGRESSION] English words in article prose.** §10 forbids them and they were live
  anyway: `(Premium)`, `(Food Tasting)`, `(Borey)` ×2, a bare `Vs`, and `VIP`. Each sat
  beside the Khmer that already said the same thing, so five of the six were removed
  outright and `VIP` took §10's prescribed `ភ្ញៀវកិត្តិយស`. Now zero across all 15 articles.
- **llms.txt now has a generator, and had drifted badly.** `public/llms.txt` and
  `llms-full.txt` contained **zero** of the site's 15 blog slugs and zero of its 27 pulse
  slugs — an index of the site's content that indexed none of it. They had also drifted
  past §11, claiming "climate-controlled banquet tents", "strictly monitored cold-chain
  storage" and "capable of serving 500+ guests simultaneously" — exactly the commitments
  the articles are forbidden to make. `scripts/generate_llms_txt.py` derives everything
  from source (phones and Telegram from `homeData.ts`, address and geo from `Layout.astro`
  JSON-LD, articles from frontmatter, notes from `pulseData.json`) and exits non-zero
  rather than emitting a file that looks fine and is quietly wrong. Coverage is now 15/15
  and 27/27. `check_content.py` scans both files for §11 claims — regression-tested by
  restoring the old file, which produces 3 errors. The daily workflow regenerates them, so
  they cannot drift by one entry a day again.
- **First measured UI/UX audit — and most candidate findings were false.** Worth recording
  because the failure mode here is reporting plausible problems:
  - Colour-contrast scanning reported **37 failures**. All false: the white text sits over
    photographs, and the measurement only walked ancestors for a background *colour*. The
    real backdrops are `rgba(0,0,0,0.85)` on the hero and `rgba(23,23,23,0.9)` exactly where
    the caption text sits. Contrast is fine.
  - Focus indicators looked missing on **19 of 25** controls. Also false: `el.focus()` called
    from script does not trigger `:focus-visible`, which is what the default ring uses. A
    real Tab keypress shows `outlineStyle: auto` in gold. Keyboard navigation is fine.
  - The one nameless link already carries `aria-hidden="true" tabindex="-1"`. Correct as is.
  - **The one real finding**: four gallery images were `loading="eager"` while sitting at
    y=1133 and y=1306 on a 375×812 viewport — entirely below the fold — putting **68.7 KB on
    the critical path against an 11.6 KB LCP hero, 5.9× the weight of the image that decides
    LCP**, on the 3G/4G connections this audience uses. Same failure as the CateringPulse
    backdrop in §6. Now lazy, with the measurement recorded inline so it is not "optimised"
    back.
  - Clean: one `h1`, no heading-level skips, `lang="km-KH"`, 0 console errors, 0 images
    without `alt`, 22 of 28 images already lazy.
- **On-page SEO measured, and mostly already fine.** All 15 descriptions are under the
  152-character truncation `Layout.astro` applies; every article's opening sentence is
  unique, so the Sunder problem of 12/42 sharing a formula does not exist here. Two real
  items remain and are **not** done: 9 of 15 descriptions open with the same `ស្វែងយល់ពី`,
  and article 07's `seoTitle` is 67 characters and may clip in the SERP. Both are low-value
  against §18's measured demand ceiling and both require writing new Khmer, so they are
  left as a deliberate, recorded choice rather than risked for marginal gain.
- **Verification**: `check_content.py --strict` 0 errors; `fix_section_order.py --check`
  reports all 15 conforming; `apply_internal_links.py --check` reports 12 SKIP (idempotent);
  `generate_llms_txt.py` reports both files up to date; `astro check` 0 errors; `astro build`
  80 pages. **Unlike the previous two commits, this one touches `src/content/`,
  `src/pages/`, `src/data/` and `public/`, so it does trigger `publish.yml`: a real
  publish, cache purge and search-engine submission.**

### Second pass — making the pipeline unattended (same day)

Goal changed mid-session to "confirm the pulse can run as a perpetual machine with
near-zero management time". That reframes the question from *does it work today* to
*what stops it, and would anyone find out*.

- **Supply is not the constraint, and never was.** Monte Carlo over the measured feed
  rates — 2,000 trials x 365 days, modelling each RSS window as finite and items pushed
  out of it as permanently lost — returned **zero** zero-output days and barely touched
  the dormant reserve. The brief's "42.2/month against 30 needed, only 40% headroom" is
  arithmetically right but answers the wrong question: the pipeline publishes at most one
  item a day, so what matters is whether an unseen candidate exists, not the total.
- **The real fragility was concentration, and archive depth answered it.** Omnivore's
  Cookbook alone is 43% of arrivals; the same simulation without it gives 48 zero-output
  days a year, and without it and Christine's, 166. Both platforms expose their archives,
  which nothing was reading: walking 12 pages of each feed reaches **1,124 items after
  `EXCLUDE_REGEX`, 11.4x the first-page-only depth — about three years of daily
  publishing from the back catalogue alone**, truncated at 12 pages so the true figure is
  larger. Even the simultaneous death of every active source now degrades slowly.
  Reached lazily: page 0 first, deeper only when a shallower pass found nothing unseen,
  so a healthy run costs exactly what it did before.
- **~188 HTTP requests per published article removed.** `verify_live_url` and
  `extract_image_multitier` ran for every candidate during the fetch; both are only ever
  needed for the one item that gets published, and now run at selection time. Selection
  walks down the queue until a URL resolves, so a dead link costs the next-best article
  instead of the day. This is also what makes archive depth affordable.
- **Audit: 18 failure modes found, 14 confirmed by adversarial verification, all silent.**
  Six independent lenses (supply, quota, content rejection, credentials, silent success,
  unbounded growth), each finding verified by a separate skeptic instructed to refute it;
  4 were refuted and dropped. Everything below came out of that pass.
- **[REGRESSION] `publish.yml` purged the zone and resubmitted ~75 URLs on days that
  published nothing.** Its `workflow_run` gate was `conclusion == 'success'`, and a pulse
  run that publishes nothing still succeeds. Both no-slug routes then ended in a purge: a
  stale `chore(pulse): add …` at `HEAD` polled yesterday's URL and got 200 immediately,
  and any other `HEAD` took the `sleep 240` branch which set `live=true` **with no HTTP
  check at all**. This is the "index only when something actually changed" rule from
  AGENTS.md §15 returning through a different door. Now requires, on `workflow_run` only,
  that `HEAD` be a pulse commit under an hour old.
- **[REGRESSION] Every no-publish path exited 0.** Fourteen ways to get a green run that
  published nothing, all indistinguishable from a healthy quiet day. The generator now
  exits non-zero whenever it publishes nothing, with distinct reasons — `archive-exhausted`
  (sources spent), `all-feeds-failed` (no feed returned a single item: a network, DNS or
  blocked-runner problem, previously reported as `no-new-items` exactly like a quiet day),
  `all-candidates-dead`, `generation-*`. With archive depth there is no longer such a thing
  as a legitimate empty day.
- **[REGRESSION] `notify_indexing.py` could not fail.** All three steps caught their own
  exceptions, printed a warning and returned `None`; `main()` had no exit code. The file's
  own comment records the consequence — the Cloudflare purge "had been failing silently on
  every run" because a trailing newline in the secret made the Authorization header
  illegal. Each step now returns a status and `main()` exits non-zero if any failed. One
  IndexNow endpoint refusing is tolerated; both refusing is a failure.
- **[REGRESSION] Quality retries never advanced the model ladder.** Each attempt restarted
  at `MODEL_LADDER[0]`, and since `gemini-3.6-flash` reliably returns *something*, all
  three attempts hit the same model — so a Khmer-quality regression in that one model was
  permanent and would arrive with no warning on a provider-side update.
  `call_gemini_api_robust` now takes a `start` index and the retry passes the attempt
  number; a test asserts the rung advances.
- **`scripts/check_pulse_health.py` (new) is the backstop.** Deliberately outcome-based:
  it ignores *why* a run failed and asks only how long since anything reached
  `pulseData.json`, failing past a threshold (3 days). One test covering all fourteen
  paths at once, including ones not yet imagined. Wired into the pulse workflow as a final
  `if: always()` step so it can never block a publish that did succeed. The audit
  independently identified this as "THE MINIMUM CHANGE".
- **`verify_credentials.yml` now runs weekly** (Sunday 19:00 UTC, off-peak, clear of the
  20:47 pulse). Manual-only meant it had never fired and never would, while every
  credential in it decays on someone else's schedule and every such failure is invisible
  in the daily pipeline. Note this schedules a real weekly zone purge; cheap here because
  HTML is not edge-cached at all (§16), so only content-hashed `/_astro/` assets are
  evicted.
- **`check_content.py` size skip is no longer silent.** Files over 2 MB dropped out of the
  credential scan with no trace; `pulseData.json` grows by one entry a day and crosses
  that at roughly 344 entries (~day 317), so the file most likely to be written by
  automation would have stopped being scanned, invisibly. Now warns — for text files only,
  since a dozen tracked photographs over the limit would have buried the one case that
  matters. Verified by padding the real file past 2 MB and restoring it.
- **One source added: Huang Kitchen.** Surveyed 25 candidates; the only one needing no
  widening of `EXCLUDE_REGEX`. 116 of 120 archived posts survive the filter, 115 with
  bilingual titles, and the repertoire is CKM's own (紅燒鮑魚海參花膠煲, 客家酿豆腐卜, 糖水).
  Rejections are recorded in `FEEDS` so they are not re-surveyed — in particular
  `christinesrecipes.com` (Chinese edition) is the **same blog** as the configured English
  feed, 20 of 25 items identical with timestamps seconds apart, and would have published
  every dish twice since dedupe keys on `source_link`.
- **Not done, deliberately**: IndexNow still resubmits the whole URL inventory on every
  publish (~75 URLs, ~36% of them `pulse-NN` aliases absent from the sitemap, growing 2/day
  — reaches IndexNow's 10,000-URL request cap in roughly 13 years). Confirmed but medium
  severity and it touches live indexing behaviour, so it is left for a deliberate change
  rather than folded into this pass.
- **Verification**: three harnesses re-run green after every change (insert path, all three
  generation-retry routes with a ladder-advance assertion, and four archive-depth scenarios
  covering lazy/deep/exhausted/all-dead); the 2 MB warning verified by padding the real
  dataset and restoring it byte-identically; `astro check` 0 errors; `astro build` 80
  pages; `check_content.py --strict` 0 errors. All changes are in `scripts/`, `.agents/`,
  `.github/workflows/` and `WORKLOG.md` — none inside `publish.yml`'s path filter, so the
  push triggers no deployment, purge or indexing.

## 2026-08-14 (Live GSC Query Audit, Homepage Title/Description Rewrite & Backlink Strategy Correction)

- **Trustworthy GSC Script**: Added `scripts/gsc_query_report.py`, pulling live Search Analytics data for `sc-domain:ckmkh.com` across totals, country, device, query, page, query×page and date, with a `country = khm` filter applied to the market-specific cuts. It has **no fallback values** and exits non-zero on an API failure. Raw output is written to `scripts/reports/gsc_search_queries.json`. Superseded `scripts/generate_analytics_report.py`, which silently falls back to hardcoded numbers (`35` clicks / `1369` impressions / `2.56%` / `6.43`) that are indistinguishable from live data in the report it writes, and whose "關鍵字亮點" section is hardcoded prose rather than derived from the data it fetched.
- **Measured Search Demand (2026-05-15 → 2026-08-12)**: Site-wide 34 clicks / 1371 impressions / CTR 2.48% / avg position 6.35. Cambodia-only: 29 clicks / 1022 impressions. Findings, all reproducible via the script above:
  - `ម្ហូបការ` — 240 impressions, 11 clicks, position 3.95 (2.66 over the last 28 days). The only term with genuine buying intent; the homepage is its landing page.
  - The `ចុងភៅ` cluster (`ចុងភៅ` 153 + `រូបចុងភៅ` 68 + `រូបភាពចុងភៅ` 11 + `logo ចុងភៅ` 8) — ~240 impressions and **0 clicks**. Image-and-logo intent, not catering intent, and collapsed to 5 impressions in the last 28 days.
  - `ម៉ឺនុយ` — 48 impressions, 0 clicks at position 5.52 against `/blog/01-traditional-8-course-wedding-menu/`, whose title matches the keyword exactly. An exact match that never gets clicked is an intent mismatch, not an optimisation problem.
  - `catering service in phnom penh` — position **1.00**, 31 impressions, **0 clicks**. Consistent with the local pack occupying everything above the fold; not fixable through on-page work.
  - Blog coverage is not the constraint: 15 articles produce ~150 impressions per 90 days combined.
  - Corrected a prior report's claim that `/blog/07-housewarming-catering-setup/` achieved "20% CTR" — filtered to Cambodia that page is 1 impression and 0 clicks. The clicks originated in Taiwan, i.e. the team itself.
- **Domain Consolidation Verified**: `https://www.ckmkh.com/` still shows 362 impressions / 11 clicks over 90 days but only 8 impressions / 0 clicks over the last 28, confirming the 301 to the apex is taking effect. Verified live that `www.ckmkh.com/`, `/en/` and `/en/tanghuot/` all return 301. No action required.
- **Homepage Title & Description Rewrite** (`src/pages/index.astro`): Reordered the title from brand-first to keyword-first — `សេវាកម្មម្ហូបការ ភ្នំពេញ | មុខម្ហូបការមង្គលការ | ចេង គួងម៉េង (CKM)` (66 chars, down from 74) — so SERP truncation costs the brand rather than the keyword. Removed `ចុងភៅ` from the title on the zero-click evidence above. Rewrote the description from 195 to 150 characters: `Layout.astro` slices at 152 and appends `...`, so the live SERP snippet on the site's highest-impression page was cut mid-word at `…កូនជ្រូកខ្វៃ ស៊ុ...`. Added an inline comment recording the data behind the ordering so it is not "optimised" back. Verified all 15 blog descriptions are already under the limit.
- **Backlink Strategy Correction**: Reviewed `.agents/skills/ckm_backlink_writer/SKILL.md` and `Docs/backlink_ledger.md`. All three ledger entries are 待發佈 with no live URL, so no effort is sunk. Recorded in `.agents/AGENTS.md` §19 that links are not this site's constraint (money keyword already at position 2.66; total commercial demand caps the channel near 50 clicks/quarter), that the nofollow status of Medium and Substack could **not** be verified from source (both blocked a scripted fetch), and that ledger entry 002 targets `ចុងភៅនៅភ្នំពេញ` — recorded here on 2026-08-13 as a "high-impression query" but measured at **1 impression in 90 days**. Redirected priority to Google Business Profile, Facebook (site referral currently **0**) and Telegram.
- **Agent Rules**: Added `.agents/AGENTS.md` §18 (Search demand — measured, not assumed) and §19 (External backlinks); renumbered Communication to §20.
- **Secrets Rule Rewrite (`.agents/AGENTS.md` §16)**: The Storage section stated "One secret, one home" and then, in the next bullet, "Local: `.env`. CI: GitHub Actions secrets" — two homes. Replaced the contradiction with a single precise rule (*a credential lives only where it is genuinely needed, with only the power it needs there*) and its two ordered consequences: delete unnecessary copies first, then reduce the privilege of the copies that cannot be deleted. Recorded that splitting a credential is worthless unless the second one is strictly weaker, and that "not currently in use" and "not needed" carry identical risk — a credential used a few times a year should be created on demand with an expiry, not parked in `.env`.
- **Credential Audit**: Scanned every environment variable actually read by code (`os.getenv`, `import.meta.env`, `secrets.*`). Findings: `GSC_API_KEY` is read by **nothing** — GSC authenticates by service account, not API key, so it was never able to do the job; verified by running `gsc_query_report.py` with the variable blanked, which succeeded. `GITHUB_PAT` is already absent from `.env`. `.env` and `google_service_account.json` are gitignored and have never appeared in git history across all refs. The repository is **public**; no workflow uses `pull_request` or `pull_request_target`, so fork PRs cannot reach secrets.
- **[REGRESSION] Over-Privileged Cloudflare Token**: `CLOUDFLARE_API_TOKEN` was verified as a scoped API token (not a Global API Key) via `/user/tokens/verify`, but `scripts/apply_cf_settings.py` uses it for `PUT /rulesets/phases/{http_request_firewall_custom,http_ratelimit,http_request_cache_settings}/entrypoint` — the power to rewrite the zone's entire WAF, rate-limit and cache rulesets. CI uses the same token for cache purge alone. Recommended splitting into a purge-only token for CI, with Cloudflare configuration changes made through the dashboard.
- **[REGRESSION] `apply_cf_settings.py` Replaces Rather Than Adds**: Each `put_ruleset_phase()` is a `PUT` on the phase entrypoint and each phase in the file holds exactly one rule, so running the script silently deletes every rule added through the dashboard since the file was last edited. Documented in §16; the file should be treated as a record of intent, not a tool.
- **Root Cause of `cf-cache-status: DYNAMIC` on HTML**: The `_headers` comment claims `s-maxage=86400, stale-while-revalidate` resolved the all-requests-hit-origin problem. It did not — measured live as `DYNAMIC` on 2026-08-14. The Cloudflare Cache Rule in `apply_cf_settings.py` marks only `/_astro/`, `/assets/` and `/fonts/` as cacheable, and Cloudflare does not cache HTML by default, so the header is inert. Not changed: adding HTML to the cache rule would require a working purge on every deploy, and `notify_indexing.py` (which performs the purge) runs only in the pulse workflow, not on an ordinary push.
- **Service Account Split & Key Rotation (completed and verified)**: The project had **one** service account, `gsc-and-ga4@…`, holding **three** keys — all with no expiry, two of them (Jul 22) of unknown purpose — shared between CI and the local machine at Search Console `Full` permission. Replaced with two accounts, neither granted any GCP IAM role (Search Console access is granted in Search Console, not via IAM):
  - `ckm-indexing@…` — Search Console **Full**, key held only in the GitHub Actions secret `GSC_SERVICE_ACCOUNT_JSON`, used by `notify_indexing.py` to `PUT` the sitemap.
  - `ckm-analytics@…` — Search Console **Restricted**, key held only in the local `google_service_account.json`, used by `gsc_query_report.py`. Confirmed that `Restricted` can read Search Analytics; a leaked local key can now read data but submit nothing.
  - Old account deleted, taking all three keys with it; its orphaned Search Console user entry removed. Verified after deletion: `Verify GSC Credential` run #3 green, and the local report returned identical figures (13 clicks / 359 impressions / 28 days).
  - Rotation order held throughout — create new, update consumer, verify, only then revoke. The first secret update silently kept the old credential (the verification log printed `gsc-and-ga4@`), which is exactly the failure the verify-before-revoke rule exists to catch.
- **Full Credential Rebuild (completed and verified)**: Every credential in the project was replaced with a least-privilege equivalent, one at a time, each verified before the predecessor was revoked. Final state — local `.env` holds no secret at all, only `GSC_GA4_SERVICE_ACCOUNT_EMAIL`, which is an email address:

  | Credential | Before | After |
  | :--- | :--- | :--- |
  | Search Console (CI) | `gsc-and-ga4@`, Full, 3 never-expiring keys, shared with local | `ckm-indexing@`, Full, one key, GitHub Actions secret only |
  | Search Console (local) | same account and key as CI | `ckm-analytics@`, **Restricted**, one key, local only |
  | Cloudflare | `CKM CF All Permission Token` — Config Rules + Cache Rules, also in local `.env` | `ckm-ci-purge-cache` — **Cache Purge only**, one zone, GitHub Actions secret only |
  | Cloudflare (orphan) | `ckm build token` — Account Containers + **Secrets Store**, all zones, unused since Feb 9 | deleted |
  | Gemini | key in both CI and local `.env` | `ckm-pulse-ci`, GitHub Actions secret only |
  | `GSC_API_KEY` | in local `.env`, read by nothing | deleted |

- **[REGRESSION] The Old Cloudflare Token Could Not Purge**: Its permissions were `Zone.Config Rules` and `Zone.Cache Rules` — *not* `Zone.Cache Purge`, which is a separate permission. Since `purge_cloudflare_cache()` catches every exception and only prints a warning, the daily purge had been failing silently behind a green workflow. No practical damage, because HTML is not edge-cached anyway (`cf-cache-status: DYNAMIC`, see above), but the replacement token is the first one that can actually perform the purge. This also proved the rotation had taken effect: the old token could not have produced the successful purge in the verification run.
- **[REGRESSION] Gemini Key Travelled in the Query String**: `call_gemini_api_robust` built `…:generateContent?key={env_key}` and then stringified any exception (`msg = str(e)`); several urllib errors carry the request URL, so a transport failure could have printed the API key into the CI log. Moved to the `x-goog-api-key` header, which authenticates identically and keeps the key out of URLs and proxy logs.
- **Cloudflare Global API Key**: Identified but not used by this project — verified, since the token in use passes `/user/tokens/verify`, which a Global API Key fails. It cannot be scoped, cannot be given an expiry, cannot be deleted (only rolled), and a leak means DNS control of the domain. Recorded in `Docs/security-baseline.md` as never to be used.
- **GA4 Programmatic Access & Pre-Facebook Baseline**: Granted `ckm-analytics@` the **Viewer** role on GA4 property `534450350` — the minimum level, matching its `Restricted` grant in Search Console. Enabling the Data API alone returned 403: the API grants the endpoint, the property grant supplies the data. Captured the baseline for the 90 days to 2026-08-14, which is the reference point for any future distribution work: 150 sessions / 102 users / 1,322 page views; channels Direct 87, Organic Search 61, Referral 2, **Social 0**; countries Taiwan 50 (the team), Cambodia 47, United States 35 (crawlers). Two readings that matter — Direct is 58% and unattributable because Telegram strips the referrer, which is why posted links need UTM tags from the first post rather than retroactively; and 8.8 page views per session is not enquiry behaviour, so after the team's own visits and crawlers the real prospect count is single digits. Recorded in AGENTS.md §18. Declined to build a `ga4_report.py` for now — the one-off query answered the question.
- **Backlink Programme Dropped**: Deleted `.agents/skills/ckm_backlink_writer/` and `Docs/backlink_ledger.md`. All three ledger entries were 待發佈 with no live URL, so nothing was sunk. AGENTS.md §19 now records the decision and its four independent reasons — the money keyword already ranks 2.66 so there is no gap for a link to close; roughly 300 commercial impressions per 90 days caps the channel regardless of placement; Medium and Substack are understood to nofollow outbound links and `*.blogspot.com` carries near-zero authority (unverified, since both platforms blocked a scripted fetch, which is itself a reason not to depend on it); and neither platform has Cambodian readership, so Khmer content there has no distribution value either. Also records when the tactic *would* be right — an English-language B2B or developer audience that actually reads those platforms — so a future project applies the reasoning rather than resurrecting the skill.
- **`ckm_blog_writer` Scoped to Quality, Not Volume**: Added a section 0 stating that the skill governs *how* to write, not *whether* to. Coverage is not this site's constraint — 15 articles produce ~150 impressions per 90 days and most take 0 clicks, so a sixteenth is worth about 10 impressions a quarter. "Filling a keyword gap" is explicitly not a valid reason to write; verify a topic against `gsc_query_report.py --days 90` filtered to `country = khm` first.
- **All Skills Retired, Rules Consolidated**: Deleted `.agents/skills/` entirely; `.agents/` now contains only `AGENTS.md`. `local_seo_analyzer` and `audience_analyzer` were generic audit checklists that would generate plausible-sounding findings untethered from the measured data in §18 — the same failure mode as the fabricated audit scripts deleted earlier today, and worse, because a skill is instructions an agent executes rather than a file it might read. `ckm_pulse_writer` restated the prompt and category taxonomy that actually live in `fetch_catering_pulse.py` (categories at lines 35–48, prompt near 363), so it was two descriptions of one thing with nothing to catch a drift. `ckm_blog_writer` duplicated roughly 90% of §10–§14 and §17. Everything genuinely unique was merged into AGENTS.md first: the full English-to-Khmer substitution table into §10; article structure into a new subsection of §14 — 1,200-character minimum, the `## ចម្លើយរហ័ស` quick-answer block, one H1, a comparison table and a checklist per post, plus two audit-derived regressions (articles 02/03/04/10/11/12 placed the conclusion before the FAQ; articles 13/14/15 shipped with zero internal links). §0 now records that the project has no skills and that they must not be recreated.
- **[REGRESSION] A Green Pulse Run Does Not Verify GSC Credentials**: The indexing step in `daily_catering_pulse.yml` is gated on `steps.wait.outputs.live == 'true'`, itself downstream of the pulse having changed, so on a day the RSS feed yields nothing the credential is never exercised and the workflow still reports success. After a rotation the first real test would otherwise be the unattended 20:47 UTC schedule. Added `.github/workflows/verify_gsc_credential.yml` (manual only) which refreshes the token, lists the account's properties, and submits the sitemap — the last step being what distinguishes `Full` from `Restricted`, since `Restricted` returns 403 there. It prints only `client_email` and `private_key_id`, both identifiers visible in the Cloud console, and never reads the private key.
- **Portable Security Baseline**: Wrote `Docs/security-baseline.md`, a project-agnostic version of this audit for the user's other repositories — grade credentials by damage rather than usage, audit IAM roles and not only which APIs are enabled, verify what a token can actually do rather than that it is merely scoped, rotate as create → update → test → revoke, keep one-off credentials out of `.env` entirely, and check for configuration living outside the repository before concluding from `grep` that something is absent.
- **Google Cloud API Surface**: The repository calls exactly two Google endpoints — Search Console (`webmasters/v3`) and Gemini (`generativelanguage`, an AI Studio key from a different project). **No code calls the GA4 Data or Admin API.** Recorded in §16 which enabled APIs to keep (Search Console; Service Usage and Service Management, which govern enabling other APIs) and which to disable (BigQuery ×7, Cloud SQL, Cloud Storage ×3, Analytics Hub, Dataplex, Dataform, Datastore — all at zero requests, and the billable ones representing real exposure if a key leaks).
- **Validation**: `python scripts/check_content.py --strict` → 0 errors, 6 pre-existing content warnings unrelated to this change. `npx astro build` → 73 pages, 0 errors; verified the rendered `<title>`, `<meta name="description">` and `og:title` in `dist/index.html`.

## 2026-08-14 (Complete 15-Article Blog Editorial Image Generation & 16:9 Media Migration)

- **Full 15-Article AI Image Generation & 16:9 Aspect Ratio Migration**: Generated 1600×900 (16:9) photorealistic editorial food photography for all 15 blog articles using dedicated prompt specifications and unified quiet-luxury style parameters:
  - Processed all 15 inline WebP images (`public/images/blog_01_inline_khmer.webp` ~ `blog_15_inline_khmer.webp`) with quality 82 (optimized between 96 KB and 248 KB).
  - Processed all 15 cover PNG images (`src/assets/grounded_images/ckm_blog_01.png` ~ `ckm_blog_15.png`).
  - Resolved the 16:9 visual clipping defect where previous 1024×1024 square images lost ~28% top/bottom canvas under `aspect-[16/9] object-cover`.
- **Blog Content & Frontmatter Integration**:
  - Inserted 16:9 inline image tags with verified descriptive Khmer `alt` attributes into `13-master-chef-catering-secrets.md`, `14-phnom-penh-master-chef-team.md`, and `15-luxury-abalone-banquet-soup.md`.
  - Normalized all 15 blog article frontmatter `coverImage` paths to point to `ckm_blog_NN.png`.
- **Image Generation Prompt Reference Vault**: Created `Docs/image-prompts.md` documenting the unified style block, negative filters, and all 15 ready-to-use prompts for future visual consistency.
- **Static Validation & Build Verification**: Verified 100% compliance with `scripts/check_content.py --strict` (0 errors) and executed `npm run build` compiling 73 static pages, AVIF assets, and OpenGraph variants cleanly with 0 errors.

## 2026-08-13 (GitHub Actions CI/CD Pipeline Debugging & Pulse SEO Automation)

- **GitHub Actions Workflow Refinement & Permissions Fix**: Debugged and resolved CI/CD pipeline issues in `.github/workflows/daily_catering_pulse.yml`. Added `permissions: { contents: write }` to the workflow configuration to authorize the `GITHUB_TOKEN` to push committed JSON updates and image files back to the repository, resolving the Git push 403 Forbidden error. Updated steps to install `requests` and `google-auth` Python libraries in the runner.
- **Service Account Credentials Integration**: Modified the indexing step to dynamically create `google_service_account.json` from the repository secret `GSC_SERVICE_ACCOUNT_JSON` at runtime.
- **IndexNow Key Rotation**: Updated `INDEXNOW_KEY` to `e521f0df7f9c42348c416f1b878d9114` in `scripts/notify_indexing.py` and replaced `public/c9b7e416a2d9426fa7406a09289196b0.txt` with the new key file `public/e521f0df7f9c42348c416f1b878d9114.txt` to match the user's Bing Webmaster Tools active IndexNow key.
- **Cloudflare Cache Purge Robustness**: Replaced the shell-based `curl` cache purge command in the GitHub Actions workflow with programmatic execution inside `scripts/notify_indexing.py` using Python's native `urllib.request`. Added defensive quote-stripping to handle cases where the user accidentally wrapped their API token in quotes within GitHub Secrets, resolving the Cloudflare API Error 1012.
- **Pulse Image SEO Automation**: Updated the Gemini AI generation prompt in `scripts/fetch_catering_pulse.py` to produce highly descriptive Khmer `image_alt` tags. Renamed cover image files to use keyword-rich article slugs instead of legacy `pulse-XX` IDs (e.g., `omurice-japanese-omelette-rice-video-pulse-01.webp` instead of `pulse-01.webp`) in both disk asset names and JSON references.
- **Assets and Database Migration**: Created and executed `scripts/migrate_pulse_images.py` to rename existing local `.webp` files to their slug-based SEO names, append default `image_alt` to all 19 entries in `src/data/pulseData.json`, and re-crawl the 4 previously timed-out articles (`pulse-16` to `pulse-19`) to download their correct unique images, resolving all duplicate image issues.
- **Astro Template Integration**: Updated `CateringPulse.astro`, `[page].astro`, `[id].astro`, and `index.astro` to render the descriptive standard `image_alt` attribute for all pulse images to maximize search engine discoverability.
- **IndexNow WAF Audit & Diagnosis**: Investigated IndexNow HTTP 403 Forbidden (`UserForbiddedToAccessSite`) error. Verified key file availability and WAF Custom Rules (which already bypass `.txt` files from managed rules, rate-limits, and Super Bot Fight Mode). Identified that Cloudflare Free Plan "Bot Fight Mode" (BFM) is challenging IndexNow's verification requests globally and recommended disabling BFM in Cloudflare dashboard as a resolution.
- **Local Env & Dispatch Automation**: Added `GITHUB_PAT` locally to the `.env` file (ignored by Git) and successfully dispatched the GitHub actions REST API to trigger the workflow.
- **Markdown Standards Compliance**: Resolved markdownlint warnings in `Docs/Architecture/Worklogs/2026-08-09_catering_pulse_autopilot_spec.md` (MD022 heading-blank-line rules) and `WORKLOG.md` (MD012 double blank lines rule) to ensure zero lint warnings across files.
- **Medium Backlink Skill Creation**: Created the `ckm_backlink_writer` skill file at `.agents/skills/ckm_backlink_writer/SKILL.md` to define standard Medium parameters (Khmer title, 100-140 character description under Medium's 150-character limit, keyword-rich anchor texts, image alt text, and English-only topics) for automated backlink generation.
- **Medium Backlink Description Refinement**: Shortened today's generated Medium description to exactly 130 characters and updated the skill file's limit guidelines to prevent future character overflow.
- **Medium Backlink Skill Canonical URL Update**: Added Canonical URL guidelines to `.agents/skills/ckm_backlink_writer/SKILL.md` to ensure future external outreach posts point directly to `https://ckmkh.com` to pass Link Juice without domain validation mismatch.
- **Substack Specifications & Backlinks Ledger Integration**: Integrated Substack publication rules into `.agents/skills/ckm_backlink_writer/SKILL.md` (Title, Subtitle/SEO description, Canonical URL setup). Created `Docs/backlink_ledger.md` to track external publications (Medium, Substack) and prevent duplicate content. Generated today's Substack outreach post targeting GSC/Bing high-impression query 'ចុងភៅនៅភ្នំពេញ' (Chef in Phnom Penh).
- **Blogger Specifications & Backlinks Ledger Update**: Added Blogger publication guidelines (Search Description, Custom English Permalinks, Labels) to `.agents/skills/ckm_backlink_writer/SKILL.md`. Updated `Docs/backlink_ledger.md` to record the new Blogger article targeting GSC keywords 'ម៉ឺនុយម្ហូបការ' (Wedding Menu) and 'ប៉ាវហឺ' (Abalone) to boost specific page authority.
- **Backlink Skill Formatting & Automation Guidelines**: Updated `.agents/skills/ckm_backlink_writer/SKILL.md` to include: (a) Dual-format output requirement (HTML code + Markdown) to prevent styling residue on copy-paste, and (b) Image generation automation rules requiring prompt details, Khmer Alt text, and PowerShell script file copy directly to the user's Downloads folder.
- **Blogger Workflow Decision**: Abandoned Blogger theme XML customization due to the legacy platform's constraints to focus time on high-value tasks. Blogger remains an active publishing target for backlinks. Restored Blogger specifications in `.agents/skills/ckm_backlink_writer/SKILL.md` and retained the Blogger article (entry 003) in the backlinks ledger `Docs/backlink_ledger.md`.
- **Markdown Standards Compliance**: Resolved markdownlint warnings in `.agents/skills/ckm_backlink_writer/SKILL.md` (MD022 heading-blank-line rules) and `medium_backlink_article.md` (MD009 trailing spaces rule) to maintain zero lint warnings.

## 2026-08-11 (Pulse Anti-Fool Audit, Over-Strict Title Guard Fix & Flash-Lite 500 RPD Model Configuration)

- **Pulse Anti-Fool & Deduplication Audit**: Thoroughly audited `scripts/fetch_catering_pulse.py` and `src/data/pulseData.json`. Confirmed that deduplication mechanisms (`source_link` checking against `existing_links`, intra-batch `seen_links`, and content keyword filters) are functioning cleanly with 0 duplicate articles.
- **Root Cause Resolution for Idle GitHub Workflow Runs**: Identified why scheduled GitHub Actions completed without committing new articles. Discovered an over-strict title guard condition (`"សិល្បៈនៃការចម្អិន" not in parsed.get("title_km", "")`) in `call_gemini_api_robust` that rejected Gemini's valid Khmer culinary titles. Refined the anti-fool check to enforce length and JSON schema validity while adding prompt guidance for title diversity.
- **500 RPD Model Queue Optimization**: Analyzed user's Google AI Studio Free Tier quota limits. Discovered standard Flash models (3.6 Flash, 2.5 Flash) have a strict 20 RPD (Requests Per Day) limit, while `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite` provide 500 RPD and 15 RPM. Updated `scripts/fetch_catering_pulse.py` model queue to `["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]` to guarantee 0 rate limit failures.
- **Dataset Accumulation & SSG Build Verification**: Successfully fetched and processed new Khmer gourmet articles (`pulse-15` through `pulse-19`), generating optimized WebP cover images (`public/images/pulse/pulse-15.webp`~`19.webp`). Verified Astro SSG build (`npm run build`), compiling 57 static pages and sitemaps cleanly with 0 errors.

## 2026-08-10 (GitHub Actions Pipeline Optimization, Gemini 3.6 Flash Upgrade & Descending Date Sorting)

- **GitHub Actions Schedule Optimization**: Shifted daily workflow cron in `.github/workflows/daily_catering_pulse.yml` from `23 1 * * *` (01:23 UTC / 08:23 AM ICT) to `47 20 * * *` (20:47 UTC / 03:47 AM ICT / 04:47 AM Taipei Time). Selected a global off-peak window and non-standard minute `:47` to avoid GitHub Actions infrastructure queue delays and guarantee early-morning automated publication before Cambodian readers wake up.
- **Gemini API Model Upgrade & Free Quota Troubleshooting**: Diagnosed why scheduled runs failed to commit new articles. Discovered that user API key had 0/0 quota for `gemini-2.0-flash` (HTTP 429) while `gemini-1.5-flash` returned HTTP 404. Updated `scripts/fetch_catering_pulse.py` model fallback list to verified active endpoints: `gemini-3.6-flash`, `gemini-3-flash-preview`, `gemini-3.5-flash`, `gemini-flash-latest`, and `gemini-flash-lite-latest` (10 RPM / 250K RPD free quota).
- **Multi-Page Pagination & Infinite Pulse Accumulation**: Removed the `[:11]` truncation limit in `scripts/fetch_catering_pulse.py`, allowing Pulse articles to accumulate naturally beyond 12 items. Astro static site generator now builds multi-page pagination (`/pulse/`, `/pulse/2/`, `/pulse/3/`) automatically as new articles are published daily.
- **Strict Descending Date Sorting (Newest First)**: Implemented `parsedate_to_datetime` descending date sorting in `fetch_catering_pulse.py` and `src/data/pulseData.json`. Resolved inverted ordering so newest articles (e.g. `09.Aug.2026`) are always placed at `#1` (`pulse-01`) on Page 1 and the Homepage (`src/components/CateringPulse.astro`), while older articles (`25.Jul.2026`, `24.Jul.2026`) shift naturally to Page 2 (`/pulse/2/`).
- **End-to-End Pipeline Simulation & Live Verification**: Simulated the full 5-step pipeline for 13th and 14th articles. Verified Astro static build (53 pages compiled with 0 errors), IndexNow/GSC submission (`notify_indexing.py` scanning 34 URLs), and live Cloudflare Pages deployment. Used `browser_subagent` and Playwright to visually confirm that `https://ckmkh.com/pulse/` renders newest articles on Page 1 with page navigation (`ទំព័រ 1 នៃ 2`), and `https://ckmkh.com/pulse/2/` renders older articles cleanly.

## 2026-08-09 (East Asian RSS Dataset, WebP Optimization & GitHub Actions Pipeline Fix)

- Configured a 100% geopolitically safe and authentic East Asian RSS dataset in `pulseData.json` (13 articles) containing Khmer, Chinese/Teochew, and Japanese culinary stories.
- Programmatically downloaded and cropped all cover images to 16:9 aspect ratio, compressing them to WebP under 45KB to eliminate CLS and accelerate mobile page loads.
- Integrated a 10-second API cooldown pacing sleep and robust 429 rate limit backoff retry chain for `gemini-2.0-flash`, `gemini-2.0-flash-lite`, and `gemini-1.5-flash`.
- Added the Anti-Fool Guard validation in the parser to preserve local data integrity during API outages.
- Upgraded the Node.js version in `.github/workflows/daily_catering_pulse.yml` from `20` to `22` to satisfy Astro 6 build requirements, resolving the instant CI build abort error.
- Successfully ran the end-to-end GitHub Actions workflow on GitHub, verifying 100% successful RSS mining, build bundling, GSC/IndexNow indexing, and auto-deployment.
- Reverted the temporary `push` trigger in `daily_catering_pulse.yml` to restore clean scheduled/manual-only triggers.

## 2026-08-08 (Pulse Homepage 3-Item Limit & 12-Item Listing Pagination)

- Added automated SEO Slugs generator (`generate_seo_slug`) to `scripts/fetch_catering_pulse.py`, transforming Pulse titles into clean, keyword-rich URLs (e.g. `/pulse/international-mobile-catering-hospitality-standards-pulse-02/`).
- Updated `src/pages/pulse/[id].astro` to generate dual static paths for both `item.slug` and `item.id` for 100% backward compatibility.
- Implemented complete Defensive Fail-Safe Guards (防呆機制) across Pulse subsystem: empty array/null safety in `getStaticPaths()`, client-side `onerror` image fallbacks, orphan image auto-pruning, and duplicate RSS entry prevention.
- Implemented hybrid relevance + rotated round-robin link juice algorithm in `src/pages/pulse/[id].astro` so Link Juice is passed evenly across all 15 blog articles.
- Updated `src/components/CateringPulse.astro` homepage section to display top 3 pulse items (`items.slice(0, 3)`) as requested.
- Downloaded all 11 external Pulse cover images to local assets directory (`public/images/pulse/pulse-01.jpg` ~ `pulse-11.webp`) and updated `src/data/pulseData.json` `image_url` references to eliminate external hotlinking dependencies and speed up page loading.
- Integrated automatic image downloading and ID-remapping into daily RSS pipeline (`scripts/fetch_catering_pulse.py`), so newly generated articles automatically download their cover images to `public/images/pulse/` and sync relative paths (`/images/pulse/pulse-XX.jpg`).
- Updated GitHub Actions workflow `.github/workflows/daily_catering_pulse.yml` to automatically stage and commit `public/images/pulse/*`.
- Updated `.agents/skills/ckm_pulse_writer/SKILL.md` output spec to enforce local image path formatting.
- Verified and updated `src/pages/pulse/index.astro` and `src/pages/pulse/[page].astro` list pages to handle 12 items per page (`pageSize: 12`) with automatic fallback navigation (`totalPages > 1` & `page.lastPage > 1`).
- Added Schema.org `BreadcrumbList` JSON-LD structured data to `src/pages/pulse/[page].astro` for search engine indexing.
- Ensured smooth static path generation and page 2 -> `/pulse/` previous link routing so automated pulse generator workflows operate without routing errors.
- Verified build using `npx astro build` (35 pages compiled with 0 errors).

## 2026-08-08 (Pulse RSS Image Optimization & VIP FAQ Audit)

- Audited and updated Catering Pulse (`src/data/pulseData.json`) to use original cover images scraped from WedLuxe and CFE News RSS feeds.
- Implemented ambient frosted glass background overlay (`blur-xl opacity-50 scale-125`) across `CateringPulse.astro`, `/pulse/index.astro`, `/pulse/[page].astro`, and `/pulse/[id].astro` to eliminate awkward aspect-ratio cropping while preserving full portrait/landscape photos cleanly.
- Added original source attribution card with external links (`target="_blank" rel="noopener noreferrer"`) in `pulse/[id].astro` to respect original RSS authors and boost Google SEO E-E-A-T entity trust.
- Audited all 13 blog posts (`src/content/blog/*.md`) to enforce zero tipping, zero leftover packing, and zero cheap bargaining topics, replacing pedestrian FAQ items in `08-waitstaff-service-flow.md` and `04-hygiene-and-temperature-control.md` with VIP elder care, food freshness, and serving timing questions.
- Audited Google Search Console & GA4 live performance data. Identified top high-demand search queries: `ចុងភៅ` (Chef / Master Chef team in Phnom Penh - 165 impressions) and `ប៉ាវហឺ` (Abalone banquet soup - 15 impressions).
- Generated Article 14 (`14-phnom-penh-master-chef-team.md`) and Article 15 (`15-luxury-abalone-banquet-soup.md`) in 100% Traditional Khmer (`km-KH`) with grounded Cambodian imagery, zero hype words, zero hard technical numbers, and 100% VIP hospitality FAQs.
- Verified build with `npm run build` (35 static pages compiled cleanly with 0 errors).

## 2026-07-28 (Cloudflare & SEO Baseline)

- Audited live Cloudflare Zone settings for `ckmkh.com` via Cloudflare REST API.
- Updated `scripts/apply_cf_settings.py` to enable auto-minify, set security level to `medium`, and expand the WAF SEO Bypass rule to include `/robots.txt`, `sitemap*.xml`, `/llms.txt`, and `/llms-full.txt`.
- Created `public/_headers` to deploy Cache-Control rules (`max-age=0` for HTML, 1-year immutable for `/_astro/*` and `/fonts/*`) and security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) to Cloudflare Pages.
- Executed `apply_cf_settings.py` and `cloudflare_audit.js` to verify API configuration.
- Successfully built project with `npm run build` and verified `dist/_headers` deployment.
- Checked project dependencies to verify the tech stack. Confirmed the project uses **Astro** and **Tailwind CSS**. Noticed that it uses **FontAwesome** instead of **Lucide** for icons.
- Initialized `WORKLOG.md` and `.agents/AGENTS.md` to start logging work and maintaining project-specific agent rules.
- Started the development server (`npm run dev`).
- Analyzed the website content (`src/data/homeData.ts` and `src/pages/index.astro`). Recorded the business context (a 60-year experienced professional catering/banquet service in Phnom Penh targeting weddings and large events, known for Khmer-Chinese fusion cuisine) into an artifact for future accuracy.
- Generated a comprehensive list of Khmer SEO, LSI, and NLP keywords based on the business context for content optimization.
- Conducted web research on the Cambodian catering market to enrich the keyword list with colloquial terms.
- Planned out 12 professional, SEO-optimized article outlines using the gathered Khmer keywords. The plan was further expanded with objective expert viewpoints, LSI/NLP keywords, non-text AI image prompts (set in Phnom Penh), and paragraph-by-paragraph summaries. The detailed plan is saved as an artifact for user review.
- Added a new rule to `AGENTS.md` specifying that only Khmer content should be modified, and Chinese/English content should be ignored.
- Researched the latest Generative Engine Optimization (GEO) best practices. Found that total word count is less important than "chunking" (40-80 word quick answers, 120-180 word sections) and factual density. Updated the SEO plan artifact with specific GEO formatting rules (use of tables, bullet points, quantitative claims, and clear H2/H3 hierarchies).
- Expanded the SEO content plan for all 12 articles to guarantee a minimum of 1200 words per article. Integrated the GEO "chunking" strategy by adding detailed H2/H3 subsections, markdown tables, expert checklists, and FAQ sections to ensure high factual density without fluff.
- Generated the first SEO article ("Traditional 8-course Khmer wedding menu") entirely in Khmer, achieving the 1200+ word depth target. Added two generated images (one cover, one inline) and saved it to `src/content/blog/01-traditional-8-course-wedding-menu.md`.

## 2026-07-04 (Content & Architecture)

- Created Article 6 (`06-signature-dishes.md`). Deleted old placeholder. Generated 2 images of Sino-Khmer cuisine with Cambodian chefs. Strictly Khmer text.
- Created Article 7 (`07-housewarming-catering-setup.md`). Deleted old placeholder. Generated 2 images for housewarming setup. Strictly Khmer text.
- Removed all English translations in parentheses from articles 01 to 07. Fixed typography typos. Created Article 8 (`08-waitstaff-service-flow.md`). Generated 2 images of Cambodian waitstaff. Strictly pure Khmer text without any English in parentheses.
- Created Article 9 (`09-outdoor-tent-infrastructure.md`). Deleted old placeholder. Generated 2 images of outdoor tent setup. Strictly pure Khmer text without any English in parentheses.
- Restored mojibake (encoding corruption) on articles 01 to 07 caused by PowerShell ANSI default read. Deleted lingering obsolete placeholder files 01, 02, 03. Created Article 10 (`10-60-years-chef-experience.md`). Generated 2 images of Cambodian master chefs.
- Created Article 11 (`11-choosing-packages.md`). Generated 2 images of wedding package consultation and VIP banquet setups. Maintained strict pure Khmer formatting.
- Created Article 12 (`12-catering-industry-trends.md`) completing the 12-article SEO series. Generated 2 images depicting futuristic and high-tech Cambodian catering setups.
- Conducted AI SEO Audit. Fixed Canonical Domain (`https://ckmkh.com` instead of www) across `robots.txt`, `MooncakePage.astro`, and `[slug].astro`.
- Purged legacy en/zh subdirectories and layouts to simplify the architecture to pure Khmer-only.
- Replaced all hardcoded SVGs with `@lucide/astro` components in `MooncakePage.astro` for icon unification.
- Injected Astro ViewTransitions for SPA-like navigation and implemented a vanilla JS `IntersectionObserver` (`.reveal`) for Quiet Luxury scroll-reveal micro-animations.
- Received Cloudflare API token from the user. To comply with strict security protocols, the token was NOT documented in git-tracked files. Instead, it was securely written to `.env` and a new token protection rule was added to `AGENTS.md`.
- Validated SEO strategy for the Tang Huot Bakery sub-brand (`/tanghuot/`). Decided to remain strictly Khmer-focused based on user instruction.

## 2026-07-22 (Local SEO & Playwright Audit)

- Saved GSC & GA4 integration service account email securely in `.env` per Security Rule.
- Added Local SEO & GEO Audit Protocol and Target Audience & Demographic Persona Protocol rules to `.agents/AGENTS.md`.
- Created custom skill `.agents/skills/local_seo_analyzer/SKILL.md` for evaluating local SEO, LocalBusiness JSON-LD schema, local Khmer keywords, and GEO targeting.
- Created custom skill `.agents/skills/audience_analyzer/SKILL.md` for analyzing local B2B/B2C customer personas, user search intent, and mobile conversion friction.
- Created Playwright automated E2E audit script `scripts/playwright_audit.js` testing 16 canonical routes across Desktop (1440x900), Tablet (768x1024), and Mobile (375x812). Achieved 100% pass rate across 96 SEO checks, 32 UX checks, and 64 UI/CSS checks with 0 JS console errors and 0 horizontal overflows.
- Implemented Cambodian Local Intent FAQ section on `src/pages/index.astro` targeting Phnom Penh banquet pricing, tent rentals, and event scope, backed by Schema.org `FAQPage` JSON-LD for Google Rich Snippets.
- Injected Schema.org `BreadcrumbList` JSON-LD across all canonical pages (`/`, `/blog/`, `/privacy/`, `/tanghuot/`) for 100% structured data coverage.
- Added smooth "Scroll to Top" floating button with Khmer ARIA label and `requestAnimationFrame` passive scroll listener in `src/layouts/Layout.astro`.
- Resolved mobile burger menu ID mismatch (`mobile-menu-toggle`), added `md:hidden` to desktop button, and re-bound JS on Astro `astro:page-load` SPA events.
- Fixed desktop navbar link contrast (`text-onyx font-bold`) and updated mobile menu overlay to a seamless Pearl White backdrop (`bg-white z-[90]`) with dark luxury Khmer typography, resolving color bleed-through issues.
- Performed Google Lighthouse performance optimizations: preloaded `hanuman-latin-700-normal.woff2` font, reduced hero image payload from 26 KiB to 7 KiB, and resized brand logo to 96x96px.
- Formalized "Royal Champagne & Onyx" Quiet Luxury brand palette rule in `.agents/AGENTS.md`.
- Created Cloudflare Live API audit suite `scripts/cloudflare_audit.js`. Conducted deep live audit of Cloudflare WAF, Cache, and Speed configurations (`ckmkh.com` Zone ID: `d459c80...`). Confirmed 1-year edge asset caching (`CKM Astro Cache Rules`), Brotli, HTTP/3, Early Hints, 0-RTT, and WAF SEO Bypass protocol (`robots.txt` & `sitemap.xml`) are active.
- All changes tested via `npx astro check` (0 errors), `npm run build` (17 static pages compiled), and pushed to GitHub `origin/main`.

## 2026-07-28 (GSC 404 Audit & AEO Tuning)

- Completed GSC 404 health audit and mitigation strategy for removed `/zh/` and `/en/` sub-paths. Added Cloudflare Pages `public/_redirects` and Astro `redirects` matrix mapping all `/zh/*` and `/en/*` legacy paths via HTTP 301 to `https://ckmkh.com/`. Updated `src/data/homeData.ts` siteDomain to non-www canonical URL. Updated `src/pages/404.astro` homeUrl fallback. Updated `scripts/gsc_ga4_audit.js` diagnostic tool. Passed `npx astro check` (0 errors) and `npm run build` (17 static pages compiled).
- Added `Communication & Interaction Protocol` to `.agents/AGENTS.md` enforcing a Professional, Rigorous, Objective, and Sincere tone for all future Agent interactions and system reports.
- Saved `GSC_API_KEY` securely into local `.env` file per Security Rule (git-ignored), authorizing automated Search Console API integration without exposing secrets to git history.
- Executed `/goal`: Conducted GSC potential opportunity audit & on-page fine-tuning. Enhanced `public/llms.txt` and created `public/llms-full.txt` for AEO (Answer Engine Optimization) to boost AI search discovery (ChatGPT/Perplexity/Gemini). Unlocked mobile CTA visibility in `src/pages/blog/[slug].astro` ensuring Call and Telegram conversion paths are 100% accessible on mobile devices (>85% Cambodian traffic). Verified static build (`npm run build`, 17 pages compiled).
- Pushed all latest commits successfully to GitHub `origin/main` for live Cloudflare Pages deployment.

## 2026-08-08 (Playwright Audit & UI/UX Fixes)

- Conducted E2E Playwright audit and visual inspection on `http://localhost:4321/`. Fixed Khmer top diacritics clipping across all `<h2>` and `<h1>` elements by setting `leading-relaxed py-1` and `scroll-mt-24` (fixed header overlap protection). Replaced `--kh-red` raw primary red in `MooncakePage.astro` with Champagne Gold `#C5A059` to align with the Royal Champagne & Onyx Quiet Luxury brand palette. Verified zero JS console errors and 100% pass on `npx astro check`.
- Installed and integrated `lenis` (`^1.3.26`) smooth scroll engine in `src/layouts/Layout.astro` for Apple-grade luxury scrolling physics across SPA page loads.
- Installed `@tailwindcss/typography` (`^0.5.19`) plugin in `tailwind.config.mjs` and injected `prose prose-slate prose-lg` classes into `src/pages/blog/[slug].astro` for elegant article typography rendering. Passed `npx astro check` with 0 errors.
- Created custom AI Agent Skill `.agents/skills/ckm_blog_writer/SKILL.md` establishing standardized Khmer-only editorial guidelines, GEO chunking structure, local Cambodian polite persona (`លោកអ្នក` / `យើងខ្ញុំ`), and strict markdownlint formatting standards.
- Formulated the "Quiet Trust & Low-Key Master" Cambodian market SEO strategy. Updated `ckm_blog_writer/SKILL.md` with explicit zero-hype, zero-boasting rules that align with the low-key Sino-Cambodian owner persona while maximizing Google AI Overview (AEO/GEO) snippet capture.
- Investigated interrupted article writing session. Identified `src/content/blog/09-outdoor-tent-infrastructure.md` as the incomplete file. Expanded and completed Article 09 with GEO Quick Answer, portable kitchen infrastructure table, 5-point logistics checklist, outdoor food safety/temperature protocols, 4-item FAQ, and humble conclusion. Fixed frontmatter `coverImage` asset path. Verified with `npx astro check` (0 errors) and `npm run build` (17 static pages compiled successfully).
- Rewrote `.agents/skills/ckm_blog_writer/SKILL.md` to remove technical architecture and complex jargon, explaining instructions in simple language.
- Standardized formatting (table border alignments `:---`, heading structures, and proper blank lines) for the remaining 4 blog articles: `02-wedding-catering-budget-guide.md`, `03-food-tasting.md`, `04-hygiene-and-temperature-control.md`, and `06-signature-dishes.md`.
- Audited all 12 articles for natural colloquial phrasing, replacing casual pronouns (`អ្នក`) with polite client honorifics (`លោកអ្នក`) while keeping role nouns (`អ្នកជំនាញ`, `អ្នករត់តុ`) intact.
- Diagnosed freeze issue when editing [02-wedding-catering-budget-guide.md](file:///c:/Projects/CKM/src/content/blog/02-wedding-catering-budget-guide.md). Identified root causes: (1) Non-standard Markdown table delimiter `|---------------------|...|` without `:---` column alignment causing editor table linters to trigger CPU-heavy regex backtracking over multi-byte Khmer text, (2) Ultra-long single-line Khmer paragraphs (500+ chars / 1500+ bytes) stressing editor word-wrap engines, and (3) trailing slash markdown links. Standardized table delimiters, added natural paragraph line wraps, cleaned link paths, and verified 100% clean build (`npx astro check` & `npm run build`).
- Conducted full technical jargon & conversational tone audit across all 12 blog posts (`src/content/blog/*.md`). Replaced all raw English jargon (`Catering`, `VIP`, `Brand Identity`, `Buffet`, `Cocktail finger food`, `KVA`, `LED`, `FAQ`, `Generator`) with natural, polite Khmer terms (`សេវាកម្មធ្វើម្ហូប`, `ភ្ញៀវកិត្តិយស`, `អត្តសញ្ញាណរបស់ក្រុមហ៊ុន`, `អាហារប៊ូហ្វេ`, `អាហារសម្រន់ស្រាលៗ`, `កម្លាំងអគ្គិសនីខ្ពស់`, `អំពូលភ្លឺច្បាស់សន្សំសំចៃថាមពល`, `ម៉ាស៊ីនភ្លើងបម្រុង`). Replaced casual pronouns (`អ្នក`) with polite client honorifics (`លោកអ្នក`), and standardized `## ចម្លើយរហ័ស` (Quick Answer) sections across all 12 articles for 100% compliance with `.agents/skills/ckm_blog_writer/SKILL.md`. Verified with `npx astro check` (0 errors) and `npm run build` (17 pages compiled successfully).
- Designed and integrated the Quiet Luxury UI component `src/components/CateringPulse.astro` into `src/pages/blog/index.astro`. Renders daily-updated international catering trend cards in Khmer (with categories, summaries, and source links). Tested via `npx astro check` (0 errors) and `npm run build` (17 static pages compiled successfully).
- Implemented 7 performance-friendly Quiet Luxury & micro-UX enhancements across `ckmkh.com`: Astro View Transitions (`<ClientRouter />`), sticky navbar glassmorphism (`backdrop-blur-md bg-white/95`), ambient champagne glow overlays, global antialiased micro-typography (`-webkit-font-smoothing` and `tabular-nums`), native scroll reveal animation (`.reveal`), active compress touch feedback (`active:scale-[0.98]`), and zero CLS aspect ratio image containers (`object-cover object-top`). Verified clean build (`npm run build`, 30 static pages built in 6.45s) and E2E browser transition audit.
- Created dedicated custom skill `.agents/skills/ckm_pulse_writer/SKILL.md` specifying the Master Prompt for AI-generated Pulse content with dual strategic focus: high local Cambodian reader value and Google Search indexing optimization.
- Established the **Minimal Technical Data Rule (少用具體數據與硬規格條款)** across `.agents/AGENTS.md`, `ckm_pulse_writer/SKILL.md`, and `ckm_blog_writer/SKILL.md`. Mandated that public website content avoids dense hard numbers (e.g. no "4°C-60°C" or "50-100 KVA") to maintain a warm, qualitative, high-luxury reading experience, reserving technical data for the business owner to present directly during Telegram/Phone client consultations.
- Optimized RSS fetcher `scripts/fetch_catering_pulse.py` to target exclusively RSS 1 (`WedLuxe`) and RSS 2 (`CFE News`), configured 1 article per day processing with deduplication, updated GitHub Actions workflow `.github/workflows/daily_catering_pulse.yml` to run at off-peak minute `23 1 * * *` (08:23 AM ICT) and trigger Cloudflare Pages auto-deployment, and verified IndexNow API key (`c9b7e416a2d9426fa7406a09289196b0`) at `public/c9b7e416a2d9426fa7406a09289196b0.txt` with Bing/IndexNow submission and Google Search Console indexing notifications (`scripts/notify_indexing.py`). Verified clean build (`npm run build`, 30 static pages compiled successfully in 6s).
- Authenticated Google Service Account (`gsc-and-ga4@just-turbine-503117-k9.iam.gserviceaccount.com`) via `google_service_account.json` key with `sc-domain:ckmkh.com` (`siteFullUser` permission). Created live API query engine `scripts/generate_analytics_report.py` fetching 100% real Search Console analytics (35 clicks, 1,369 impressions, 2.56% CTR, 6.43 avg position, and #1 Google rankings for `catering service in phnom penh` & `private dinner party restaurants`), generating structured JSON (`scripts/reports/gsc_ga4_3month_report.json`) and Executive Markdown (`Docs/Reports/2026-Q3_GSC_GA4_3Month_Performance_Report.md`). Protected JSON key pattern in `.gitignore`.
- Analyzed GSC 90-day search queries gap (`ចុងភៅ` 165 impressions, `មុខម្ហូបការ` 65 impressions, `ប៉ាវហឺ` 15 impressions) and authored SEO Article 13 (`src/content/blog/13-master-chef-catering-secrets.md` / `13-master-chef-catering-secrets`). Written in 100% Pure Khmer (`km-KH`) with GEO Quick Answer (`## ចម្លើយរហ័ស`), elder vs. modern guest preference table, 5-step tasting checklist, and 4 Cambodian banquet FAQs. Verified clean build (`npm run build`, 31 static pages compiled successfully in 6.39s) and submitted to IndexNow.
- Separated Catering Pulse daily trend feed from the main blog listing page (`src/pages/blog/index.astro`). Replaced inline `<CateringPulse />` with a Quiet Luxury navigation callout banner directing readers to `/pulse/`, keeping `/blog/` focused 100% on the 13 deep-dive Khmer SEO guide articles. Verified clean build (`npm run build`, 31 static pages built in 7.17s).
- Configured 12 items per page pagination for both `/blog/` (`src/pages/blog/index.astro` & `src/pages/blog/page/[page].astro`) and `/pulse/` (`src/pages/pulse/index.astro` & `src/pages/pulse/[page].astro`). Sorted blog entries descending by ID so Article 13 (`13-master-chef-catering-secrets`) appears prominently at position #1 on Page 1. Verified clean static build (`npm run build`, 33 static pages compiled in 6.43s).
- Fixed gold overlay sliding across screen on blog detail pages (`/blog/[slug]/`). Refined `src/components/ReadingProgress.astro` to an ultra-thin 2px progress line (`h-[2px] max-h-[2px] z-[100] bg-champagne-dark/80`), replacing the heavy gradient fill and removing delayed 150ms transition animations. Verified clean static build (`npm run build`, 33 static pages compiled in 7.82s).
- Updated `.agents/skills/ckm_blog_writer/SKILL.md` and `.agents/AGENTS.md` with Section 1.2 "Promotional Boundaries Mandate": strictly forbidding unverifiable claims about high-tech/automated kitchen equipment, unlimited custom fusion menus, or online digital app booking/payments/plan selectors. Mandated 100% Cambodian localized photography and direct Telegram/Phone 1-on-1 consultations. Audited and rewritten Articles 12, 13, 04, 09 to align 100%. Verified clean static build (`npm run build`, 33 static pages compiled in 7.49s).

## 2026-08-09 (Safe East Asian Verified RSS & Pipeline Upgrades)

- Configured pure East Asian & geopolitically safe RSS dataset in `src/data/pulseData.json` (13 articles) containing 100% Chinese/Teochew, Khmer, and Japanese culinary stories, completely excluding Thai, Vietnamese, Western fast food, and movies.
- Remapped all 13 external source URLs to 100% active, live, and verified links (HTTP 200 OK) from Just One Cookbook, The Woks of Life, Epicurious, and BBC Good Food.
- Downloaded and compressed all 13 article cover images directly from their live CDN/og:image sources into high-quality WebP files stored at `public/images/pulse/` (strictly < 45 KB per image) to guarantee zero CLS and ultra-fast page load speeds in Cambodia.
- Upgraded the automated daily pipeline script `scripts/fetch_catering_pulse.py` to target `gemini-2.5-flash` model for localized translations and content generation as requested.
- Integrated a robust 10-second safety cooldown pacing delay (`time.sleep(10)`) between consecutive API calls to prevent HTTP 429 Rate Limit triggers on Google's developer API tier.
- Verified build compatibility with `npm run build` (48 static pages compiled cleanly with 0 errors).

## 2026-08-11 (Automation Pipeline Alignment & Cloudflare Edge Cache Purge Integration)

- **Workflow Pipeline & Execution Order Realignment**:
  - Reordered GitHub Action pipeline steps in `.github/workflows/daily_catering_pulse.yml` so that `git commit & push` triggers single unified Cloudflare Pages deployment before running indexing & cache purge scripts.
  - Eliminated redundant `cloudflare/pages-action` direct deployment step to prevent Cloudflare build race conditions and quota duplication.
- **Cloudflare Edge CDN Cache Purge Automation**:
  - Added Cloudflare Edge CDN cache purge step (`purge_everything: true`) targeting `ckmkh.com` Zone ID `d459c80e06d000c6e1927783fc6b3a7a` via `CLOUDFLARE_API_TOKEN` after 35-second deployment wait.
- **Agent Rule Standardization**:
  - Added `Automated Deployment, Edge Cache Purge & Performance Protocol` to `.agents/AGENTS.md` specifying strict workflow execution order, anti-race-condition rules, Cloudflare Zone Purge SOPs, and editor freeze prevention rules for Khmer text.

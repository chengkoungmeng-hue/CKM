# Project Agent Rules — ckmkh.com

<RULE[project_scoped]>

## 0. How to use this file

- Every rule below describes **what the code actually does today**, not what it should
  ideally do. Before adding a rule, verify it against the source. Before trusting a rule,
  spot-check it — this file has drifted from reality before, and a confidently wrong rule
  is worse than no rule.
- If you change behaviour that a rule describes, update the rule in the same commit.
- Rules marked **[REGRESSION]** exist because that exact bug shipped to production.
  Do not "simplify" them away.
- Run `python devops/check_content.py` before committing content. It enforces the
  mechanical half of this file in under a second. `npm run build` runs it with `--strict`
  and fails on any error, and `.github/workflows/content_gate.yml` runs it on every push
  and PR touching content — Cloudflare Pages builds *after* merge, so CI is the real gate.
- **Verify with a different mechanism than the one that made the change.** A checker that
  shares an assumption with the code it checks is not a check: on Sunder a rename pass and
  its verification script used the same regex, so the script reported real breakage as a
  false positive. Confirm frontmatter budgets against rendered `dist/` HTML, `llms.txt`
  against built routes, and UI behaviour in a real browser.
- **Skills policy (revised 2026-08-20).** `.agents/skills/` was removed on 2026-08-14:
  the five skills either duplicated this file, restated specs that live in code, or were
  generic audit checklists producing findings untethered from §18's measured data, and
  `ckm_backlink_writer` described a programme §19 rejects. On 2026-08-20 the owner
  reinstated ONE skill, `ckm-seo`, under a strict boundary: this file stays the only home
  of RULES; the skill holds only execution material (Khmer FB voice, image prompts,
  platform mechanics with research dates, expired after 6 months). The skill must never
  restate a rule from this file; on conflict this file wins. Do not create further
  skills without recording the same boundary here.
- **Prefer measuring over reasoning.** Nearly every error found on 2026-08-14 — a
  fabricated audit script, a cache purge silently failing for want of a permission, a
  secret that reported success while still holding the old credential — was invisible to
  inspection and obvious to a single command. When a claim in this file can be checked,
  check it.

## 1. Work log

- Document significant work, decisions and outcomes in `WORKLOG.md` at the repo root.
- Record architectural decisions and recurring failure modes here, so the next session
  does not rediscover them.

## 2. Language scope

- The live site is **Khmer only**. `baseLang` in `src/layouts/Layout.astro` is hardcoded
  to `"km"`; `/zh/` and `/en/` are 301-redirected via `public/_redirects`.
- The `zh` / `en` entries in `brandDict`, `navTranslations` and `homeData.ts` are
  unreachable legacy. Do not extend them. Do not link to `/zh/…` or `/en/…` from content.
- Only edit Khmer content at the root of content folders (`src/content/blog/*.md`,
  `src/pages/index.astro`).

## 3. Domain & canonical

- Canonical domain is exactly `https://ckmkh.com`. Never `www.`, never bare `http://`.
- `trailingSlash: 'always'`. Every internal link must end in `/` or Cloudflare issues a
  301 and the link equity is spent on a redirect.
- **[REGRESSION] Canonical pulse pages use descriptive slug paths only.** Emitting both
  `/pulse/[slug]/` and `/pulse/[id]/` as 200 OK HTML pages causes Google Search Console to flag
  "Duplicate, Google chose different canonical than user". Static generation in `pulse/[id].astro`
  emits only `/pulse/[slug]/`, and `public/_redirects` 301-redirects `/pulse/pulse-NN/` to `/pulse/:slug/`.

## 4. Client-side scripts

- **[REGRESSION] Guard every listener against double-binding.** `<ClientRouter />` fires
  `astro:page-load` at window `load`, *and* module scripts run again at
  `readyState === "interactive"`. Registering in both places binds the same handler twice.
  This shipped: the mobile menu bound two click listeners, the first opened the overlay and
  the second closed it inside the same click, so the navigation was completely unusable on
  mobile for as long as it was live.
  - Mark the element: `if (el.dataset.ckmBound === "1") return; el.dataset.ckmBound = "1";`
    The marker rides on a node ClientRouter swaps, so navigation re-binds and never stacks.
  - Listeners on `window` / `document` are **never** swapped. Bind those once at module
    scope behind a boolean, and resolve the element lazily inside the handler.
- **[REGRESSION] Content must never depend on JavaScript to become visible.** `.reveal
  { opacity: 0 }` lived in `Layout.astro` with `.active` as the only route back to visible,
  and **nothing in this repository ever added `.active`** — there has never been an
  `IntersectionObserver` in `src/`. Eleven live elements carried the class, including the
  whole `<article>` body in `blog/[slug].astro`. It was harmless only because the rule was
  component-scoped and matched nothing in slotted children — meaning **§5's own correct
  advice, to move such styles into `<style is:global>`, would have blanked every article
  on the site.** Removed 2026-08-16. If you add a reveal animation, start from `opacity: 1`
  and let the script *enhance*, so a script that never loads costs an animation and not the
  content. Sunder shipped exactly this bug and an audit dismissed it as unreachable
  "because the observer always runs for JS-enabled visitors" — module loading fails
  independently of JS being enabled.
- **[REGRESSION] An accessible name must contain the visible label (WCAG 2.5.3).** The
  sticky mobile call bar showed `011 827 782` and had the accessible name `ហៅទូរស័ព្ទ`, so
  a voice-control user could not activate the primary CTA by saying what they saw. Note
  Lighthouse weights `label-content-name-mismatch` at **0** — the category can score 100
  while this fails. A 100 is not evidence.
- **Keep the skip link.** `<a href="#main-content" class="skip-link">` is the first element
  in `<body>`; `<main>` carries `id="main-content" tabindex="-1"`. Twelve focusable elements
  precede the content on every page (WCAG 2.4.1, Level A).
- No scroll-hijacking libraries. Lenis was removed: on touch devices it defaulted to
  `syncTouch: false` and intercepted nothing, while still shipping ~19 KB and leaking one
  immortal `requestAnimationFrame` loop per navigation. Native `scroll-behavior: smooth`
  on `html` is the whole solution.
- Respect `prefers-reduced-motion`. The guard lives in the global `<style is:global>` block
  in `Layout.astro`.

## 5. Astro & CSS scoping

- **[REGRESSION] A `<style>` block in an `.astro` file is scoped to that component.**
  `Layout.astro` defined `.reveal { opacity: 0 }` intending it to animate sections in
  `index.astro`. It compiled to `.reveal[data-astro-cid-…]` and matched nothing, so the
  animation was dead the entire time — and the `.prose` table-overflow guards in the same
  block died with it. Styles that must reach slotted children go in `<style is:global>`.
- `inlineStylesheets: 'always'` + `_headers` setting HTML to `max-age=0, must-revalidate`
  means the CSS is re-downloaded on every page view and can never be cached across pages.
  This is a deliberate trade (one less round trip on first paint). Do not change it
  casually, and measure both sides if you do.

## 6. Images

- Use Astro's `<Image />` / `getImage()` for anything under `src/assets/`. It emits AVIF
  and correctly sized variants automatically.
- **[REGRESSION] `og:image` must resolve.** Blog posts pointed at `/blog/og/{slug}.png`,
  a route that never existed, so all 15 articles shipped a 404 preview to Facebook and
  Telegram — the two channels this business actually runs on. Derive share cards from the
  cover with `getImage({ width: 1200, height: 630, format: 'jpeg' })`; use JPEG, because
  older social scrapers do not handle AVIF/WebP reliably.
- **[REGRESSION] Decorative duplicates must be `loading="lazy"`.** The blurred backdrop in
  `CateringPulse.astro` had no `loading` attribute, so it eagerly fetched the same URL as
  the lazy foreground image. That put 122 KB of below-the-fold pulse imagery on the
  homepage critical path — 66% of the initial payload, each image larger than the LCP hero.
- **[REGRESSION] Pulse illustrations are rendered from our own text, never rehosted.**
  Until 2026-08-22 the pulse pipeline downloaded the source recipe blog's photograph and
  served it from `ckmkh.com`: **35 files in `public/images/pulse/` taken from seven
  third-party blogs, with no credit anywhere on the page.** Re-encoding to WebP and
  renaming the file changes nothing about who owns the photograph — that was copyright
  exposure with no defence, on the pages that grow by one a day. Removed 2026-08-22 and
  replaced by `devops/render_pulse_card.py`, which draws a `1200×675` PNG from the entry's
  **own Khmer text** — the shortest `key_points_km` entry set large, with `title_km` as a
  small attribution line — so nothing from a third party is reproduced. The pipeline must
  never again download and rehost an image from a source feed. If a future entry needs a
  photograph, it must be one the owner supplies or one this project holds a licence to.
- **The card renderer needs Pillow built against raqm, and a local render is not
  evidence.** Khmer requires complex shaping: a COENG subscript stacks below its base
  consonant, and without shaping it lands beside it as a separate glyph. Pillow only
  shapes when built against raqm. Measured 2026-08-22 — `ubuntu-latest` reports Pillow
  12.3.0 with raqm 0.10.5 and a shaped-to-naive advance ratio of `0.556`, i.e. shaping is
  active; **Windows wheels report `raqm=False`**, so anything rendered on the owner's
  machine proves nothing about the artefact CI will publish. Verify card output from a CI
  run. FreeType cannot read woff2, so `devops/fonts/` holds a ttf converted from the same
  Hanuman the site self-hosts; it is a build input, not a site asset, and does not belong
  in `public/`.
- **The card is a SHARE image, not an in-article hero.** It feeds `og:image` and the
  JSON-LD `image`, and it fills the image slot on the listing pages. The pulse article's
  own top image block was removed 2026-08-22 for two independent reasons: a card whose
  text is a key point, sitting directly above the article that contains that key point,
  tells the reader nothing twice; and that block rendered the same file **twice**, once
  blurred as a backdrop behind itself — the defect the bullet above records for
  `CateringPulse.astro`, shipped again on every pulse page. Do not reinstate it. The
  listing layouts were deliberately left alone.
- Blog inline images are `1600×900` (16:9) WebP in `public/images/`, named
  `blog_NN_inline_khmer.webp`. Article `NN` references image `NN` — nothing else.
  `check_content.py` enforces this.
- All imagery must depict authentic Cambodian / Phnom Penh banquet reality. No Western
  stock kitchens, no industrial hardware.
- The homepage `#gallery` caption claims real photographs (`រូបភាពពិតៗ`). Only put genuine
  photos there. Illustrative or AI-assisted imagery belongs in blog bodies, never there.

## 7. Icons

- Use `@lucide/astro`.
- Known exceptions, all pre-existing: the Facebook glyph in `index.astro`, three phone
  glyphs in `homeData.ts`, one warning glyph in `404.astro`, one in `MooncakePage.astro`.
  These are brand marks or one-offs with no Lucide equivalent — leave them, but do not add
  more.
- **[REGRESSION] Never reference an icon font that is not loaded.** Four FontAwesome
  `<i class="fas …">` tags sat in `blog/[slug].astro` while `@fortawesome/fontawesome-free`
  was installed but imported nowhere, so the phone and Telegram CTAs on every article had
  a blank gap where the icon should be.

## 8. Fonts

- Khmer body text intentionally uses the **system fallback** for 0 CLS and instant LCP.
  Only Hanuman is self-hosted, from `public/fonts/`, for headings.
- **Do not name a font family that is not loaded.** `font-km-sans` still resolves to
  `'Kantumruy Pro'`, which has no `@font-face` anywhere — it silently falls through to
  `sans-serif`. It reads as a bug to every reviewer. Either load it or drop the name.
- `@fontsource/*` packages in `package.json` are unused. Do not import them without
  measuring the cost on 3G first.

## 9. Palette

Values are authoritative from `tailwind.config.mjs`. Keep this table in sync with it.

| Token | Hex | Use |
| :--- | :--- | :--- |
| `onyx` | `#171717` | Dark sections, primary text |
| `champagne` | `#C5A059` | Gold accent on dark backgrounds |
| `champagne-dark` | `#8C6D31` | Gold accent on light backgrounds (contrast) |
| `pearl` | `#FDFCF8` | Light section background |

- The `primary` / `gold` / `dark` / `cream` block in `tailwind.config.mjs` is legacy.
  Do not use it in new work.
- Avoid raw `amber-*` / `blue-*` / `slate-*` accents where a token exists. Plain primary
  colours undercut the quiet-luxury positioning.

## 10. Brand voice

- Reader honorific: **`លោកអ្នក`**. Never plain `អ្នក`.
- Team self-reference: **`យើងខ្ញុំ`**.
- Zero hype. No `第一`, `最強`, `神級`, `無敵`, or Khmer equivalents.
- 100% Khmer in public copy. No parenthetical English or Chinese translations.
- **No English word or engineering abbreviation appears in article bodies.** Substitute:

  | English | Khmer |
  | :--- | :--- |
  | `Catering` | `សេវាកម្មម្ហូបការ` / `សេវាកម្មធ្វើម្ហូប` |
  | `VIP` | `ភ្ញៀវកិត្តិយស` |
  | `Buffet` | `អាហារប៊ូហ្វេ` |
  | `Cocktail` / `Finger food` | `អាហារសម្រន់ស្រាលៗ` |
  | `Food safety` / `HACCP` | `អនាម័យនិងសុវត្ថិភាពម្ហូបអាហារ` |
  | `Brand identity` | `អត្តសញ្ញាណរបស់ក្រុមហ៊ុន` |
  | `LED` | `អំពូលភ្លឺច្បាស់សន្សំសំចៃថាមពល` |
  | `Generator` | `ម៉ាស៊ីនភ្លើងបម្រុង` |
  | `FAQ` (as a heading) | `## សំណួរដែលសួរញឹកញាប់` — never `(FAQ)` |

  `50-100 KVA` → `កម្លាំងអគ្គិសនីខ្ពស់` with Khmer numerals, but see §11: prefer omitting
  the figure entirely.
- Cultural anchors: honour elders (`ចាស់ទុំ`) in menu advice; address dry-season heat and
  wet-season rain for outdoor events; answer real Phnom Penh logistics (borey approval,
  parking, narrow lanes).

## 11. Promotional boundaries

**We market this business on the owner's behalf. We cannot verify his operations, so we
never commit him to anything.** State what is generally true, and route every specific
commitment to a direct conversation.

- Forbidden claims: modern/automated kitchen technology, digital temperature monitoring,
  unlimited custom or international fusion menus, online booking/payment/plan-selection,
  VAT invoice guarantees.
- Forbidden absolutes: `១០០%` anything, "no hidden costs whatsoever", any unconditional
  guarantee. **[REGRESSION]** `សុវត្ថិភាពអនាម័យ១០០%` and `គ្មានការចំណាយលាក់កំបាំង` both
  shipped, and the latter was contradicted two articles later by our own FAQ.
- **Never publish the owner's margin.** A cost-breakdown table exposing
  `ប្រាក់ចំណេញ ១៥%-២០%` shipped on the one page that also publishes prices — handing a
  negotiating lever to every buyer who read it.
- Reserve hard figures (temperatures, kVA, exact prices, minimum table counts, service
  areas) for the owner's own Telegram or phone consultation. `check_content.py` warns on
  Celsius and kVA specs in article bodies.
  - **Absolutes are an ERROR, not a warning**, as of 2026-08-16 — the backlog reached zero
    so the rule can block. `hard-spec` stays a warning: "prefer omitting" is a judgement,
    an unconditional guarantee is not.
  - **[REGRESSION] `check_hard_specs` used `re.search` and reported one hit per file.**
    Article 04 showed one Celsius warning while carrying three. The true count was 15, not
    5. Use `re.finditer` for any rule that can legitimately fire more than once — a silent
    undercount reads as "nearly clean".
  - Figures that are **general planning advice to the reader** (floor area per guest,
    kitchen-to-table distance, height off the ground) are not commitments about what CKM
    supplies and are deliberately kept. Do not write a blanket `ម៉ែត្រ` rule; it matches
    `ទែម៉ូម៉ែត្រ` ("thermometer").
- Forbidden topics: tipping, leftover packing, bargaining or cheapness framing. FAQs stay
  on elder care, service rhythm, ingredient freshness and venue coordination.

## 12. Content consistency

**[REGRESSION]** The same fact was stated three different ways across the site: abalone
broth simmer time (`៨ ទៅ ៨៦ ម៉ោង` — a corrupted number — vs `១២ ទៅ ២៤` vs `៨ ដល់ ១២`),
booking lead time (`៦ ទៅ ៨ ខែ` vs `៤ ទៅ ៦ សប្តាហ៍` vs `២ ទៅ ៣ ខែ`), and room-temperature
holding (article 06 said 3 hours, article 04 said 2). Before stating a fact, grep for it.

- Booking lead time, site-wide: **`២ ទៅ ៤ សប្តាហ៍`**, always closing with an invitation to
  contact and confirm the date. Do not reintroduce a busy-season caveat.
- Simmer times and course positions vary by ingredient size and family custom. Say so;
  do not invent a fixed number.
- Dish names must match `src/data/homeData.ts` exactly. Lotus-leaf rice is
  **`បាយខ្ចប់ស្លឹកឈូក`** — `ខ្ចប់` means "to wrap" and is the root of `កញ្ចប់`; `ខ្ទប់` is
  not the word and was live on the homepage.

## 13. Khmer text integrity

**[REGRESSION]** Thai, Chinese, Japanese and Devanagari characters shipped inside Khmer
words — `หัวใจ`, `วัฒนธรรม`, `環境的控制與使用醬料調配提升風味`, a Devanagari `।` standing in
for `។`, and `ควរ` for `គួរ` inside an H3. Hanuman cannot render any of them, so they
reach Khmer readers as tofu boxes. `ដើមីបី` (for `ដើម្បី`) appeared 16 times, including in
a meta description that renders in the Google result.

- Khmer copy contains Khmer, Latin and Khmer numerals only.
- `devops/check_content.py` fails the build on any Thai / Devanagari / CJK / Kana
  codepoint in an article or in a Khmer pulse field.
- The pulse generator rejects a Gemini response containing foreign script rather than
  publishing it. Do not downgrade that to silent stripping — removing a Chinese word from
  the middle of a sentence leaves broken Khmer grammar.
- Watch for doubled words (`លោកលោកអ្នក` shipped five times, once in an H2).

## 14. Frontmatter & schema

- `src/content.config.ts` is the source of truth. Zod **strips unknown keys**:
  `target_keyword` and `slug` are in almost every article's frontmatter and are read by
  nothing. `schemaType` is declared but `blog/[slug].astro` hardcodes `"@type": "Article"`.
  Either wire them up or delete them — do not add more inert fields.
- **[REGRESSION] `date:` is required.** When it was missing, `blog/[slug].astro` fell back
  to `new Date()`, so every deploy re-stamped 14 evergreen articles as published today —
  a textbook date-manipulation signal. The fallback now omits `datePublished` entirely;
  keep it that way.
- **[REGRESSION] `seoTitle` ≤ 60 units, `description` ≤ 155 units — measured in rendered
  width, never in `len()`.** `check_content.py` enforces both (`title-too-long`,
  `description-too-long`). `blog/[slug].astro` passes `seoTitle || title` and the layout
  appends no brand suffix, so the budget is the full 60.
  **Do not "simplify" this to a character count.** Measured 2026-08-16: a Khmer base
  consonant is 1.6–2.0× a Latin character, but 22 of the 128 Khmer codepoints have *zero*
  advance width and a subscript after COENG costs 0.113 instead of 1.6–2.0. The errors
  nearly cancel — mean ratio 1.03 — so `len()` looks right while being ±11% wrong per
  article. It would have missed 4 of the 6 real violations found that day. The per-codepoint
  table in `check_content.py` came from a browser (`devops/build_width_table.cjs`) and
  reproduces it within 2.6%.
- **[REGRESSION] Truncate Khmer on cluster boundaries, never on a codepoint index.**
  `Layout.astro` used `slice(0, 152)` for the meta description; 9.1% of cut points split a
  base consonant from its COENG and shipped a dotted circle to the Google snippet — the
  same defect `check_khmer_clusters` fails the build for in source. Use `truncateKhmer`.
- **[REGRESSION] No opener may be shared by more than 2 articles.** Eleven of fifteen
  descriptions once opened `ស្វែងយល់ពី` (articles 01–11) and four seoTitles opened
  `របៀបជ្រើសរើស`. Each article reads fine alone — the failure is only visible on a search
  results page. `check_content.py` caps the first 10 codepoints of `seoTitle`,
  `description` and the first prose paragraph at 2 articles (`repeated-opener`).
  Headings are exempt on purpose: this section *requires* the FAQ and conclusion headings
  in every article.
  **When fixing a batch, choose the opening per article, not per batch.** Sunder fixed this
  exact defect with a batched rewrite and produced nine new templates of five articles each.
- **The 60/155 budget applies to pulse and to page templates too, not just articles.**
  `check_content.py` scans `src/content` and `pulseData.json`; it does **not** read
  `.astro` page titles, which is how `- CKM Premium Catering` stayed live on the blog
  listing pages. Verify budgets against rendered `dist/` HTML, not frontmatter.
  - **[REGRESSION] Do not append a brand suffix to a pulse title.** `" - CKM"` cost 7.4
    units and pushed six entries past the budget by itself; Google cut the headline, not
    the suffix. Removed 2026-08-16.
  - **[REGRESSION] `truncateKhmer` in Layout.astro is a cluster-safety net, NOT the budget.**
    It counts codepoints, and a 153-codepoint Khmer summary measures 172 units — sixteen
    pages passed the net and still shipped truncated by Google. Enforce length at source,
    in units. Never cite "the 155-char slice" as the budget.
  - Pulse rules (`pulse-title-too-long`, `pulse-summary-too-long`, `pulse-english-word`,
    `repeated-opener`) are **blocking**, and `fetch_catering_pulse.py` rejects and retries
    on all four so new entries cannot reintroduce them. It **imports** `display_width` from
    `check_content.py` — one measured table, two consumers. Do not copy the table.
  - **[REGRESSION] A retry must tell the model what actually failed.** The retry prompt was
    hardcoded to say "it contained non-Khmer characters" for every rejection reason, so the
    2026-08-16 run was rejected three times for missing subheadings and told three times to
    fix characters that were correct. Every `reject_reason` now needs a `RETRY_GUIDANCE`
    entry; add one whenever you add a reason.
- **`revision:` is optional, hand-set, and drives `dateModified`.** Set it only when an
  article's substance changes, to the date that actually happened. **Never stamp it on
  deploy** — that is the same date-manipulation signal the `date:` fallback caused above.
  Changing a title or a description is metadata, not substance; it does not earn a revision.
- `authoritySignals` render as trust badges directly under the hero — the first thing a
  mobile reader sees. Make them carry a checkable fact and vary them per article; identical
  boilerplate across 15 posts trains readers to ignore the badge. Shipped placeholders to
  avoid: `សេវាកម្មប្រកបដោយវិជ្ជាជីវៈ`, `បច្ចេកទេសចម្អិនកម្រិតខ្ពស់`.

### Article structure

Merged here from the retired `ckm_blog_writer` skill, which duplicated most of this file.
Every item below came out of an audit of the 15 live articles.

- **Length**: at least 1,200 Khmer characters.
- **Quick answer**: directly under the intro, a `## ចម្លើយរហ័ស` heading with a 40–80
  character answer to the reader's actual question. This is what AI summaries lift.
- **One H1 per article.** Everything else is `##` / `###`. Keep heading line-height loose —
  Khmer diacritics (`ើ ឹ ី`) collide with the line above when it is tight.
- **At least one comparison table** (budget split, package contrast, table-count estimate)
  and one practical checklist.
- **[REGRESSION] Section order is body → `## សំណួរដែលសួរញឹកញាប់` → `## សេចក្តីសន្និដ្ឋាន`.**
  The conclusion sits closest to the CTA; it belongs where the reader is ready to act, not
  before an administrative note. This rule previously named articles 02, 03, 04, 10, 11
  and 12. **Measured 2026-08-15, thirteen of fifteen were non-conforming** — 02–08 and
  10–12 and 14–15 had the conclusion first, and 13 had no conclusion at all. Only 01 and
  09 were correct. All fixed; `devops/fix_section_order.py --check` re-verifies in a
  second and refuses to write unless the file's content is a permutation of itself, so it
  can only ever move blocks, never alter Khmer.
  *A rule that names specific files goes stale silently. Prefer a checker.*
- **[REGRESSION] At least 3 in-context links to other `/blog/` articles per post.**
  Articles 13, 14 and 15 shipped with **zero** internal links — no site authority reaches
  them and no reader continues from them. Anchor text describes the destination, never
  "click here"; the URL **must** end in a slash or §3's redirect penalty applies.
  Enforced by `check_content.py` (`too-few-internal-links`, and `link-missing-slash`), so
  article 16 cannot ship the same way.
- **Internal links are declared, not pattern-matched.** `src/data/internalLinks.json` names
  the article, an EXACT anchor string that already exists in that article's prose, and the
  destination; `devops/apply_internal_links.py` wraps it. It is idempotent and refuses any
  anchor that is not unique or that sits in a heading, a table row or an existing link.
  **Do not port a keyword-regex injector.** Sunder's `apply_internal_links.cjs` corrupted
  130 places across 53 files by replacing `（TCO）` with a space-prefixed `[TCO](…)`, and
  Khmer makes that
  approach strictly worse: Khmer has no spaces between words, so there is no `\b` to
  anchor a pattern to and no way to tell a word from the middle of a longer one. Exact
  strings sidestep the whole problem.
- **[REGRESSION] No English word appears in article prose, including parenthetical
  glosses.** §10 says this, and it had drifted anyway: `(Premium)`, `(Food Tasting)`,
  `(Borey)` ×2 and a bare `Vs` and `VIP` were live, each sitting beside the Khmer that
  already said it. A gloss in brackets is still an English word.

## 15. Pulse pipeline

- **[REGRESSION] URLs are permanent.** `id` and `slug` used to be reassigned from list
  position on every run, so adding one article rewrote all 20 URLs; the previous day's
  pages 404'd while `notify_indexing.py` submitted the new ones to Google and Bing.
  `id` is now monotonic (`next_pulse_id`) and `slug` never encodes position. Assign both
  once at insert; never recompute.
- **The archive is the reserve, and it is reached lazily.** A feed's default URL returns
  only its most recent page — 99 items across all eight sources. Both platforms expose
  their archives (`?paged=N` on WordPress, `?start-index=N&max-results=M` on Blogspot),
  and walking 12 pages of each reaches **1,124 items surviving `EXCLUDE_REGEX`**: about
  three years of daily publishing from the back catalogue alone, measured 2026-08-15 and
  truncated at 12 pages, so the real depth is greater. Page 0 is fetched first and is
  enough on an ordinary day; `fetch_verified_gourmet_rss_items` only goes deeper when a
  shallower pass turned up nothing unseen, so a healthy run still costs one request per
  feed. This is why losing a source is survivable rather than fatal.
- **`verify_live_url` runs on the SELECTED item only.** It, and the image extractor that
  used to sit beside it, once ran for every candidate during the fetch — up to two extra
  HTTP requests each, ~188 per run to publish one article — while only ever being needed
  for the one item that gets published. Moving that work to selection time is what makes
  walking the archives affordable. Selection walks down the sorted queue until a URL
  resolves, so one dead link costs the next-best article rather than the whole day.
  The image extractor is gone entirely as of 2026-08-22; the reason is in §6.
- **[REGRESSION] The pipeline never downloads an image from a source feed.** See §6 for
  the incident and for what replaced it. Here the consequence is narrower and absolute:
  no step of this pipeline may fetch, re-encode or write a byte of third-party media into
  `public/`. The entry's illustration is generated from the entry's own Khmer text by
  `devops/render_pulse_card.py`, which runs in the same job — Python only, so the
  no-JavaScript rule further down this section is unaffected.
- **The outbound link to the source recipe blog was removed 2026-08-22.** The Khmer text
  is written from a dish name and a short feed description; it is never a translation of
  the source article, so no attribution is owed. The generation prompt already instructs
  the model not to mention the source blog — the template then named and linked it on
  every page, contradicting the pipeline's own instruction and sending what little
  authority these pages carry to a competitor's recipe site. Do not restore the link, and
  keep any wording elsewhere on the site (the disclaimer page in particular) consistent
  with this: the feed takes a dish name as a starting point, nothing more.
- **[REGRESSION] The daily item is the NEWEST unseen one, not the first in `FEEDS` order.**
  Selection used to take the first unseen item while walking `FEEDS` in order, so the queue
  followed the source list rather than the calendar. Measured 2026-08-15 with 88 unseen
  items queued: the next 14 days would have published content 182 to 1,399 days old, and
  `omnivorescookbook.com` — the most active source at ~18 posts/month — would not have been
  reached until day 48, by which point ~28 of its posts would have scrolled out of its
  10-item window unread. The reason to prefer fresh is **shelf life, not recency**: an
  active feed's items are perishable, a dormant feed's back catalogue is not. Spend the
  perishable supply first; the dormant catalogue is the reserve that covers a lean day.
  Adding a feed to `FEEDS` therefore no longer changes *when* it is reached — only what is
  in the pool.
- **Banquet fit re-ranks the queue; it does not filter it (owner directive 2026-08-22).**
  Freshness alone kept selecting home-cooking posts under a banquet brand — the mismatch the
  bullet below already notes about the feed sources. `BANQUET_REGEX` now adds a bounded
  `BANQUET_FIT_BONUS_DAYS = 21` to the sort key of an item whose title carries a banquet
  marker, so it ranks as if published 21 days later than it was. It is a bonus, never a
  filter: nothing is excluded, and an item cannot overtake anything more than 21 days fresher.
  21 days sits inside the ~17-day shelf life this file records for `omnivorescookbook.com`'s
  10-item window, so no perishable item is held back long enough to scroll out unread and
  nothing from the dormant archive can jump a fresh item. Items that fail date parsing
  (`datetime.min`) are excluded from the bonus so "undated sorts last" stays exact.
  Calibrated against real data, not guessed: over the 36 `source_title_en` values in
  `pulseData.json` the first draft matched 3 and missed four Cambodian dishes; the shipped
  pattern matches 9 of 36.
- **[REGRESSION] Feed dates come in two formats and only one parser was applied.**
  WordPress feeds emit RFC 2822; Blogspot emits ISO 8601, and the extraction loop keeps the
  *last* matching element, which on Blogspot is the Atom `<updated>` field — so even a feed
  carrying a valid RFC 2822 `<pubDate>` arrives as ISO. `parsedate_to_datetime` rejects ISO,
  which silently collapsed 47 of 88 queued items to `datetime.min`. Parse every feed
  timestamp through `parse_any_date()`, which accepts both, always returns a
  timezone-aware datetime, and sorts unrecognised input last rather than raising —
  `sorted()` raises mid-sort and takes the whole run down.
- Order of operations, and it is not negotiable: generate → validate → commit → **wait for
  the page to actually be live** → purge Cloudflare cache → IndexNow → GSC. The workflow
  polls the real URL; it does not sleep and hope. Never announce a URL before it resolves.
- Index only when something actually changed. `if: always()` on the indexing step meant
  daily submissions of unchanged URLs.
- **[REGRESSION] That rule came back through `publish.yml`'s `workflow_run` trigger.** The
  gate was `conclusion == 'success'`, and a pulse run that publishes *nothing* still
  succeeds — so on every dry day `publish.yml` ran anyway. Worse, both of its no-slug
  routes ended in a purge: if `HEAD` was still yesterday's `chore(pulse): add …` commit it
  polled that stale URL, got 200 immediately and purged; if `HEAD` was any other commit it
  took the `sleep 240` branch, which set `live=true` with **no HTTP check at all**. Either
  way the zone was purged and ~75 URLs resubmitted, daily, for nothing. `publish.yml` now
  requires, on `workflow_run` only, that `HEAD` be a pulse commit less than an hour old.
- **A failure that cannot turn a run red will not be noticed.** Verified 2026-08-15 by
  audit: fourteen distinct paths ended with a green run and nothing published. Two rules
  follow, and both are load-bearing:
  1. `fetch_catering_pulse.py` exits **non-zero** whenever it publishes nothing. There is
     no longer such a thing as a legitimate empty day — selection walks every archive page
     of every feed first, so "nothing to publish" means the sources are spent
     (`archive-exhausted`), the network is broken (`all-feeds-failed`), every candidate URL
     is dead (`all-candidates-dead`), or Gemini failed (`generation-*`). Each needs a
     person. Keep the reason strings distinct; they are the whole diagnosis.
  2. `notify_indexing.py` returns a status from each of its three steps and exits non-zero
     if any failed. Every one of them used to catch its own exception, print a warning and
     return `None`, which is how the Cloudflare purge "had been failing silently on every
     run" behind a green workflow.
- **`check_pulse_health.py` is the backstop, and it is deliberately outcome-based.** It
  ignores *why* a run failed and asks only how long since anything reached
  `pulseData.json`, failing the job past a threshold. That single test covers all fourteen
  paths at once, including ones nobody has thought of. Run last, `if: always()`, so it can
  never block a publish that did succeed.
- **The retry loop must walk DOWN the model ladder.** `call_gemini_api_robust` takes a
  `start` index and the quality-retry passes the attempt number. Every rejection used to
  restart at `MODEL_LADDER[0]`, and since `gemini-3.6-flash` reliably returns *something*,
  all three attempts hit the same model — a Khmer-quality regression in that one model was
  therefore permanent, arriving with no warning on a provider-side update.
- Nothing in the workflow runs JavaScript. Do not reintroduce `setup-node` / `npm ci`.
- Feed sources currently produce Western and Japanese home recipes, which sit oddly under
  a Khmer-Chinese banquet brand. Prefer sources matching the brand's actual cuisine.
- **The prompt and the category taxonomy live in `devops/fetch_catering_pulse.py`, not in
  documentation.** The retired `ckm_pulse_writer` skill restated both, which meant two
  descriptions of one thing that could drift apart with nothing to catch it. Read the
  script. The four Khmer categories are defined around lines 35–48; the generation prompt
  and `MODEL_LADDER` sit near line 363.
- Pulse copy obeys §10–§13 exactly as articles do. The generator rejects a response
  containing foreign script rather than publishing it (§13).
- **[REGRESSION] `EXCLUDE_REGEX` terms must match their inflections.** The list mixes
  singular and plural entries and compiles as `\b(term|term|…)\b`, so any other form
  slipped past: `summer roll` is on the list and "Mango Chicken **Summer Rolls**"
  published anyway — Vietnamese, which §15 excludes on explicit geopolitical grounds.
  Seven of nine probe titles evaded this way, in both directions (`taco` missing "Tacos",
  `waffles` missing "Waffle"). `_with_inflections()` now stems each term and matches an
  optional -s/-es. When adding a term, add the base form; do not hand-write both.
  Verified after the change: 0 of 15 on-brand titles wrongly blocked, and across 109 live
  feed titles only 3 newly filtered — two Japanese okonomiyaki, correctly, and one
  Chinese corn pancake, which was added to `ALLOW_REGEX`.
- **[REGRESSION] An instruction in the prompt is a request; only a gate is a standard.**
  The prompt asks for "exactly 4 sections, each with its own descriptive Khmer
  subheading". Nothing checked it, and measured 2026-08-15 across the six entries
  generated since the prompt was rewritten, only ONE carried four subheadings — the other
  five were flat walls of text that passed every check and published. Length and script
  purity were gated and are honoured; structure was not gated and was not. `MIN_CONTENT_SECTIONS`
  now rejects and retries, feeding the specific reason back to the model. Anything the
  output MUST have needs a gate, or it holds only when the model feels like it.
- **Pulse quality is now the site's quality.** The blog is frozen at 15 articles; pulse
  grows by one a day, so it passes 90% of the site's pages within a year. Judge a change
  to the generator by what 400 entries of it will look like, not by the next one.
- Every pulse page already links to three blog articles, chosen by real term overlap with
  two slots and a rotating third (`pulse/[id].astro`). Measured: all 15 blog articles are
  reached, 4 inbound links minimum, 168 total. Do not "fix" this by adding in-body links —
  the distribution is deliberate, and the rotating slot exists because pure relevance
  ranking gave one article 14 inbound links and another none.
- **[REGRESSION] Candidate fallback loop prevents pipeline stalls.** If Gemini fails all
  attempts on a single candidate dish (e.g. non-culinary anomaly, edge-case term collision),
  `fetch_catering_pulse.py` buffers up to 3 live candidates and tries the next dish instead
  of immediately failing the GitHub Actions workflow run. Dormant feeds must be pruned if
  they are hijacked with non-culinary spam.

## 16. Secrets

**The agent is responsible for not exposing secrets. The user should never have to think
about it.** Assume the user will say "the token is in `.env`" and nothing more — that is
correct and sufficient. Never ask them to paste a value.

### Reading a secret

Pipe it into an environment variable. It must never reach stdout.

```bash
export GH_TOKEN=$(grep '^GITHUB_PAT=' .env | cut -d= -f2- | tr -d '\r\n"')
curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/...
```

### **[REGRESSION] Mask before printing anything that can carry a credential**

A live `ghp_…` PAT was embedded in the git remote URL. A plain `git remote -v` printed it
in full into the transcript. The user had not pasted anything — the leak came entirely
from an unmasked diagnostic command.

Commands that require masking, always:

| Instead of | Use |
| :--- | :--- |
| `git remote -v` | `git remote -v \| sed 's#//[^@]*@#//<hidden>@#'` |
| `git config -l` | `git config -l \| sed 's/=.*token.*/=<hidden>/I'` |
| `cat .env` | `sed 's/=.*/=<hidden>/' .env` |
| `env` / `printenv` | never dump wholesale; read one named variable |

Before running any command that prints a URL, a config file, or an environment, ask
whether it could contain a credential. If it could, mask it.

### Storage

The rule used to read "one secret, one home", immediately followed by "Local: `.env`.
CI: GitHub Actions secrets" — two homes. That was self-contradictory and is replaced by:

> **A credential lives only where it is genuinely needed, with only the power it needs
> there. Everywhere else, it must not exist.**

Two consequences, applied in order:

1. **Delete unnecessary copies.** A copy that nothing reads is pure risk at zero benefit.
   This is what the original rule was reaching for: the leaked PAT was in `.env` *and*
   `.git/config` on the same machine for the same purpose, and the redundant one leaked.
2. **Downgrade the necessary ones.** A copy that cannot be deleted should be able to do
   as little as possible. Splitting a credential in two is worthless unless the second is
   strictly weaker — the point is least privilege, not the split.

The gain from (2) is not fewer copies, it is: a lower damage ceiling if one leaks,
revocation that does not break the other environment (so it actually happens promptly),
and knowing which environment leaked when a key is abused.

**"Not currently in use" and "not needed" are the same risk.** A credential that is used
a few times a year should be created when needed, given an expiry, and revoked after —
not parked in `.env` between uses.

### Which copies are justified — audit, do not assume

Run this before claiming any credential is needed:

```bash
grep -rhoE "os\.(getenv|environ(\.get)?)\(\s*[\"'][A-Z_0-9]+[\"']" devops/ src/
grep -rhoE "(process\.env|import\.meta\.env)\.[A-Z_0-9]+" src/ devops/
grep -rhoE "secrets\.[A-Z_0-9]+" .github/workflows/
```

Audited 2026-08-14:

| Credential | Read by | Home |
| :--- | :--- | :--- |
| `CLOUDFLARE_API_TOKEN` | CI: `notify_indexing.py` (purge only). Local: `apply_cf_settings.py`, `cloudflare_audit.js` | CI only, scoped to **Cache Purge**. Local WAF work goes through the dashboard |
| `GEMINI_API_KEY` | `fetch_catering_pulse.py`, run by CI | GitHub Actions secrets |
| `GSC_SERVICE_ACCOUNT_JSON` | CI, written transiently to `google_service_account.json` and deleted in the same step | GitHub Actions secrets |
| `google_service_account.json` | Local: `gsc_query_report.py` | Local only. Should be a **read-only** (`webmasters.readonly`) service account, separate from the CI one that can submit indexing |
| `GSC_GA4_SERVICE_ACCOUNT_EMAIL` | **nothing** — re-audited 2026-08-17. Both readers (`generate_analytics_report.py`, `gsc_ga4_audit.js`) were deleted in `6292696`; `git grep` outside `*.md` returns zero hits | **Delete.** Not a secret — an email address — but a variable nothing reads is a variable nobody maintains |
| `GSC_API_KEY` | **nothing** | **Delete.** GSC authenticates by service account, not API key |
| `GITHUB_PAT` | **nothing** | **Never store.** CI uses `secrets.GITHUB_TOKEN`; local pushes use the OS credential manager |

### Google Cloud project surface

The project `just-turbine-503117-k9` exists for one purpose. The whole repository calls
exactly two Google endpoints — verified 2026-08-14:

**[REGRESSION] The account this paragraph used to name — `gsc-and-ga4@just-turbine-…` —
no longer exists.** It was deleted on 2026-08-15 over a leak concern and replaced by two,
split by privilege. A rule file that names a deleted account is the "confidently wrong
rule" section 0 warns about, so the current pair is written down here instead:

| Account | Scope | Used by |
| :--- | :--- | :--- |
| `ckm-indexing@just-turbine-503117-k9` | `auth/webmasters` (write) | CI only, via `SEARCH_CONSOLE_SA_JSON`, to resubmit the sitemap |
| `ckm-analytics@just-turbine-503117-k9` | `webmasters.readonly` + `analytics.readonly` | local `google_service_account.json`, for `gsc_query_report.py` |

This satisfies the split the table above asks for: the local key is read-only and cannot
submit indexing. Verified 2026-08-16 — the local key resubmitting a sitemap returns 403,
while `gsc_query_report.py` returns live data.

```bash
grep -rhoE "https://[a-z0-9.-]*googleapis\.com/[a-zA-Z0-9/._-]*" --include=*.py --include=*.js devops/ | sort -u
#   https://www.googleapis.com/webmasters/v3/…          -> Search Console
#   https://generativelanguage.googleapis.com/…         -> Gemini (AI Studio key, different project)
```

**Grade by damage, not by usage.** "Nothing calls it" is a weak reason on its own — the
question is what a leaked key could do through that API. Disabling something harmless is
churn, and worse, it dilutes the recommendations that matter:

| Tier | Examples | Worst case if a key leaks | Action |
| :--- | :--- | :--- | :--- |
| **Billable / storage** | BigQuery (×7), Cloud SQL, Cloud Storage (×3) | Someone else's compute and file hosting on your invoice | **Disable** |
| Read-only, not billable | Google Analytics Data / Admin API | Someone reads your traffic numbers | Either state is fine — not a security decision |
| Infrastructure | Service Usage, Service Management, Telemetry, Logging, Monitoring, Trace | Nothing | **Keep.** Disabling Service Usage can lock you out of the enable/disable controls themselves |
| In use | Google Search Console API (56 requests) | — | **Keep** — the only API anything here calls |

State as of 2026-08-14: everything in the billable tier is disabled, along with Analytics
Hub, Dataplex, Dataform and Datastore. The GA4 pair is also disabled, which was optional.

Disabling an API does **not** revoke IAM roles; the service account's roles are still the
primary control. It is a cheap second layer for the billable tier and close to pointless
for the rest. Re-enabling is one click.

- **[REGRESSION] A scoped token is not automatically a small one.** The single
  `CLOUDFLARE_API_TOKEN` also carried `PUT /rulesets/phases/…/entrypoint`, i.e. the power
  to rewrite the zone's entire WAF, rate-limit and cache rulesets — while CI used it only
  to purge cache. Verify what a token can do, not just that it is scoped:

  ```bash
  export CF_TOKEN=$(grep '^CLOUDFLARE_API_TOKEN=' .env | cut -d= -f2- | tr -d '\r\n"')
  curl -s https://api.cloudflare.com/client/v4/user/tokens/verify \
    -H "Authorization: Bearer $CF_TOKEN"
  ```

- **[REGRESSION] `devops/apply_cf_settings.py` replaces rulesets, it does not add to
  them.** Each `put_ruleset_phase()` is a `PUT` on the phase entrypoint, and each phase in
  that file holds exactly one rule. Running it silently deletes every rule added through
  the dashboard since it was last edited. Change Cloudflare settings in the dashboard;
  treat that file as a record of intent, not a tool.
- The repository is **public**. `.env` and `google_service_account.json` are gitignored and
  have never been committed (verified across all refs, 2026-08-14). No workflow uses
  `pull_request` or `pull_request_target`, so fork PRs cannot reach the secrets — do not
  add such a trigger.
- **GitHub Actions secrets are write-only and cannot be read back**, not by the API, the
  `gh` CLI, or an agent. To use a CI-only secret, move the *work* into a workflow; there is
  no way to move the *value* out.
- Anyone who can push a workflow to this repo can exfiltrate every secret in it (masking
  only matches the raw string; base64 defeats it). Repo write access **is** secret access.
- Never write a live token into `WORKLOG.md`, this file, or any tracked file.
  `devops/check_content.py` scans for common credential patterns and fails on a hit.

### If a secret is exposed anyway

Say so immediately and plainly, establish the blast radius before advising
(tracked files? git history? remote?), then clean every local copy. Revoking and issuing
credentials is the user's action — never do it for them, and never enter credentials.

## 17. Formatting

- Break Khmer paragraphs at sensible lengths; single lines beyond ~300 multi-byte
  characters stall editor word-wrap engines.
- Markdown tables must use explicit alignment delimiters (`| :--- |`) — linters can
  backtrack catastrophically on multi-byte cells without them.
- Blank line before and after every heading, list and fenced block. No consecutive blank
  lines. Exactly one trailing newline.

## 18. Search demand — measured, not assumed

**Read this before proposing any SEO work.** Every number below was pulled live on
2026-08-14 and is reproducible:

```bash
python devops/gsc_query_report.py --days 90
```

- **`devops/gsc_query_report.py` is the only trustworthy analytics script.** It exits
  non-zero on an API failure, so a caller can never mistake a placeholder for a
  measurement. Raw output lands in `devops/reports/gsc_search_queries.json`.
- **[REGRESSION] Never rebuild `devops/generate_analytics_report.py`.** The script was
  deleted in `6292696` ("delete the fabricated analytics scripts and their output") and
  verified gone on 2026-08-17; this rule records *why*, so nobody writes it again. It fell
  back to hardcoded numbers (`35` clicks / `1369` impressions / `2.56%` / `6.43`) that were
  indistinguishable from live output in the file it wrote, and its "關鍵字亮點" section was
  hardcoded prose **not** derived from the data it had just fetched. It called
  rank-1-with-zero-clicks a success. Any replacement must exit non-zero on API failure
  rather than degrade to a plausible-looking placeholder.
- **Always filter to `country = khm`.** Taiwan and US rows are the owner's own team and
  crawlers. Unfiltered totals overstate reach by roughly 25%.

### [REGRESSION] The analytics tag is not in this repository — verify it in a browser

**The transferable rule, and the one that caught the change below: front-end injection
must be verified in a real browser.** Cloudflare injects at the edge, so `git grep` finds
nothing (the tag was never in the source) *and* `curl` finds nothing (injection is skipped
for non-browser user agents). Two independent negatives, both wrong, both easy to mistake
for "this site has no analytics". Load the page in a browser and read `window` and
`document.cookie`.

**What is true as of 2026-08-22: Cloudflare Web Analytics only.** The owner switched
Cloudflare Zaraz and its GA4 tool off in the dashboard that day, across all four of their
sites. Verified the same day in a real browser on `ckmkh.com`:

| Check | Result |
| :--- | :--- |
| `window.zaraz` | `undefined` |
| `window.dataLayer` | `undefined` |
| `document.cookie` | empty |
| third-party scripts | `static.cloudflareinsights.com/beacon.min.js`, and nothing else |

Consequences that other rules depend on:

- **Measurement is cookieless and stores nothing on the visitor's device**, so no consent
  banner is required. `src/pages/privacy.astro` was corrected the same day to say so; it
  had described a consent banner that has never existed in this repo. If anything is ever
  added that does set a cookie, that page stops being true.
- **No GA4 collection after 2026-08-22.** The property (`534450350`) and the
  `ckm-analytics@` reader still exist and whatever they hold ends on that date; it does
  not grow. Whether the Data API still answers is a separate question — §16 records the
  GA4 API pair as disabled in the Google Cloud project since 2026-08-14 — so check before
  claiming either way. Either way, do not present GA4 output as current traffic.
- **Do not "fix" the missing tag by adding `gtag.js` to `Layout.astro`.** GA4 was removed
  deliberately; re-adding it by hand would reinstate the tool the owner turned off, put
  back the cookie the privacy page now says is absent, and ship a payload larger than the
  19 KB §4 rejected Lenis over. Analytics on this site is a dashboard decision, not a
  `Layout.astro` edit.

### Frozen GA4-era baseline — 90 days to 2026-08-14

The reference point for whether distribution work is doing anything. 150 sessions,
102 users, 1,322 page views. **This table is history, not a live report** — GA4 stopped
collecting on 2026-08-22 (above), so it can never be extended and there is no "same
measurement, later" to compare against. Cloudflare Web Analytics does not model sessions
and users the way GA4 did, so a number taken from it is not a continuation of this series.
Treat 2026-08-22 as a hard break: keep the table for what it establishes about the
starting point, and state the source and date of any later figure rather than setting it
beside these.

| Channel | Sessions | | Country | Sessions |
| :--- | ---: | :--- | :--- | ---: |
| Direct | 87 | | Taiwan (the team) | 50 |
| Organic Search | 61 | | **Cambodia** | **47** |
| Referral | 2 | | United States (crawlers) | 35 |
| **Social** | **0** | | everything else | 18 |

- **Facebook referral is zero.** Not small — none.
- **Direct is 58% and unattributable.** Telegram strips the referrer, so Telegram clicks
  land here alongside the team's own visits. Tag every posted link with
  `?utm_source=facebook|telegram&utm_medium=social&utm_campaign=<date-or-topic>` from the
  first post — traffic that arrives untagged can never be separated retroactively.
- **8.8 page views per session is not human behaviour** for a catering enquiry. After the
  team's own visits and crawlers, the count of real prospects is single digits, not 47.
  Treat that as calibration, not failure: the site is not underperforming, it is unknown.

**Behavioural metrics were never worth reading here, which is most of why losing GA4
costs little.** Engagement time, bounce rate and scroll depth are *distributions* and need
a sample; most articles take 0 clicks per quarter, so those numbers describe the one
visitor, not the page. Revisit that argument somewhere north of 1,000 sessions per month;
the site is at roughly 15. The one thing that does stay meaningful at any volume is
discrete events — how many people tapped the Telegram or phone CTA — and the current
setup does not report them. Nothing was lost, because they were never instrumented; but
do not claim conversion data the site does not collect, and if the owner ever wants it,
weigh it against the cookieless, banner-free position just gained.

### Measured demand, Cambodia only, 2026-05-15 → 2026-08-12

| Query | Impressions | Clicks | Position | Verdict |
| :--- | ---: | ---: | ---: | :--- |
| `ម្ហូបការ` | 240 | 11 | 3.95 | The only term with real buying intent and clicks |
| `ចុងភៅ` | 153 | 0 | 7.59 | Image intent — do not target |
| `រូបចុងភៅ` | 68 | 0 | 6.46 | Image intent — do not target |
| `មុខម្ហូបការ` | 60 | 2 | 5.23 | Secondary, real |
| `ម៉ឺនុយ` | 48 | 0 | 5.52 | Generic-term intent mismatch — do not target |
| `catering service in phnom penh` | 31 | 0 | **1.00** | Rank 1, zero clicks — local pack owns the fold |

- **The `ចុងភៅ` cluster is a trap.** `ចុងភៅ` + `រូបចុងភៅ` + `រូបភាពចុងភៅ` + `logo ចុងភៅ`
  total ~240 impressions and **0 clicks**. Those searchers want chef photos and logo
  assets, not catering. The cluster also collapsed to 5 impressions in the last 28 days.
- **`ម៉ឺនុយ` is not a catering query.** `/blog/01-traditional-8-course-wedding-menu/`
  has an exactly-matching title (`ម៉ឺនុយម្ហូបការ ៨ មុខ…`), ranks 5.52, and took 0 clicks
  from 48 impressions. A perfect keyword match that never gets clicked is an intent
  mismatch, not an optimisation problem.
- **Coverage is not the constraint.** 15 articles produce ~150 impressions per 90 days
  combined. Writing article 16 has an expected value of ~10 impressions per quarter.
  Do not propose "more content" as an SEO fix.
- **Rankings are not the constraint either.** `ម្ហូបការ` sits at position 2.66 over the
  last 28 days. The ceiling on this channel is total demand — roughly 300 commercial
  impressions per 90 days — not placement.
- **[REGRESSION] Non-Cambodian clicks are not signal.** A prior report highlighted
  `/blog/07-housewarming-catering-setup/` at "20% CTR". Filtered to Cambodia that page is
  1 impression and 0 clicks; the clicks came from Taiwan, i.e. the team itself.

### Homepage title and description

`src/pages/index.astro` line ~78. Rewritten 2026-08-14 from measured data — do not
"optimise" it back:

- **Keyword first, brand last.** The title used to open with `ចេង គួងម៉េង (CKM)`, spending
  the most valuable characters in the SERP on a name nobody searches. Ordering is now
  `សេវាកម្មម្ហូបការ ភ្នំពេញ | មុខម្ហូបការមង្គលការ | ចេង គួងម៉េង (CKM)` so that truncation
  eats the brand, not the term.
- **`ចុងភៅ` was removed from the title on purpose.** See the cluster note above.
- **[REGRESSION] Keep any `description` at or under 155 characters.** `Layout.astro`
  slices at 152 and appends `...`. The homepage description was 195 characters and shipped
  to the SERP cut mid-word (`…កូនជ្រូកខ្វៃ ស៊ុ...`) on the highest-impression page on the
  site. All 15 blog descriptions are currently under the limit — verified, keep it that way.
- `title` also feeds `og:title` and the breadcrumb JSON-LD, so it is the Facebook share
  headline too. Changing it changes both.

## 19. External backlinks — dropped, and why

**Decision, 2026-08-14: this site does not pursue backlinks. Do not restart it, and do not
propose it as an SEO fix.** `.agents/skills/ckm_backlink_writer/SKILL.md` and
`Docs/backlink_ledger.md` were deleted; the three ledger entries were all 待發佈 with no
live URL, so nothing was sunk. The reasoning is recorded here so it is not re-derived.

Four independent reasons, any one of which is sufficient:

1. **There is no ranking gap for a link to close.** `ម្ហូបការ` sits at position 2.66 over
   the last 28 days (§18). Links push rankings; the ranking is already there.
2. **Demand caps the channel, not placement.** Roughly 300 commercial impressions per 90
   days in Khmer search. Perfect rankings across every term is on the order of 50 clicks a
   quarter. No amount of link building creates searches that nobody performs.
3. **The links carry no signal.** Medium and Substack are understood to mark outbound
   links `rel="nofollow"`, and `*.blogspot.com` carries near-zero authority. The nofollow
   claim was **not verified from source** — both platforms blocked a scripted fetch — so
   treat it as unconfirmed, which is itself a reason not to build a plan on it.
4. **No distribution value either.** Neither platform has meaningful Cambodian readership.
   Khmer content posted there is read by nobody, so it does not even work as marketing
   independent of SEO.

**[REGRESSION] Verify a keyword against `gsc_query_report.py` before targeting it.** Ledger
entry 002 targeted `ចុងភៅនៅភ្នំពេញ`, recorded in `WORKLOG.md` as a "GSC/Bing high-impression
query". Measured: **1 impression in 90 days**, and its parent term is the zero-click image
cluster in §18. The whole plan rested on a number nobody had checked.

### When the tactic would be right — for a different project

The technique is not universally worthless; it was wrong *here*. Posting to Medium or
Substack works when the audience genuinely reads those platforms — English-language B2B,
SaaS, developer tooling. The value then comes from readers seeing the piece, not from the
link passing authority. If a future project has that audience, apply that reasoning rather
than resurrecting the deleted skill.

### What reaches this market instead

- **Google Business Profile.** Reviews are local SEO's equivalent of links, and GBP is what
  wins the local pack currently absorbing the rank-1, zero-click
  `catering service in phnom penh` result.
- **Facebook.** Referral is **0** (§18 baseline). This is the largest gap and the one that
  does not depend on Google at all. Tag every posted link with UTM parameters from the
  first post — untagged traffic lands in Direct and can never be separated afterwards.
- **Telegram.** The site's CTAs already point there; nothing circulates on it.

## 20. Communication

**Moved to the global rule file on 2026-08-17.** This section said: ground every diagnosis
in a file, a line, a measurement or a log rather than in plausibility; state what was
verified and what was assumed; say so when a check was not run; report failures plainly,
including your own. All four are now in `~/.agents/GLOBAL.md` §2 (誠實) and §3 (驗證優先
於推理), which every agent tool loads from its own global config path. Keeping a second
copy here only creates a place for the two to drift apart.

§0's "verify with a different mechanism than the one that made the change" was promoted
to the global file in the same pass — it generalises beyond this project, and the incident
it cites happened on Sunder.

## 21. Facebook Page — zero-link Khmer image-and-copy programme

Decision 2026-08-19 (owner directive): CKM's social channel is the Facebook Page
(粉絲團), run as image + copy posts in Khmer. Goals are reach and follower
accumulation on-platform; no traffic funneling.

- **Zero links in posts.** No URLs, no "search for X" hints; the Page name and
  profile are the brand asset. Consistent with §19 (backlinks dropped).
- **Every post ships as a triple**: (1) Khmer copy — native, colloquial,
  pain-point or interest-first for wedding/banquet audiences; (2) zh-TW
  line-by-line translation for owner review before publishing; (3) an English
  image-generation prompt (luxury banquet food / table-setting close-ups).
- **Engagement without bait**: invite comments through genuine questions or
  useful specifics (menus, seasonal dishes, planning tips) — Meta demotes
  explicit engagement bait. Khmer-only on the public side, per §2.
- **Execution engine**: the project skill `.agents/skills/ckm-seo/`
  (2026-08-20, moved in-project from the retired user-level engine). This file
  overrides the skill where they conflict; see §0 Skills policy for the boundary.

## 22. Tooling lives in `devops/`

Renamed from `scripts/` on 2026-08-20. Every workflow, `package.json`, this file, `Docs/`
and the two `public/llms*.txt` generator lines were updated in the same pass; `WORKLOG.md`
keeps its historical `scripts/` references on purpose.

- **Every tool in `devops/` is tracked, and `devops/` is never gitignored wholesale.** CI
  invokes them out of the checkout, from the repo root — no workflow step sets
  `working-directory`, so CWD-relative constants inside the scripts survive the rename.
- **Exactly two subfolders are ignored**: `devops/local/` (one-off scratch — the three
  retired pulse seeders moved there) and `devops/reports/` (generated output: audit JSON,
  the GSC raw dump, the width table, screenshots).
- Broader one-off exploration still lives in `scratch/`, which is ignored wholesale.
- `devops/README.md` lists every tool, its purpose, and how it is invoked.

## 23. Multi-Account Git & GitHub Deployment Protocol

This machine manages four isolated client identities (`CKM`, `Sunder`, `TWProbe`, `PressaGen`).
To prevent identity graph cross-contamination, all Git operations enforce strict per-account
isolation.

### Identity Mapping

| Project | GitHub Account | SSH Host Alias | Key Path |
| :--- | :--- | :--- | :--- |
| **CKM** | `chengkoungmeng-hue` | `github.com-chengkoungmeng` | `~/.ssh/id_ed25519_chengkoungmeng` |
| **Sunder** | `sundermou-ship-it` | `github.com-sundermou` | `~/.ssh/id_ed25519_sundermou` |
| **TWProbe** | `TWProbe` | `github.com-twprobe` | `~/.ssh/id_ed25519_twprobe` |
| **PressaGen** | `pressagencom-svg` / `PressaGen-me` | `github.com-pressagen` | `~/.ssh/id_ed25519_pressagen` |

### Non-Interactive Shell Rules for AI Agents

1. **Git Remote & Push**: Remote URL is `git@github.com-chengkoungmeng:chengkoungmeng-hue/CKM.git`.
   In non-interactive background subshells on Windows, pass `BatchMode=yes` to avoid SSH prompt hangs:
   `git -c core.sshCommand="ssh -o BatchMode=yes" push origin <branch>`
2. **GitHub CLI (`gh`) Operations**: Before creating/merging PRs or calling GitHub APIs:
   `gh auth switch --hostname github.com --user chengkoungmeng-hue`

</RULE[project_scoped]>

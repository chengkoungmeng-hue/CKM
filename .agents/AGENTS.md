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
- Run `python scripts/check_content.py` before committing content. It enforces the
  mechanical half of this file in under a second.
- **This project has no skills.** `.agents/skills/` was removed on 2026-08-14. The five
  that existed either duplicated this file (`ckm_blog_writer`, `ckm_pulse_writer`),
  restated a spec that actually lives in code (`ckm_pulse_writer` again), or were generic
  audit checklists that would generate plausible findings untethered from the measured
  data in §18 (`local_seo_analyzer`, `audience_analyzer`). `ckm_backlink_writer` described
  a programme this project has decided not to run — see §19. Everything worth keeping was
  merged into this file. **Do not recreate them.** A skill is instructions an agent
  executes, so a stale one is more dangerous than a stale document.
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
- `scripts/check_content.py` fails the build on any Thai / Devanagari / CJK / Kana
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
  Articles 02, 03, 04, 10, 11 and 12 shipped with the conclusion *before* the FAQ, so the
  last thing a reader saw was an administrative note. The conclusion sits closest to the
  CTA; it belongs where the reader is ready to act.
- **[REGRESSION] At least 3 in-context links to other `/blog/` articles per post.**
  Articles 13, 14 and 15 shipped with **zero** internal links — no site authority reaches
  them and no reader continues from them. Anchor text describes the destination, never
  "click here"; the URL **must** end in a slash or §3's redirect penalty applies.

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
- **`verify_live_url` and `extract_image_multitier` run on the SELECTED item only.** Both
  used to run for every candidate during the fetch — up to two extra HTTP requests each,
  ~188 per run to publish one article — and both are only ever needed for the one item
  that gets published. Moving them to selection time is what makes walking the archives
  affordable. Selection walks down the sorted queue until a URL resolves, so one dead link
  costs the next-best article rather than the whole day.
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
- **The prompt and the category taxonomy live in `scripts/fetch_catering_pulse.py`, not in
  documentation.** The retired `ckm_pulse_writer` skill restated both, which meant two
  descriptions of one thing that could drift apart with nothing to catch it. Read the
  script. The four Khmer categories are defined around lines 35–48; the generation prompt
  and `MODEL_LADDER` sit near line 363.
- Pulse copy obeys §10–§13 exactly as articles do. The generator rejects a response
  containing foreign script rather than publishing it (§13).

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
grep -rhoE "os\.(getenv|environ(\.get)?)\(\s*[\"'][A-Z_0-9]+[\"']" scripts/ src/
grep -rhoE "(process\.env|import\.meta\.env)\.[A-Z_0-9]+" src/ scripts/
grep -rhoE "secrets\.[A-Z_0-9]+" .github/workflows/
```

Audited 2026-08-14:

| Credential | Read by | Home |
| :--- | :--- | :--- |
| `CLOUDFLARE_API_TOKEN` | CI: `notify_indexing.py` (purge only). Local: `apply_cf_settings.py`, `cloudflare_audit.js` | CI only, scoped to **Cache Purge**. Local WAF work goes through the dashboard |
| `GEMINI_API_KEY` | `fetch_catering_pulse.py`, run by CI | GitHub Actions secrets |
| `GSC_SERVICE_ACCOUNT_JSON` | CI, written transiently to `google_service_account.json` and deleted in the same step | GitHub Actions secrets |
| `google_service_account.json` | Local: `gsc_query_report.py` | Local only. Should be a **read-only** (`webmasters.readonly`) service account, separate from the CI one that can submit indexing |
| `GSC_GA4_SERVICE_ACCOUNT_EMAIL` | `generate_analytics_report.py`, `gsc_ga4_audit.js` | Not a secret — an email address |
| `GSC_API_KEY` | **nothing** | **Delete.** GSC authenticates by service account, not API key |
| `GITHUB_PAT` | **nothing** | **Never store.** CI uses `secrets.GITHUB_TOKEN`; local pushes use the OS credential manager |

### Google Cloud project surface

The project behind `gsc-and-ga4@just-turbine-503117-k9…` exists for one purpose. The whole
repository calls exactly two Google endpoints — verified 2026-08-14:

```bash
grep -rhoE "https://[a-z0-9.-]*googleapis\.com/[a-zA-Z0-9/._-]*" --include=*.py --include=*.js scripts/ | sort -u
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

- **[REGRESSION] `scripts/apply_cf_settings.py` replaces rulesets, it does not add to
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
  `scripts/check_content.py` scans for common credential patterns and fails on a hit.

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
python scripts/gsc_query_report.py --days 90
```

- **`scripts/gsc_query_report.py` is the only trustworthy analytics script.** It exits
  non-zero on an API failure, so a caller can never mistake a placeholder for a
  measurement. Raw output lands in `scripts/reports/gsc_search_queries.json`.
- **[REGRESSION] Do not trust `scripts/generate_analytics_report.py`.** It falls back to
  hardcoded numbers (`35` clicks / `1369` impressions / `2.56%` / `6.43`) that are
  indistinguishable from live output in the file it writes, and its "關鍵字亮點" section
  is hardcoded prose that is **not** derived from the data it just fetched. It called
  rank-1-with-zero-clicks a success.
- **Always filter to `country = khm`.** Taiwan and US rows are the owner's own team and
  crawlers. Unfiltered totals overstate reach by roughly 25%.

### [REGRESSION] GA4 is installed, and not in this repository

**Grepping the source for `gtag` / `googletagmanager` finds nothing, and concluding "this
site has no analytics" is wrong.** GA4 is injected by **Cloudflare Zaraz**, configured in
the Cloudflare dashboard — outside the repo, invisible to any code search.

Worse, `curl https://ckmkh.com/` also finds nothing: Cloudflare skips Zaraz injection for
non-browser user agents. Verify with a browser UA, which returns ~22 `zaraz` references:

```bash
curl -s https://ckmkh.com/ -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" | grep -c zaraz
```

Zaraz is also the right answer to the weight objection — §4 removed Lenis over 19 KB, and
`gtag.js` is larger than that. Zaraz loads third-party tools at the edge instead. Do not
"fix" the missing tag by adding `gtag.js` to `Layout.astro`; that would double-count every
page view and add the payload Zaraz exists to avoid.

**GA4 is readable programmatically.** `ckm-analytics@` holds Viewer on property
`534450350`, so `analyticsdata.googleapis.com/v1beta/properties/534450350:runReport`
works with `google_service_account.json` and the `analytics.readonly` scope. Enabling the
Data API alone is not enough — that grants the endpoint, not the data; without the
property grant it returns 403.

### Baseline before any Facebook activity — 90 days to 2026-08-14

The reference point for whether distribution work is doing anything. 150 sessions,
102 users, 1,322 page views.

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

**GA4 is collecting but not worth reading yet.** Engagement time, bounce rate and scroll
depth are *distributions* and need a sample; most articles take 0 clicks per quarter, so
those numbers describe the one visitor, not the page. Discrete events — how many people
tapped the Telegram or phone CTA — stay meaningful at any volume and are the only thing
worth instrumenting at current traffic. Revisit behavioural reports somewhere north of
1,000 sessions per month; the site is at roughly 15.

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

- Professional, rigorous, objective, sincere. Ground every diagnosis in a file, a line, a
  measurement or a log — not in plausibility.
- State what was verified and what was assumed. If a check was not run, say so.
- Report failures plainly, including your own.

</RULE[project_scoped]>

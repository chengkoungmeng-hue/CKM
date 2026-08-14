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
- Terminology:
  `Catering` → `សេវាកម្មម្ហូបការ` / `សេវាកម្មធ្វើម្ហូប` ·
  `VIP` → `ភ្ញៀវកិត្តិយស` ·
  `Buffet` → `អាហារប៊ូហ្វេ` ·
  `Finger food` → `អាហារសម្រន់ស្រាលៗ` ·
  `Food safety` → `អនាម័យនិងសុវត្ថិភាពម្ហូបអាហារ`
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
- `authoritySignals` render as trust badges directly under the hero. Make them carry a
  checkable fact and vary them per article; identical boilerplate across 15 posts trains
  readers to ignore the badge.

## 15. Pulse pipeline

- **[REGRESSION] URLs are permanent.** `id` and `slug` used to be reassigned from list
  position on every run, so adding one article rewrote all 20 URLs; the previous day's
  pages 404'd while `notify_indexing.py` submitted the new ones to Google and Bing.
  `id` is now monotonic (`next_pulse_id`) and `slug` never encodes position. Assign both
  once at insert; never recompute.
- Order of operations, and it is not negotiable: generate → validate → commit → **wait for
  the page to actually be live** → purge Cloudflare cache → IndexNow → GSC. The workflow
  polls the real URL; it does not sleep and hope. Never announce a URL before it resolves.
- Index only when something actually changed. `if: always()` on the indexing step meant
  daily submissions of unchanged URLs.
- Nothing in the workflow runs JavaScript. Do not reintroduce `setup-node` / `npm ci`.
- Feed sources currently produce Western and Japanese home recipes, which sit oddly under
  a Khmer-Chinese banquet brand. Prefer sources matching the brand's actual cuisine.

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

| Enabled API | Requests | Keep? |
| :--- | ---: | :--- |
| Google Search Console API | 38 | **Yes** — the only API anything here uses |
| Service Usage API, Service Management API | 0 | **Yes** — these manage other APIs; disabling can lock you out of the console's enable/disable controls |
| Cloud Logging / Monitoring / Trace / Telemetry | 0 | Harmless GCP defaults, no billing exposure |
| Google Analytics Data API / Admin API | 3 / 1 | **No code calls GA4.** Those requests were manual tests. Disable unless GA4 reporting is actually built |
| BigQuery (×7), Cloud SQL, Cloud Storage (×3) | 0 | **Disable.** Never called, and all are billable — a leaked key plus a wide IAM role turns these into someone else's compute and storage on your invoice |
| Analytics Hub, Dataplex, Dataform, Datastore | 0 | Disable — never called |

Disabling an API does **not** revoke IAM roles; the service account's roles are still the
primary control. It is a cheap second layer: even a leaked key with broad roles cannot
reach a service whose API is off. Re-enabling is one click, so the change is low-risk.

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

## 19. External backlinks

`.agents/skills/ckm_backlink_writer/SKILL.md` and `Docs/backlink_ledger.md` exist and
define a Medium / Substack / Blogger publishing flow. **As of 2026-08-14 all three ledger
entries are 待發佈 with no live URL — nothing has actually been published.**

Before extending that flow, weigh it against §18:

- Links are not this site's constraint. The money keyword already ranks 2.66; there is no
  ranking gap for a link to close, and total commercial demand caps the channel at roughly
  50 clicks per quarter under perfect execution.
- Medium and Substack are believed to mark outbound links `rel="nofollow"`, and
  `*.blogspot.com` carries near-zero authority. **This was not verified from source** —
  both platforms blocked a scripted fetch on 2026-08-14. Treat it as unconfirmed and do
  not build a plan that depends on those links passing signal.
- Neither platform has meaningful Cambodian readership, so Khmer content there has no
  distribution value either.
- **[REGRESSION] Verify a keyword against `gsc_query_report.py` before targeting it.**
  Ledger entry 002 targets `ចុងភៅនៅភ្នំពេញ`, recorded in `WORKLOG.md` as a "GSC/Bing
  high-impression query". Measured: **1 impression in 90 days**, and its parent term is
  the zero-click image cluster.
- The channels that actually reach this market are Google Business Profile (reviews are
  local SEO's link equivalent, and GBP is what wins the local pack that is eating the
  rank-1 zero-click result), Facebook — site referral is currently **0** — and Telegram.

## 20. Communication

- Professional, rigorous, objective, sincere. Ground every diagnosis in a file, a line, a
  measurement or a log — not in plausibility.
- State what was verified and what was assumed. If a check was not run, say so.
- Report failures plainly, including your own.

</RULE[project_scoped]>

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

- One secret, one home. Duplicating a value into a second location is how it leaks —
  the PAT was in `.env` *and* in `.git/config`, and only the second one leaked.
- Local: `.env` (gitignored). CI: GitHub Actions secrets. Git auth: the OS credential
  manager (`credential.helper = manager`), never a token in the remote URL.
- `GITHUB_PAT` is not needed by anything. CI uses the auto-provisioned
  `secrets.GITHUB_TOKEN`; local pushes use the credential manager.
- `google_service_account.json` is gitignored, written transiently in CI, and deleted in
  the same step.
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

## 18. Communication

- Professional, rigorous, objective, sincere. Ground every diagnosis in a file, a line, a
  measurement or a log — not in plausibility.
- State what was verified and what was assumed. If a check was not run, say so.
- Report failures plainly, including your own.

</RULE[project_scoped]>

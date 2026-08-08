# Project Agent Rules

<RULE[project_scoped]>

## Maintain Work Log and Rules

- **Work Log**: ALWAYS document significant work, decisions, and progress in `WORKLOG.md` located in the root directory.
- **Agent Rules**: When encountering important project-specific architectural decisions, recurring issues, or specific workflows, MUST document them as rules in this `.agents/AGENTS.md` file to ensure continuity and prevent repeated mistakes.

## Language Scope

- **Khmer Only**: When generating, editing, or updating content (like blog posts or webpage copy), ONLY modify the Khmer content (which is typically located at the root level of content folders, e.g., `src/content/blog/*.md` or `src/pages/index.astro`). Ignore Chinese (`zh/`) and English (`en/`) content unless the user explicitly requests otherwise.

## Architectural & Aesthetic Standards

- **Canonical Domain**: The canonical domain is exclusively `https://ckmkh.com`. Do NOT use `www.ckmkh.com` anywhere in `robots.txt`, schemas, or `baseUrl` configurations to avoid SEO canonical mismatch.
- **Quiet Luxury & Performance**: The UI must maintain a "Quiet Luxury" feel without sacrificing speed. We strictly use Astro SSG + Tailwind. Global fade-in animations are handled via a lightweight `IntersectionObserver` targeting `.reveal` classes. Do NOT introduce heavy animation libraries (like Framer Motion) unless absolutely necessary.
- **SPA Navigation**: Astro `<ClientRouter />` is enabled in the root layout. Ensure all custom client-side scripts are wrapped in `document.addEventListener("astro:page-load", ...)` instead of `DOMContentLoaded` so they re-trigger on navigation.
- **Icon System**: Strictly use `@lucide/astro` for icons. Do NOT inline raw SVGs into Astro components to maintain a clean codebase and unified stroke widths.

## Security & Secrets Management

- **Token Protection**: NEVER write active API tokens, passwords, or credentials into `WORKLOG.md`, `AGENTS.md`, or any code files committed to the repository. All secrets (e.g., Cloudflare API Tokens) must be saved exclusively in `.env`, which is strictly ignored by Git.

## Font Strategy

- **System Fonts First**: For Khmer body text, strictly use `system-ui` fallback fonts instead of heavy Web Fonts to achieve 0 CLS and instant LCP. Use custom self-hosted fonts (like Hanuman) ONLY for large headings, and always load them locally via `public/fonts/`.

## Sub-brands SEO

- **Concentrated Domain Authority**: Sub-brands hosted on the main domain (e.g., `/tanghuot/`) that target the same demographic should remain strictly Khmer-focused. Do NOT create multilingual routes (`/zh/`, `/en/`) for them unless explicitly requested, to consolidate SEO authority.

## Local SEO & GEO Audit Protocol

- **Local Target Audience Focus**: Primary focus is local Cambodian / Phnom Penh audience (`https://ckmkh.com`). All local SEO analyses must prioritize Khmer keywords, local search intent, and regional search behavior.
- **LocalBusiness Structured Data**: Ensure all business pages embed Schema.org `LocalBusiness` / `Organization` JSON-LD with correct canonical URLs (`https://ckmkh.com`), GEO coordinates, address, and localized NAP (Name, Address, Phone).
- **GSC & GA4 Integration Safety**: Integration credentials (e.g., `GSC_GA4_SERVICE_ACCOUNT_EMAIL`) must be read strictly from `.env`. Never hardcode active secrets or credentials into code or markdown documentation.

## Target Audience & Demographic Persona Protocol

- **Audience Segmentation**: Categorize visitors based on local intent (e.g., B2B buyers, local consumers in Phnom Penh / Cambodia).
- **Resonance & Intent Analysis**: Evaluate content readability, Khmer natural phrasing, mobile UX friction, and CTA alignment for local conversions.

## Brand Palette & Aesthetic System

- **Canonical Color Tokens**: Strictly maintain the "Royal Champagne & Onyx" Quiet Luxury palette (`#0B0F17` Onyx, `#FAF9F6` Pearl, `#D4AF37` / `#C5A059` Champagne Gold). Avoid raw primary colors (plain red, plain blue, plain green) to preserve the 60-year VIP banquet prestige.

## Brand Tone & Content Strategy (業主偏好與品牌口吻指引)

- **Humble & Respectful Tone (溫和謙遜口吻)**: Public web copy must strictly embody a humble, sincere, and respectful tone reflecting the 60-year brand legacy of CKM Catering in Phnom Penh.
  - Reader Honorific: Always use **"លោកអ្នក"** (Respected Visitor/You), never use plain "អ្នក".
  - Team Self-Reference: Always use **"យើងខ្ញុំ"** (We / CKM Team).
  - Zero Hype Mandate: Strictly ban hype words like "第一", "最強", "神級", "無敵".
- **Minimal Technical Data Rule (少用具體數據與硬規格)**: Public website copy must avoid dense numbers, hard temperature ranges (e.g., NO "4°C-60°C"), or electrical specs (e.g., NO "50-100 KVA"). Describe meticulous care, food freshness, hygiene protection, and VIP guest comfort qualitatively in warm Khmer phrasing. Reserve specific numerical data, exact figures, and technical quotes for the owner to introduce directly to clients during Telegram or phone consultation.
- **Pure Khmer Copy Standard**: All public-facing content (Blog, Pulse, Service cards) must be written in 100% Traditional Khmer (`km-KH`). Do NOT attach inline English or Chinese translations in parentheses.
- **Cambodian Cultural Respect & Local Logistics**:
  - Respect for Elders (មេបា / ចាស់ទុំ): Banquet content must emphasize honoring family elders' tastes (traditional soups, soft textures, low sugar) alongside modern preferences.
  - Climate Realities (រដូវប្រាំង / រដូវវស្សា): Outdoor/tent banquet advice must address dry season heat management vs. wet season rain protection.
  - Local Practicalities: FAQ copy must address real-world Phnom Penh concerns (Borey security approval បុរី, parking coordination, customized package consultation).
- **Promotional Boundaries Mandate (嚴禁宣稱未確認之硬體、數位系統、菜色與稅務發票承諾)**: We promote the client's catering business without making unverifiable operational guarantees. Strictly forbid claims regarding:
  - High-tech/automated kitchen equipment (smart ovens, digital temperature tracking).
  - Unlimited custom fusion dishes or international fusion menus.
  - Online app booking, automated digital payments, or online plan selector apps.
  - Tax invoice / VAT invoice guarantees (never make legal tax promises on behalf of the owner; direct clients to contact team via Telegram or phone for 1-on-1 consultation).
  - Direct clients to contact the team via Telegram or phone for one-on-one consultation and personalized quotes.
- **Zero Tipping & Zero Leftover Packing Mandate (嚴禁小費、打包與低俗尷尬話題)**: Public web copy and FAQs must strictly avoid awkward, pedestrian topics that compromise VIP banquet prestige (NO tipping discussions, NO leftover packing instructions, NO cheap bargaining/discount phrasing). Focus FAQs exclusively on VIP elder care (ការគោរពចាស់ទុំ), fresh ingredient sourcing, serving timing, and venue coordination.
- **Local Khmer Image Standard (圖片 100% 柬埔寨在地化)**: All blog cover images and inline illustrations must depict authentic Cambodian / Phnom Penh banquet setups, traditional Khmer chefs, and local venue realities. Avoid Western stock photos or industrial kitchen hardware images.
- **Khmer Terminology Standards**:
  - `Catering` ➔ `សេវាកម្មធ្វើម្ហូប` or `សេវាកម្មម្ហូបការ`
  - `VIP` ➔ `ភ្ញៀវកិត្តិយស`
  - `Buffet` ➔ `អាហារប៊ូហ្វេ`
  - `Cocktail / Finger Food` ➔ `អាហារសម្រន់ស្រាលៗ`
  - `Food Hygiene / Safety` ➔ `អនាម័យនិងសុវត្ថិភាពម្ហូបអាហារ`

## Communication & Interaction Protocol

- **Tone & Persona**: All responses, reports, technical analyses, and recommendations must maintain a **Professional, Rigorous, Objective, and Sincere** (專業、嚴謹、客觀、誠懇) tone. Avoid superficial flattery, vague speculation, or unverified claims. Base every diagnostic statement and architectural recommendation strictly on empirical evidence, verifiable code logic, and real log data.

</RULE[project_scoped]>

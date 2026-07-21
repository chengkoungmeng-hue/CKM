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
</RULE[project_scoped]>


---
name: audience_analyzer
description: Analyze target audience, customer demographic profiles (Khmer market), user search intent, content resonance, and conversion friction for ckmkh.com.
---

# Target Audience & Demographic Persona Analyzer Skill

When this skill is activated, follow this step-by-step diagnostic workflow to evaluate visitor personas, market segments, and messaging resonance for the local market.

## 1. Audience Segmentation & Persona Profiling
Analyze site copy (`src/content/blog/`, `src/pages/`) to categorize customer segments:
- **Local B2B Buyers / Wholesale Clients**: Seeking bulk product availability, supplier reliability, location details, and direct contact options (Telegram / Phone / WhatsApp).
- **Local B2C Consumers (Phnom Penh & Cambodia Regions)**: Seeking product specs, Khmer descriptions, clear pricing/inquiry pathways, and fast mobile navigation.

## 2. Intent & Content Resonance Analysis
Evaluate whether landing page content matches user search intent:
- **Informational Intent**: Educational blog posts / articles targeting problem-solving keywords in Khmer.
- **Transactional / Commercial Intent**: Service & product landing pages with clear Call-to-Actions (CTAs) optimized for local messaging apps (e.g., Telegram integration, phone click-to-call).
- **Cultural & Linguistic Alignment**: Verify that content uses natural Khmer phrasing, respectful tone, and culturally relevant positioning for Cambodian users.

## 3. GA4 Demographic & UX Behavior Correlation
- Read `GSC_GA4_SERVICE_ACCOUNT_EMAIL` from `.env` when integrating GA4 API data.
- Analyze key audience indicators:
  - **Device Distribution**: Mobile vs Desktop ratio (Mobile optimizations are critical for Cambodian traffic).
  - **User Engagement & Bounce Rate**: Measure which pages hold local audience attention.
  - **Traffic Sources**: Organic Search, Direct, Social Media (Facebook/Telegram channels common in Cambodia).

## 4. Conversion Friction Audit
- Mobile Responsiveness & Touch Targets: Check if CTAs and contact buttons are easily clickable on small screens.
- Page Load Performance: Ensure system font fallback strategies (Khmer `system-ui`) and compressed images prevent page load delays for users on cellular data.

## 5. Output Deliverables
Provide a structured audience report containing:
- **Target Persona Profiles (B2B vs B2C)**
- **Content-to-Intent Alignment Matrix**
- **Mobile UX & Friction Analysis**
- **Actionable Content & Messaging Optimization Strategy**

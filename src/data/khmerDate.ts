// Khmer date formatting for the /pulse/ surfaces.
//
// [REGRESSION] The date was formatted inline in four templates as
//     (item.added_at || item.pub_date).split(' ').slice(1, 4).join('.')
// which turns the stored RFC 2822 stamp "Sat, 22 Aug 2026 08:14:55 +0000" into
// "22.Aug.2026". Measured 2026-08-23 against the built dist/: an English month
// abbreviation appeared on 42 of the 66 pages. Section 10 requires public copy to
// be 100% Khmer, and check_content.py could never have caught it — the checker
// reads pulseData.json and src/content, never an .astro template, and the English
// was manufactured by the template out of a field that is legitimately English.
//
// Every one of those templates also carried a hardcoded '2026.08.08' fallback for a
// missing stamp. Section 14 records what a fabricated date cost this site once
// already: a new Date() fallback in blog/[slug].astro re-stamped 14 evergreen
// articles as published-today on every deploy, a textbook date-manipulation signal.
// The fallback here is the empty string. A missing line is inert; a confident wrong
// date is not. Measured: 26 of 37 entries have no added_at and all 37 have a
// parseable pub_date, so nothing renders blank today.

const KHMER_DIGITS = ['០', '១', '២', '៣', '៤', '៥', '៦', '៧', '៨', '៩'];

/** Latin digits to Khmer digits; everything else passes through. */
export function khmerNumerals(input: string | number): string {
  return String(input).replace(/[0-9]/g, (d) => KHMER_DIGITS[Number(d)]);
}

// A hardcoded table rather than Intl.DateTimeFormat('km-KH'), for two reasons.
// The formatter returns Khmer month names with LATIN digits, which would leave half
// the defect in place; and the site builds on Cloudflare Pages, whose ICU data
// cannot be verified from here — a runtime without the km locale would silently
// fall back to English and reintroduce exactly this bug. Twelve strings are
// deterministic everywhere.
const KHMER_MONTHS = [
  'មករា', 'កុម្ភៈ', 'មីនា', 'មេសា', 'ឧសភា', 'មិថុនា',
  'កក្កដា', 'សីហា', 'កញ្ញា', 'តុលា', 'វិច្ឆិកា', 'ធ្នូ',
];

function parseStamp(raw?: string | null): Date | null {
  if (!raw || typeof raw !== 'string') return null;
  const d = new Date(raw.trim());
  return Number.isNaN(d.getTime()) ? null : d;
}

/**
 * "Sat, 22 Aug 2026 08:14:55 +0000" -> "២២ សីហា ២០២៦". Empty string when unparseable.
 *
 * UTC getters deliberately: every stored stamp carries +0000, the build runs on
 * GitHub Actions in UTC while the owner reads the page from ICT, so local getters
 * would print two different dates for one entry depending on who built it.
 *
 * Accepts both formats the pipeline stores. Section 15 records that feeds arrive in
 * RFC 2822 from WordPress and ISO 8601 from Blogspot, and that applying one parser
 * to both silently collapsed 47 of 88 items; Date's constructor takes both.
 */
export function khmerDate(raw?: string | null): string {
  const d = parseStamp(raw);
  if (!d) return '';
  return `${khmerNumerals(d.getUTCDate())} ${KHMER_MONTHS[d.getUTCMonth()]} ${khmerNumerals(d.getUTCFullYear())}`;
}

/** ISO date for a <time datetime> attribute. Empty string when unparseable. */
export function isoDate(raw?: string | null): string {
  const d = parseStamp(raw);
  return d ? d.toISOString().slice(0, 10) : '';
}

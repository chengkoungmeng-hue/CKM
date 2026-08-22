// Turn an article's Khmer FAQ section into schema.org FAQPage entries.
//
// WHY
// ---
// Section 14 already REQUIRES every article to carry a FAQ section, and all 15 do.
// Measured 2026-08-23 against the built dist/: 40 questions across 14 articles, and
// exactly two pages on the whole site emitted FAQPage markup — the homepage and
// /tanghuot/. Forty Khmer question-and-answer pairs were sitting in the HTML with
// nothing telling a machine what they were.
//
// Be honest about what this buys. Google restricted FAQ rich results to authoritative
// government and health sites in August 2023, so this will NOT produce a rich snippet
// in Google search. What it does is make the Q&A machine-readable for the systems that
// do read it: AI assistants and answer engines lifting a direct answer, and non-Google
// engines. Section 14's ចម្លើយរហ័ស quick-answer block exists for the same reason. The
// cost is a few lines and no payload the reader downloads twice.
//
// PARSING
// -------
// The shape is fixed by section 14 and verified against all 15 files:
//     ## សំណួរដែលសួរញឹកញាប់…      (the heading carries a suffix in every article,
//                                  e.g. "…ពីអ្នកជំនាញ", so match the prefix)
//     ### ១. question text          (Khmer-numeral prefix, stripped from the name)
//     answer paragraphs…
//     ### ២. …
// The section ends at the next ## heading — which section 14 requires to be the
// conclusion — or at end of file.

export interface FaqPair {
  question: string;
  answer: string;
}

const FAQ_HEADING = 'សំណួរដែលសួរញឹកញាប់';

// A leading "១. " / "២) " style marker is presentation, not part of the question.
const LEADING_MARKER = /^[០-៩0-9]+\s*[.)។]?\s*/;

/** Strip inline markdown so the schema carries plain text, not syntax. */
function plain(md: string): string {
  return md
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')       // images
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')     // links keep their anchor text
    .replace(/[*_`]{1,3}/g, '')                  // emphasis and code marks
    .replace(/<[^>]+>/g, '')                     // stray html
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Extract the FAQ pairs from a raw markdown body. Returns [] when the article has no
 * FAQ section, no questions under it, or when the body is unavailable — the caller
 * omits the schema entirely rather than emitting an empty FAQPage, which would be a
 * claim that the page has an FAQ when it does not.
 */
export function parseFaq(body?: string | null): FaqPair[] {
  if (!body || typeof body !== 'string') return [];

  const lines = body.split('\n');
  const start = lines.findIndex(
    (l) => l.startsWith('## ') && l.includes(FAQ_HEADING),
  );
  if (start === -1) return [];

  let end = lines.length;
  for (let i = start + 1; i < lines.length; i++) {
    if (lines[i].startsWith('## ')) {
      end = i;
      break;
    }
  }

  const pairs: FaqPair[] = [];
  let question: string | null = null;
  let buffer: string[] = [];

  const flush = () => {
    if (question) {
      const answer = plain(buffer.join(' '));
      // A question with no answer is not an FAQ entry. Skip it rather than emit a
      // pair with an empty acceptedAnswer.
      if (answer) pairs.push({ question, answer });
    }
    question = null;
    buffer = [];
  };

  for (let i = start + 1; i < end; i++) {
    const line = lines[i];
    if (line.startsWith('### ')) {
      flush();
      question = plain(line.slice(4)).replace(LEADING_MARKER, '').trim() || null;
    } else if (question) {
      // Tables and lists inside an answer would read as noise once flattened; keep
      // prose only. Nothing in the 40 measured answers is a table today.
      if (!line.trimStart().startsWith('|')) buffer.push(line);
    }
  }
  flush();

  return pairs;
}

/** The FAQPage node, or null when there is nothing to describe. */
export function faqPageSchema(body: string | null | undefined, pageUrl: string) {
  const pairs = parseFaq(body);
  if (!pairs.length) return null;
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    '@id': `${pageUrl}#faq`,
    inLanguage: 'km-KH',
    mainEntity: pairs.map((p) => ({
      '@type': 'Question',
      name: p.question,
      acceptedAnswer: { '@type': 'Answer', text: p.answer },
    })),
  };
}

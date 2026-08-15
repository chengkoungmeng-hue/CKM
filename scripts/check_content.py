#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CKM content guard — fast, dependency-free checks for the defect classes that have
actually shipped to production on this site.

Every rule here exists because the bug it catches was found in the live repo, not
because it seemed like a good idea. Keep it that way: do not add speculative rules.

Usage:
    python scripts/check_content.py           # report only, exit 0
    python scripts/check_content.py --strict  # exit 1 on any ERROR (use in CI)

Runs in well under a second over the whole content tree.
"""

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- helpers

ERRORS = []
WARNINGS = []


def err(rule, path, line, msg):
    ERRORS.append((rule, os.path.relpath(path, ROOT).replace("\\", "/"), line, msg))


def warn(rule, path, line, msg):
    WARNINGS.append((rule, os.path.relpath(path, ROOT).replace("\\", "/"), line, msg))


def lineno(text, idx):
    return text.count("\n", 0, idx) + 1


def read(path):
    return io.open(path, encoding="utf-8").read()


# ---------------------------------------------------------------- rule 1

# Thai, Devanagari, Bengali, CJK and Kana have all been found embedded inside Khmer
# words on this site (machine-translation residue). Hanuman cannot render them, so
# they ship as tofu boxes to the exact audience the site is written for.
# Whitelist, not blacklist. An enumerated blacklist of Thai/CJK/Kana/Devanagari let
# Hebrew through, because nobody thought to list Hebrew. Allow only what this site
# legitimately contains.
ALLOWED_RANGES = [
    (0x1780, 0x17FF),   # Khmer
    (0x19E0, 0x19FF),   # Khmer symbols
    (0x0020, 0x007E),   # printable ASCII
    (0x00A0, 0x00FF),   # latin-1 supplement (é, ñ in source titles)
    (0x2000, 0x206F),   # general punctuation
    (0x2190, 0x21FF),   # arrows (used in markdown tables)
    (0x2500, 0x25FF),   # box drawing / geometric (■ bullets in prose)
]
ALLOWED_CHARS = set("\n\r\t")

_SCRIPTS = [
    (0x0E00, 0x0E7F, "Thai"), (0x0900, 0x097F, "Devanagari"),
    (0x0980, 0x09FF, "Bengali"), (0x4E00, 0x9FFF, "CJK"),
    (0x3040, 0x30FF, "Kana"), (0x0590, 0x05FF, "Hebrew"),
    (0x0600, 0x06FF, "Arabic"), (0x0400, 0x04FF, "Cyrillic"),
    (0xAC00, 0xD7AF, "Hangul"), (0x0370, 0x03FF, "Greek"),
    (0x3000, 0x303F, "CJK punctuation"),
]


def _script_name(cp):
    for lo, hi, name in _SCRIPTS:
        if lo <= cp <= hi:
            return name
    return "U+%04X" % cp


def check_foreign_scripts(path, text):
    for i, ch in enumerate(text):
        if ch in ALLOWED_CHARS:
            continue
        cp = ord(ch)
        if any(lo <= cp <= hi for lo, hi in ALLOWED_RANGES):
            continue
        ctx = text[max(0, i - 20):i + 12].replace("\n", " ")
        err("foreign-script", path, lineno(text, i),
            "%s char %r (U+%04X) in Khmer copy: ...%s..." % (_script_name(cp), ch, cp, ctx))


# Khmer is a clustered script: base consonant + optional COENG (U+17D2, the "foot") +
# subscript consonant + vowel signs + diacritics. A cluster can be malformed while every
# individual codepoint is a valid Khmer character — and it renders as a dotted circle to
# the reader. Codepoint-level checks alone will not catch it.
_CONS    = lambda c: 0x1780 <= ord(c) <= 0x17A2
_INDEP_V = lambda c: 0x17A3 <= ord(c) <= 0x17B5
_DEP_V   = lambda c: 0x17B6 <= ord(c) <= 0x17C5
_SIGN    = lambda c: 0x17C6 <= ord(c) <= 0x17D3
_COENG   = "្"


def check_khmer_clusters(path, text):
    n = len(text)
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else ""
        nxt = text[i + 1] if i + 1 < n else ""
        if ch == _COENG:
            if not nxt or not (_CONS(nxt) or _INDEP_V(nxt)):
                err("khmer-cluster", path, lineno(text, i),
                    "COENG not followed by a consonant: ...%s..." % text[max(0, i - 10):i + 8])
        elif _DEP_V(ch) or _SIGN(ch):
            if not prev or not (_CONS(prev) or prev == _COENG or _DEP_V(prev)
                                or _SIGN(prev) or _INDEP_V(prev)):
                err("khmer-cluster", path, lineno(text, i),
                    "vowel/diacritic with no base consonant: ...%s..."
                    % text[max(0, i - 10):i + 8])


# ---------------------------------------------------------------- rule 2

# Doubled Khmer words shipped in body copy and in an H2 heading. Only flag pairs
# that are never legitimate; ការការ is excluded because ការការពារ ("protection")
# is a real word and produced 4 false positives out of 5 hits.
DOUBLED = ["លោកលោក", "យើងយើង", "និងនិង", "ដែលដែល", "ការការសុំ", "ការការធ្វើ"]


def check_doubled_words(path, text):
    for w in DOUBLED:
        start = 0
        while True:
            i = text.find(w, start)
            if i < 0:
                break
            err("doubled-word", path, lineno(text, i), "repeated word %r" % w)
            start = i + 1


# ---------------------------------------------------------------- rule 3

# Known misspellings that shipped. ដើមីបី appeared 16 times across 5 files,
# including inside a meta description that renders in the Google SERP.
MISSPELLINGS = {
    "ដើមីបី": "ដើម្បី",
    "គួចៀសវាង": "គួរចៀសវាង",
}


def check_misspellings(path, text):
    for bad, good in MISSPELLINGS.items():
        i = text.find(bad)
        if i >= 0:
            err("misspelling", path, lineno(text, i), "%r should be %r" % (bad, good))


# ---------------------------------------------------------------- rule 4

# AGENTS.md bans hard technical specs in public copy — the owner supplies exact
# figures during a 1-on-1 consultation instead. Celsius tables and kVA ratings
# both slipped into published articles anyway.
HARD_SPECS = [
    (r"អង្សាសេ", "Celsius temperature spec"),
    (r"\bKVA\b|គីឡូវ៉ាត់", "electrical load spec"),
    (r"\bHACCP\b", "English technical acronym"),
]


def check_hard_specs(path, text):
    for pat, label in HARD_SPECS:
        m = re.search(pat, text)
        if m:
            warn("hard-spec", path, lineno(text, m.start()),
                 "%s — AGENTS.md reserves exact figures for direct consultation" % label)


# ---------------------------------------------------------------- rule 5

# Absolute guarantees create liability for the owner. "100% hygiene safety" and
# "no hidden costs whatsoever" both shipped and both were contradicted elsewhere
# on the same site.
ABSOLUTES = [
    (r"១០០ ?%", "absolute percentage guarantee"),
    (r"គ្មានការចំណាយលាក់កំបាំង", "absolute 'no hidden costs' claim"),
    (r"ធានា ?១០០", "absolute guarantee"),
]


def check_absolutes(path, text):
    for pat, label in ABSOLUTES:
        for m in re.finditer(pat, text):
            warn("over-promise", path, lineno(text, m.start()), label)


# ---------------------------------------------------------------- rule 6

# Article 12 embedded blog_01's inline image while its own blog_12 image sat
# unreferenced. A NN-prefixed article must reference its own NN-prefixed image.
def check_inline_image_number(path, text):
    base = os.path.basename(path)
    m = re.match(r"^(\d{2})-", base)
    if not m:
        return
    n = m.group(1)
    for im in re.finditer(r"/images/blog_(\d{2})_inline", text):
        if im.group(1) != n:
            err("wrong-inline-image", path, lineno(text, im.start()),
                "article %s references blog_%s_inline (should be blog_%s_inline)"
                % (n, im.group(1), n))


# ---------------------------------------------------------------- rule 7

# Every article needs a real date. A missing one used to make [slug].astro emit
# the BUILD date as datePublished, re-stamping evergreen posts on every deploy.
REQUIRED_FM = ["title", "seoTitle", "description", "coverImage", "date", "authoritySignals"]


def check_frontmatter(path, text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        err("frontmatter", path, 1, "missing frontmatter block")
        return
    fm = m.group(1)
    for key in REQUIRED_FM:
        if not re.search(r"^%s:" % re.escape(key), fm, re.M):
            err("frontmatter", path, 1, "missing required field %r" % key)
    cov = re.search(r"^coverImage:\s*[\"']?(.+?)[\"']?\s*$", fm, re.M)
    if cov:
        p = os.path.normpath(os.path.join(os.path.dirname(path), cov.group(1)))
        if not os.path.exists(p):
            err("frontmatter", path, 1, "coverImage does not exist: %s" % cov.group(1))


# ---------------------------------------------------------------- rule 8

# Pulse data is machine-generated and auto-committed daily with no human review,
# so it gets the same character checks plus its own structural ones.
# Only the Khmer-facing fields are script-checked. source_title_en and source_link
# legitimately carry the original foreign title (e.g. "Pickled Daikon 大根の漬物"),
# so scanning the raw file would drown real defects in false positives.
PULSE_KHMER_FIELDS = ("title_km", "summary_km", "content_km", "key_points_km",
                      "image_alt", "category")


# A live GitHub PAT once sat in .git/config's remote URL and leaked through a plain
# `git remote -v`. Nothing is currently tracked with a credential in it — this check
# exists to keep it that way, since a secret committed to history cannot be un-committed.
# Extensions whose contents cannot meaningfully hold a pasted credential. Skipped from
# the size warning below so the one text file that matters is not lost among a dozen
# oversized photographs.
BINARY_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".zip", ".gz", ".mp4", ".webm", ".mp3",
}

SECRET_PATTERNS = [
    (r"ghp_[A-Za-z0-9]{36}", "GitHub personal access token"),
    (r"github_pat_[A-Za-z0-9_]{40,}", "GitHub fine-grained token"),
    (r"gho_[A-Za-z0-9]{36}", "GitHub OAuth token"),
    (r"sk-[A-Za-z0-9]{32,}", "OpenAI-style secret key"),
    (r"AIza[A-Za-z0-9_\-]{35}", "Google API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
    (r"https://[^/\s:@]+:[^/\s@]+@", "credential embedded in a URL"),
]


def check_secrets():
    """Scan git-tracked files only. Untracked local files (.env) are the correct home
    for secrets and must not be flagged."""
    try:
        import subprocess
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                                 text=True, timeout=30).stdout.split("\n")
    except Exception:
        return
    for rel in tracked:
        rel = rel.strip()
        if not rel:
            continue
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        # Binary assets cannot carry a pasted credential in any form this scanner would
        # recognise, and there are a dozen images over the limit. Warning about those
        # would bury the one case that matters in noise.
        if os.path.splitext(rel)[1].lower() in BINARY_EXTS:
            continue
        # The size guard used to be silent, so the day a tracked TEXT file crossed 2 MB
        # it simply dropped out of the credential scan with no trace. pulseData.json
        # grows by one entry a day and reaches that size at roughly 344 entries
        # (~day 317) — the file most likely to be written by automation would have
        # stopped being checked, invisibly. Say so instead.
        if os.path.getsize(path) > 2_000_000:
            warn("secret-scan-skipped", path, 1,
                 "text file is over 2 MB and was NOT scanned for credentials")
            continue
        try:
            text = io.open(path, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for pat, label in SECRET_PATTERNS:
            m = re.search(pat, text)
            if m:
                err("secret-in-tracked-file", path, lineno(text, m.start()),
                    "%s appears in a git-tracked file — rotate it, then remove it" % label)


def check_pulse():
    p = os.path.join(ROOT, "src", "data", "pulseData.json")
    if not os.path.exists(p):
        return
    raw = read(p)
    try:
        items = json.loads(raw)
    except Exception as e:
        err("pulse", p, 1, "invalid JSON: %s" % e)
        return

    for it in items:
        ident = it.get("id", "?")

        # [REGRESSION] source_title_en is NOT a Khmer field, so it is rightly absent from
        # PULSE_KHMER_FIELDS — but pulse/[id].astro renders it verbatim on the page under
        # ប្រភពដើមអន្តរជាតិ. Feeds title posts bilingually, so "Pickled Daikon 大根の漬物"
        # and "Omurice … オムライス" shipped to Khmer readers as tofu boxes, because
        # Hanuman cannot draw CJK or kana. Anything rendered must be renderable, whatever
        # language the field nominally holds.
        src_title = it.get("source_title_en") or ""
        for i, ch in enumerate(src_title):
            cp = ord(ch)
            if cp < 0x0250 or ch in "‘’“”–—…":
                continue
            err("source-title-unrenderable", p, 1,
                "%s.source_title_en contains %s %r and is rendered on the page: ...%s..."
                % (ident, _script_name(cp), ch,
                   src_title[max(0, i - 18):i + 12]))
            break

        for field in PULSE_KHMER_FIELDS:
            v = it.get(field)
            if not v:
                continue
            for chunk in (v if isinstance(v, list) else [v]):
                if not isinstance(chunk, str):
                    continue
                for i, ch in enumerate(chunk):
                    if ch in ALLOWED_CHARS:
                        continue
                    cp = ord(ch)
                    if any(lo <= cp <= hi for lo, hi in ALLOWED_RANGES):
                        continue
                    err("foreign-script", p, 1,
                        "%s.%s contains %s %r: ...%s..."
                        % (ident, field, _script_name(cp), ch,
                           chunk[max(0, i - 18):i + 12].replace("\n", " ")))
                check_khmer_clusters(p, chunk)
    seen_slugs = {}
    for i, it in enumerate(items):
        where = "item %d (%s)" % (i, it.get("id", "?"))
        for k in ("id", "slug", "title_km", "summary_km", "category", "source_link"):
            if not it.get(k):
                err("pulse", p, 1, "%s missing %r" % (where, k))
        slug = it.get("slug")
        if slug:
            if slug in seen_slugs:
                err("pulse", p, 1, "duplicate slug %r (also item %d)" % (slug, seen_slugs[slug]))
            seen_slugs[slug] = i
        img = it.get("image_url")
        if img and img.startswith("/"):
            if not os.path.exists(os.path.join(ROOT, "public", img.lstrip("/"))):
                err("pulse", p, 1, "%s image_url not found: %s" % (where, img))
        if not it.get("image_alt"):
            warn("pulse", p, 1, "%s missing image_alt" % where)


# ---------------------------------------------------------------- rule 9

# The site is Khmer-only and the layout hardcodes baseLang="km". Any stray
# /zh/ or /en/ link in content is a guaranteed redirect or 404.
def check_dead_locale_links(path, text):
    for m in re.finditer(r"\]\((/(?:zh|en)/[^)]*)\)", text):
        err("dead-locale-link", path, lineno(text, m.start()),
            "link to removed locale route: %s" % m.group(1))


# ---------------------------------------------------------------- main

INTERNAL_LINK_FLOOR = 3
BLOG_LINK = re.compile(r"\]\((/blog/[^)]*)\)")

# AGENTS.md section 11 applies to everything published under this domain, not only to
# article bodies. public/llms.txt and llms-full.txt had drifted into exactly the claims
# the articles are forbidden to make -- "climate-controlled banquet tents", "strictly
# monitored cold-chain storage", "capable of serving 500+ guests simultaneously" -- and
# nothing checked them, because the checker only ever looked at src/content.
LLMS_FORBIDDEN = [
    (r"cold[- ]chain", "cold-chain storage claim"),
    (r"climate[- ]controlled", "climate-control equipment claim"),
    (r"air[- ]conditioned", "air-conditioning equipment claim"),
    (r"digital temperature|temperature[- ]monitor", "temperature-monitoring claim"),
    (r"\d{3,}\+?\s*guests", "hard capacity figure"),
    (r"\bVAT\b", "VAT/invoice guarantee"),
    (r"unlimited", "unlimited-customisation claim"),
    (r"\b100%\b", "absolute guarantee"),
]


def check_llms_txt():
    """The AI-facing index is public copy too, and section 11 governs it."""
    for rel in ("public/llms.txt", "public/llms-full.txt"):
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            warn("llms-missing", rel, 1,
                 "file is absent — run scripts/generate_llms_txt.py")
            continue
        text = read(path)
        for pat, label in LLMS_FORBIDDEN:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                err("llms-over-promise", rel, lineno(text, m.start()),
                    "%s — AGENTS.md 11 forbids committing the owner to this" % label)


def check_internal_links(path, text):
    """AGENTS.md section 14: at least three in-context links to other /blog/ articles.

    [REGRESSION] Articles 13, 14 and 15 shipped with ZERO. No site authority reached them
    and no reader continued from them, and nothing in the build noticed. Detecting this
    is the durable half of the fix — the nine missing links were a one-off, but an
    unchecked floor would let article 16 ship the same way.

    Deliberately a check and not an injector: Khmer has no spaces between words, so a
    keyword-matching injector has no word boundary to anchor to. Links are declared in
    src/data/internalLinks.json and applied by exact string match instead.
    """
    body = text.split("---", 2)[2] if text.startswith("---") else text
    self_slug = os.path.splitext(os.path.basename(path))[0]

    links = []
    for m in BLOG_LINK.finditer(body):
        url = m.group(1)
        line = body[:m.start()].count("\n") + 1
        # A link to the article's own URL is not an internal link out.
        if url.strip("/").endswith(self_slug):
            continue
        if not url.endswith("/"):
            err("link-missing-slash", path, line,
                "internal link %s must end in '/' or Cloudflare 301s it (AGENTS.md 3)" % url)
        links.append(url)

    if len(links) < INTERNAL_LINK_FLOOR:
        err("too-few-internal-links", path, 1,
            "%d in-context /blog/ link(s); AGENTS.md 14 requires at least %d. "
            "Declare them in src/data/internalLinks.json and run "
            "scripts/apply_internal_links.py" % (len(links), INTERNAL_LINK_FLOOR))


def main():
    strict = "--strict" in sys.argv

    articles = sorted(glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md")))
    if not articles:
        print("no articles found — wrong working directory?")
        return 1

    for path in articles:
        text = read(path)
        check_foreign_scripts(path, text)
        check_khmer_clusters(path, text)
        check_doubled_words(path, text)
        check_misspellings(path, text)
        check_hard_specs(path, text)
        check_absolutes(path, text)
        check_inline_image_number(path, text)
        check_frontmatter(path, text)
        check_dead_locale_links(path, text)
        check_internal_links(path, text)

    check_pulse()
    check_llms_txt()
    check_secrets()

    for label, items in (("ERROR", ERRORS), ("WARN", WARNINGS)):
        if not items:
            continue
        print("\n%s (%d)" % (label, len(items)))
        for rule, path, line, msg in items:
            print("  [%-20s] %s:%s  %s" % (rule, path, line, msg))

    print("\n%d articles checked | %d errors | %d warnings"
          % (len(articles), len(ERRORS), len(WARNINGS)))

    if ERRORS and strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

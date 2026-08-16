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

# Every message this script prints can contain Khmer, because the context snippet is the
# whole point of the report. A Windows console defaults to cp1252, so the script used to
# die with UnicodeEncodeError at the first finding — locally, which is exactly where
# AGENTS.md tells you to run it before committing. CI runs on Linux and never saw it.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
    # finditer, not search. This used to report only the FIRST match per pattern per
    # file, so article 04 showed one Celsius warning while carrying three, and 09 showed
    # one while carrying two plus a litre spec. Fixing the reported line just promoted
    # the next one into view — an undercount reads as "nearly clean" when it is not.
    for pat, label in HARD_SPECS:
        for m in re.finditer(pat, text):
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
    # An ERROR, not a warning, as of 2026-08-16. Section 11 marks both surviving cases
    # ([REGRESSION] `សុវត្ថិភាពអនាម័យ១០០%` and `គ្មានការចំណាយលាក់កំបាំង`) as claims that
    # already shipped once and were contradicted elsewhere on the same site. A warning
    # let them sit in the report for months. The backlog is now zero, so this can block.
    # `hard-spec` stays a warning on purpose: section 11 says "prefer omitting" there,
    # which is a judgement, while an absolute guarantee is simply forbidden.
    for pat, label in ABSOLUTES:
        for m in re.finditer(pat, text):
            err("over-promise", path, lineno(text, m.start()), label)


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


# ---------------------------------------------------------------- rule 7b

# Google truncates a search result on RENDERED WIDTH, not on character count. The
# familiar "60 characters for a title, 155 for a description" advice is a Latin proxy
# for a pixel budget, so for Khmer it has to be converted back into one.
#
# Both obvious shortcuts are wrong, and measurably so (scripts/build_width_table.cjs,
# measured 2026-08-16 in headless Chromium):
#
#   len(s)              treats every codepoint as one Latin character
#   len(s) * 2          treats Khmer like CJK, as the East-Asian-width rule would
#
# Neither holds, because two large errors run in opposite directions:
#
#   * A Khmer base consonant is roughly 1.6-2.0x a Latin character — nearly CJK-wide.
#   * 22 of the 128 Khmer codepoints have ZERO advance width. The dependent vowels and
#     diacritics (U+17B7-U+17BD, U+17C6, U+17C9-U+17D3) stack above or below the base
#     and cost nothing horizontally.
#   * A subscript consonant after COENG costs 0.113 units, not the 1.6-2.0 the same
#     consonant costs standing alone, because it stacks underneath.
#
# Averaged over the 15 live articles those errors very nearly cancel: the mean
# Khmer-codepoint-to-Latin-codepoint ratio came out at 1.03. That coincidence is
# exactly why len(s) LOOKS fine and must not be trusted -- per article the ratio ranged
# from 0.913 to 1.132, a +/-11% error in both directions on a budget whose whole
# purpose is to sit close to a hard cutoff.
#
# So the widths are measured per codepoint and baked in below. Unit: 1.0 is the average
# advance of a Latin character in the same font and size. Regenerate with
# scripts/build_width_table.cjs if the budget ever looks wrong.
#
# Caveat worth keeping in mind: this table is one font's metrics (Chromium's Khmer
# fallback at 20px). Google renders the SERP in its own font, so the table is a much
# better proxy than a codepoint count, not ground truth.
_WIDTH_RANGES = [
    (0x0020,0x0021,0.612), (0x0022,0x0022,0.783), (0x0023,0x0024,1.226), (0x0025,0x0025,1.96),
    (0x0026,0x0026,1.47), (0x0027,0x0027,0.421), (0x0028,0x0029,0.734), (0x002A,0x002A,0.858),
    (0x002B,0x002B,1.287), (0x002C,0x002C,0.612), (0x002D,0x002D,0.734), (0x002E,0x002F,0.612),
    (0x0030,0x0039,1.226), (0x003A,0x003B,0.612), (0x003C,0x003E,1.287), (0x003F,0x003F,1.226),
    (0x0040,0x0040,2.238), (0x0041,0x0042,1.47), (0x0043,0x0044,1.592), (0x0045,0x0045,1.47),
    (0x0046,0x0046,1.347), (0x0047,0x0047,1.715), (0x0048,0x0048,1.592), (0x0049,0x0049,0.612),
    (0x004A,0x004A,1.102), (0x004B,0x004B,1.47), (0x004C,0x004C,1.226), (0x004D,0x004D,1.836),
    (0x004E,0x004E,1.592), (0x004F,0x004F,1.715), (0x0050,0x0050,1.47), (0x0051,0x0051,1.715),
    (0x0052,0x0052,1.592), (0x0053,0x0053,1.47), (0x0054,0x0054,1.347), (0x0055,0x0055,1.592),
    (0x0056,0x0056,1.47), (0x0057,0x0057,2.081), (0x0058,0x0059,1.47), (0x005A,0x005A,1.347),
    (0x005B,0x005D,0.612), (0x005E,0x005E,1.034), (0x005F,0x005F,1.226), (0x0060,0x0060,0.734),
    (0x0061,0x0062,1.226), (0x0063,0x0063,1.102), (0x0064,0x0065,1.226), (0x0066,0x0066,0.612),
    (0x0067,0x0068,1.226), (0x0069,0x006A,0.49), (0x006B,0x006B,1.102), (0x006C,0x006C,0.49),
    (0x006D,0x006D,1.836), (0x006E,0x0071,1.226), (0x0072,0x0072,0.734), (0x0073,0x0073,1.102),
    (0x0074,0x0074,0.612), (0x0075,0x0075,1.226), (0x0076,0x0076,1.102), (0x0077,0x0077,1.592),
    (0x0078,0x007A,1.102), (0x007B,0x007B,0.736), (0x007C,0x007C,0.573), (0x007D,0x007D,0.736),
    (0x007E,0x007E,1.287), (0x1780,0x1780,1.857), (0x1781,0x1781,1.855), (0x1782,0x1782,1.857),
    (0x1783,0x1783,2.018), (0x1784,0x1786,1.857), (0x1787,0x1787,1.695), (0x1788,0x1788,2.826),
    (0x1789,0x1789,2.018), (0x178A,0x178A,1.695), (0x178B,0x178B,1.615), (0x178C,0x178C,1.695),
    (0x178D,0x178D,2.018), (0x178E,0x178E,2.422), (0x178F,0x178F,1.857), (0x1790,0x1790,1.693),
    (0x1791,0x1791,1.615), (0x1792,0x1793,1.857), (0x1794,0x1794,1.855), (0x1795,0x1795,1.695),
    (0x1796,0x1796,1.776), (0x1797,0x1798,1.857), (0x1799,0x1799,2.18), (0x179A,0x179A,0.727),
    (0x179B,0x179B,2.018), (0x179C,0x179C,0.727), (0x179D,0x179D,1.938), (0x179E,0x179E,1.857),
    (0x179F,0x17A1,2.018), (0x17A2,0x17A3,1.857), (0x17A4,0x17A4,2.583), (0x17A5,0x17A5,1.857),
    (0x17A6,0x17A6,1.663), (0x17A7,0x17AA,1.695), (0x17AB,0x17AE,1.776), (0x17AF,0x17AF,1.857),
    (0x17B0,0x17B0,1.776), (0x17B1,0x17B1,1.696), (0x17B2,0x17B2,1.372), (0x17B3,0x17B3,1.696),
    (0x17B4,0x17B5,0), (0x17B6,0x17B6,0.727), (0x17B7,0x17BD,0), (0x17BE,0x17BE,0.807),
    (0x17BF,0x17BF,1.454), (0x17C0,0x17C0,1.453), (0x17C1,0x17C2,0.807), (0x17C3,0x17C3,0.808),
    (0x17C4,0x17C5,1.534), (0x17C6,0x17C6,0), (0x17C7,0x17C7,0.825), (0x17C8,0x17C8,0.727),
    (0x17C9,0x17D3,0), (0x17D4,0x17D4,1.047), (0x17D5,0x17D5,1.29), (0x17D6,0x17D6,0.743),
    (0x17D7,0x17D7,1.372), (0x17D8,0x17D8,3.552), (0x17D9,0x17D9,1.293), (0x17DA,0x17DA,1.858),
    (0x17DB,0x17DB,0.97), (0x17DC,0x17DC,1.131), (0x17DD,0x17DD,0), (0x17DE,0x17DF,1.653),
    (0x17E0,0x17E0,1.453), (0x17E1,0x17E1,1.451), (0x17E2,0x17E2,1.695), (0x17E3,0x17E3,2.018),
    (0x17E4,0x17E6,1.534), (0x17E7,0x17E8,1.695), (0x17E9,0x17E9,1.534), (0x17EA,0x17EF,1.653),
    (0x17F0,0x17F0,0.848), (0x17F1,0x17F1,0.798), (0x17F2,0x17F2,0.427), (0x17F3,0x17F3,1.258),
    (0x17F4,0x17F4,0.789), (0x17F5,0x17F5,0.854), (0x17F6,0x17F6,0.591), (0x17F7,0x17F7,1.06),
    (0x17F8,0x17F8,0.591), (0x17F9,0x17F9,0.998), (0x17FA,0x17FF,1.653),
]

# A consonant that follows COENG stacks below the base instead of beside it.
SUBSCRIPT_WIDTH = 0.113
# Anything outside the measured table — general punctuation, arrows — is close enough
# to one Latin character that guessing is safe; nothing else legitimately appears here.
_DEFAULT_WIDTH = 1.0
_COENG_CP = 0x17D2


def display_width(s):
    """Rendered width of a string in units of one average Latin character."""
    total = 0.0
    after_coeng = False
    for ch in s:
        cp = ord(ch)
        if after_coeng and 0x1780 <= cp <= 0x17A2:
            total += SUBSCRIPT_WIDTH
            after_coeng = False
            continue
        after_coeng = (cp == _COENG_CP)
        for lo, hi, w in _WIDTH_RANGES:
            if lo <= cp <= hi:
                total += w
                break
        else:
            total += _DEFAULT_WIDTH
    return total


# blog/[slug].astro passes `seoTitle || title` to the layout, which renders it as the
# whole <title> with no brand suffix appended — so the budget is the full 60 units.
SEO_TITLE_MAX = 60.0
DESCRIPTION_MAX = 155.0


def check_length_budget(path, text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return
    fm = m.group(1)

    def field(k):
        f = re.search(r"^%s:\s*(.*)$" % k, fm, re.M)
        return f.group(1).strip().strip("\"'") if f else ""

    serp_title = field("seoTitle") or field("title")
    if serp_title:
        w = display_width(serp_title)
        if w > SEO_TITLE_MAX:
            err("title-too-long", path, 1,
                "SERP title is %.1f units (max %.0f); Google cuts the tail off: %s"
                % (w, SEO_TITLE_MAX, serp_title))

    desc = field("description")
    if desc:
        w = display_width(desc)
        if w > DESCRIPTION_MAX:
            err("description-too-long", path, 1,
                "description is %.1f units (max %.0f); the snippet is truncated"
                % (w, DESCRIPTION_MAX))


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
    # Same cap as the articles, same reason. SIXTEEN of 29 pulse titles opened
    # `សិល្បៈនៃកា` ("the art of the...") and two more opened `សិល្បៈធ្វើ` — 18 of 29 built
    # from one phrase. The prompt in fetch_catering_pulse.py already asks the model to vary
    # the opening, and entries 23+ obey it; the block that predates that instruction did
    # not. A request in a prompt is not enforcement, so cap it here too.
    # Summaries as well as titles: the summary is the SERP snippet, and seven of them
    # opened `ការណែនាំអំ` ("a guide to...") with three more on `ស្វែងយល់ពី` — the same
    # phrase the blog descriptions had to be cleared of.
    for field, label in (("title_km", "titles"), ("summary_km", "summaries")):
        openers = {}
        for it in items:
            t = it.get(field) or ""
            if len(t) >= OPENER_PREFIX:
                openers.setdefault(t[:OPENER_PREFIX], []).append(it.get("id", "?"))
        for prefix, ids in sorted(openers.items()):
            if len(ids) > OPENER_CAP:
                err("repeated-opener", p, 1,
                    "%d pulse %s open with %r (max %d) — %s"
                    % (len(ids), label, prefix, OPENER_CAP, ", ".join(sorted(ids))))

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

        # Pulse titles reach the SERP exactly like article titles do, and pulse is the
        # surface with NO human review — one Gemini-written entry lands every day.
        # ADVISORY on purpose. `fetch_catering_pulse.py` asks the model for 30-55
        # characters, but that file's own comment says it best: "an instruction in the
        # prompt is a request", not a guarantee — the model returns up to 70 units. Eight
        # entries are over today. Making this an error would block every build until the
        # back catalogue is rewritten, which is the trap of turning a gate blocking while
        # violations exist. Clear the backlog and add a generator-side rejection (the file
        # already rejects foreign script this way), THEN promote this to err().
        # ADVISORY. Section 10 forbids English words in public copy and the generator
        # prompt demands "ZERO raw English words" — yet `Five-Spice` and `(Miso)` are live
        # in pulse titles. They survive `check_foreign_scripts` because that rule allows
        # printable ASCII (legitimately: source titles and numerals need it), so an English
        # word is invisible to a codepoint whitelist in a way a Chinese word is not.
        # Three or more consecutive Latin letters is a word, not a numeral or a stray mark.
        # Read the id from THIS loop's item. `ident` belongs to the earlier loop over the
        # same list and still holds its last value here, so borrowing it labelled every
        # finding "pulse-27" — a report that names the wrong entry is worse than none.
        pid = it.get("id", "?")

        for field in ("title_km", "summary_km"):
            v = it.get(field) or ""
            for m in re.finditer(r"[A-Za-z]{3,}", v):
                err("pulse-english-word", p, 1,
                    "%s.%s contains the English word %r — AGENTS.md 10 requires 100%% Khmer"
                    % (pid, field, m.group(0)))

        t_km = it.get("title_km") or ""
        if t_km and display_width(t_km) > SEO_TITLE_MAX:
            err("pulse-title-too-long", p, 1,
                "%s title_km is %.1f units (max %.0f); Google truncates it: %s"
                % (pid, display_width(t_km), SEO_TITLE_MAX, t_km))

        # pulse/[id].astro passes summary_km straight to the layout as the meta
        # description. Layout's truncateKhmer is a cluster-safety net that counts
        # CODEPOINTS, so a 153-codepoint summary measuring 172 units sails through it —
        # the exact len()-vs-width error this file exists to prevent. The budget has to be
        # enforced here, in units, at the source.
        s_km = it.get("summary_km") or ""
        if s_km and display_width(s_km) > DESCRIPTION_MAX:
            err("pulse-summary-too-long", p, 1,
                "%s summary_km is %.1f units (max %.0f); the SERP snippet is cut short"
                % (pid, display_width(s_km), DESCRIPTION_MAX))


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


# ---------------------------------------------------------------- rule 11

# Every article reads fine on its own. The failure only becomes visible on a search
# results page, where ten of them sit in a column and open with the same words.
#
# Measured on this repo 2026-08-16: ELEVEN of fifteen descriptions opened with
# `ស្វែងយល់ពី` ("learn about"), articles 01 through 11 — a contiguous block, which is
# the signature of one batch generated with one instruction. Articles 12-15, written
# later, each opened differently.
#
# A cap, not a cleanup. Sunder fixed the same defect by rewriting in batches and got
# NINE new templates of five articles each, because the opening strategy was assigned
# per batch instead of per article. Only a standing limit survives the next batch.
#
# Deliberately scoped to the description and the first prose paragraph. Headings are
# exempt: AGENTS.md 14 REQUIRES `## សំណួរដែលសួរញឹកញាប់` and `## សេចក្តីសន្និដ្ឋាន` in
# every article, so a cap applied to headings would fight the structure rule and lose.
OPENER_CAP = 2
# Ten codepoints is a phrase, not grammar. Khmer sentences legitimately share short
# leading particles (`ការ`, `នៅ`); at ten the match is a reused construction.
OPENER_PREFIX = 10


def _first_prose(body):
    for line in body.split("\n"):
        s = line.strip()
        if not s or s.startswith(("#", "!", ">", "|", "-", "*", "<")):
            continue
        return s
    return ""


def check_opener_variety(articles):
    """articles: list of (path, text). Cross-file, so it cannot live in the per-file loop."""
    buckets = {"seoTitle": {}, "description": {}, "body opening": {}}
    for path, text in articles:
        m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)

        def fmfield(k):
            f = re.search(r"^%s:\s*(.*)$" % k, fm, re.M)
            return f.group(1).strip().strip("\"'") if f else ""

        fields = {
            # The title is the bold blue line, so a shared title opener is the most
            # visible repetition of the three. Four of fifteen opened `របៀបជ្រើសរើស`.
            "seoTitle": fmfield("seoTitle") or fmfield("title"),
            "description": fmfield("description"),
            "body opening": _first_prose(body),
        }
        for kind, value in fields.items():
            if len(value) < OPENER_PREFIX:
                continue
            buckets[kind].setdefault(value[:OPENER_PREFIX], []).append(path)

    for kind, groups in buckets.items():
        for prefix, paths in sorted(groups.items()):
            if len(paths) <= OPENER_CAP:
                continue
            names = ", ".join(os.path.basename(p)[:2] for p in sorted(paths))
            for p in sorted(paths):
                err("repeated-opener", p, 1,
                    "%s opens with %r, shared by %d articles (max %d) — %s"
                    % (kind, prefix, len(paths), OPENER_CAP, names))


def main():
    strict = "--strict" in sys.argv

    articles = sorted(glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md")))
    if not articles:
        print("no articles found — wrong working directory?")
        return 1

    loaded = []
    for path in articles:
        text = read(path)
        loaded.append((path, text))
        check_length_budget(path, text)
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

    check_opener_variety(loaded)
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

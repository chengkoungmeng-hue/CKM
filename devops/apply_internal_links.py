"""Apply the declared internal-link table to the blog markdown. Idempotent.

`src/data/internalLinks.json` is the single source of truth: each entry names an article,
an EXACT anchor string that already exists in that article's prose, and a destination
slug. This script wraps that anchor in a markdown link. It never invents text.

Why a declaration table and not a keyword regex:

  The obvious approach is Sunder's `apply_internal_links.cjs` — scan for keywords and
  link them wherever they appear. That script corrupted 130 places across 53 files: it
  replaced `（TCO）` with ` [TCO](…)`, eating the brackets and adding a space Chinese
  does not use. Khmer makes the same approach strictly worse, because Khmer has no
  spaces between words, so there is no `\\b` to anchor a pattern to and no reliable way
  to tell a word from the middle of a longer one.

  Exact-string matching sidesteps the whole problem. Every anchor is verified to occur
  EXACTLY ONCE, in ordinary body prose, before anything is written. A table entry that
  cannot be applied safely is refused and reported, never guessed at.

Safety rules, all enforced before any write:
  - the anchor must appear exactly once in the file, outside frontmatter
  - never inside a heading line, a table row, or an existing markdown link
  - the destination article must exist
  - the emitted URL always ends in "/" (AGENTS.md section 3: a missing slash costs a 301)
  - already-applied links are detected and skipped, so re-running changes nothing

    python devops/apply_internal_links.py            # apply
    python devops/apply_internal_links.py --check    # verify only, exit 1 on problems
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "src", "data", "internalLinks.json")
BLOG = os.path.join(ROOT, "src", "content", "blog")

LINK_SPAN = re.compile(r"\[[^\]]*\]\([^)]*\)")


def split_frontmatter(text):
    """Return (frontmatter_including_fences, body). Body offsets are what we edit."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            cut = text.find("\n", end + 1) + 1
            return text[:cut], text[cut:]
    return "", text


def safe_occurrences(body, anchor):
    """Every occurrence of `anchor` that it would be safe to wrap in a link.

    Returns (safe, skipped) where skipped explains each rejected occurrence, so a
    refusal can say WHY rather than just failing.
    """
    safe, skipped = [], []
    offset = 0
    for line in body.splitlines(keepends=True):
        stripped = line.lstrip()
        start = 0
        while True:
            i = line.find(anchor, start)
            if i == -1:
                break
            start = i + 1
            if stripped.startswith("#"):
                skipped.append("inside a heading")
            elif "|" in line:
                skipped.append("inside a table row")
            elif any(m.start() <= i < m.end() for m in LINK_SPAN.finditer(line)):
                skipped.append("inside an existing markdown link")
            else:
                safe.append(offset + i)
        offset += len(line)
    return safe, skipped


def apply_entry(entry, check_only):
    article, anchor, target = entry["article"], entry["anchor"], entry["target"]
    src = os.path.join(BLOG, article + ".md")
    dst = os.path.join(BLOG, target + ".md")

    if not os.path.isfile(src):
        return "ERROR", f"source article {article}.md does not exist"
    if not os.path.isfile(dst):
        return "ERROR", f"destination {target}.md does not exist"
    if article == target:
        return "ERROR", "an article cannot link to itself"

    text = open(src, encoding="utf-8").read()
    fm, body = split_frontmatter(text)
    url = f"/blog/{target}/"
    replacement = f"[{anchor}]({url})"

    if replacement in body:
        return "SKIP", "already applied"

    safe, skipped = safe_occurrences(body, anchor)
    if not safe:
        why = f"; rejected occurrences: {', '.join(sorted(set(skipped)))}" if skipped else ""
        return "ERROR", f"anchor not found in ordinary prose{why}"
    if len(safe) > 1:
        return "ERROR", (f"anchor appears {len(safe)} times in prose — it must be unique, "
                         f"or a replace would hit the wrong one. Lengthen it.")

    if check_only:
        return "OK", "would apply"

    i = safe[0]
    body = body[:i] + replacement + body[i + len(anchor):]
    with open(src, "w", encoding="utf-8", newline="") as f:
        f.write(fm + body)
    return "APPLIED", f"-> {url}"


def main(argv):
    check_only = "--check" in argv
    if not os.path.exists(TABLE):
        print(f"No link table at {TABLE}; nothing to do.")
        return 0

    entries = json.load(open(TABLE, encoding="utf-8"))
    counts = {}
    problems = 0
    for e in entries:
        status, detail = apply_entry(e, check_only)
        counts[status] = counts.get(status, 0) + 1
        if status == "ERROR":
            problems += 1
            print(f"  [ERROR ] {e['article']} -> {e['target']}: {detail}")
            print(f"           anchor: {e['anchor'][:60]}")
        else:
            print(f"  [{status:<7}] {e['article']} -> {e['target']}  {detail}")

    print(f"\n{len(entries)} entries: " +
          ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Move the conclusion after the FAQ, per AGENTS.md section 14.

    body -> ## សំណួរដែលសួរញឹកញាប់ -> ## សេចក្តីសន្និដ្ឋាន

[REGRESSION] Articles shipped with the conclusion BEFORE the FAQ, so the last thing a
reader saw was an administrative note. The conclusion sits closest to the CTA; it
belongs where the reader is ready to act. AGENTS.md named six articles; measured
2026-08-15, twelve are affected.

This is a pure block move. It rewrites no Khmer, so the safety property worth enforcing
is that the file's content is a permutation of itself: the script refuses to write
unless the sorted multiset of lines is identical before and after.

    python devops/fix_section_order.py --check   # report only
    python devops/fix_section_order.py           # rewrite
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAQ = "សំណួរដែលសួរញឹកញាប់"
CONCLUSION = "សេចក្តីសន្និដ្ឋាន"
H2 = re.compile(r"^##\s+(?!#)(.*)$", re.M)


def split_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            cut = text.find("\n", end + 1) + 1
            return text[:cut], text[cut:]
    return "", text


def h2_blocks(body):
    """[(title, start, end)] for every level-2 section; end is exclusive."""
    marks = [(m.group(1).strip(), m.start()) for m in H2.finditer(body)]
    out = []
    for i, (title, start) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(body)
        out.append((title, start, end))
    return out


def reorder(body):
    """Return (new_body, note). new_body is None when nothing needs doing."""
    blocks = h2_blocks(body)
    fi = next((i for i, b in enumerate(blocks) if FAQ in b[0]), None)
    ci = next((i for i, b in enumerate(blocks) if CONCLUSION in b[0]), None)

    if fi is None and ci is None:
        return None, "neither FAQ nor conclusion present"
    if ci is None:
        return None, "NO CONCLUSION — needs one written, cannot be fixed by moving blocks"
    if fi is None:
        return None, "no FAQ section"
    if fi < ci:
        return None, "already correct"

    _, cs, ce = blocks[ci]
    _, fs, fe = blocks[fi]
    conclusion = body[cs:ce]
    faq = body[fs:fe]

    if ci + 1 != fi:
        return None, ("conclusion and FAQ are not adjacent (%d blocks between) — "
                      "refusing to guess" % (fi - ci - 1))

    # Adjacent: [ ... prefix ][ conclusion ][ faq ][ suffix ] -> swap the middle two.
    new_body = body[:cs] + faq + conclusion + body[fe:]

    # Normalise the seam: exactly one blank line between the two blocks, and preserve
    # the file's single trailing newline (AGENTS.md section 17).
    new_body = re.sub(r"\n{3,}", "\n\n", new_body)
    if not new_body.endswith("\n"):
        new_body += "\n"
    return new_body, "moved conclusion after FAQ"


def main(argv):
    check_only = "--check" in argv
    changed = failed = ok = 0

    for path in sorted(glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md"))):
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        fm, body = split_frontmatter(text)
        new_body, note = reorder(body)

        if new_body is None:
            if note == "already correct":
                ok += 1
                print(f"  [ok      ] {name}")
            else:
                failed += 1
                print(f"  [MANUAL  ] {name}: {note}")
            continue

        # The whole safety argument: content must be a permutation of itself.
        before = sorted(l.strip() for l in body.splitlines() if l.strip())
        after = sorted(l.strip() for l in new_body.splitlines() if l.strip())
        if before != after:
            failed += 1
            lost = set(before) - set(after)
            print(f"  [REFUSED ] {name}: content changed, not just order "
                  f"({len(lost)} line(s) would be lost)")
            continue

        changed += 1
        if check_only:
            print(f"  [would   ] {name}: {note}")
        else:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(fm + new_body)
            print(f"  [fixed   ] {name}: {note}")

    print(f"\nalready correct {ok} | {'would fix' if check_only else 'fixed'} {changed} "
          f"| needs a human {failed}")
    return 1 if (failed and check_only) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Generate public/llms.txt and public/llms-full.txt from the site's own content.

Both files existed but nothing produced them, so they drifted. Measured 2026-08-15 they
contained **zero** of the 15 blog slugs and **zero** of the 27 pulse slugs — an index of
the site's content that indexed none of it, which is the one job llms.txt has.

They had also drifted past AGENTS.md section 11, making claims the articles themselves are
forbidden to make: "climate-controlled banquet tents", "strictly monitored cold-chain
storage", "capable of serving 500+ guests simultaneously". We market this business on the
owner's behalf and cannot verify his operations, so we do not commit him to equipment,
capacity figures or temperature control. Those are gone and must not come back;
check_content.py now scans these two files for them.

Facts are derived from the source of truth rather than retyped:
  phones / telegram   src/data/homeData.ts
  address / geo       src/layouts/Layout.astro JSON-LD
  article index       src/content/blog/*.md frontmatter (already validated by check_content)
  pulse index         src/data/pulseData.json
If any of those cannot be parsed the script exits non-zero rather than emitting a file
that looks fine and is quietly wrong.

    python devops/generate_llms_txt.py           # write
    python devops/generate_llms_txt.py --check   # exit 1 if the files are out of date
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ckmkh.com"
OUT_SHORT = os.path.join(ROOT, "public", "llms.txt")
OUT_FULL = os.path.join(ROOT, "public", "llms-full.txt")


def die(msg):
    print(f"::error::{msg}")
    sys.exit(1)


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8").read()


def extract_facts():
    home = read("src/data/homeData.ts")
    layout = read("src/layouts/Layout.astro")

    phones = re.findall(r'\{\s*num:\s*"([^"]+)",\s*type:\s*"([^"]+)"', home)
    telegram = re.search(r'telegramLink\s*=\s*"([^"]+)"', home)
    street = re.search(r'streetAddress:\s*"([^"]+)"', layout)
    lat = re.search(r'latitude:\s*([\d.]+)', layout)
    lon = re.search(r'longitude:\s*([\d.]+)', layout)
    postal = re.search(r'postalCode:\s*"([^"]+)"', layout)

    if not phones:
        die("could not parse phone numbers from src/data/homeData.ts")
    for name, val in (("telegram", telegram), ("street address", street),
                      ("latitude", lat), ("longitude", lon), ("postal code", postal)):
        if not val:
            die(f"could not parse {name} from the source files")

    return {
        "phones": phones, "telegram": telegram.group(1), "street": street.group(1),
        "lat": lat.group(1), "lon": lon.group(1), "postal": postal.group(1),
    }


def fm_value(fm, key):
    m = re.search(rf'^{key}:\s*(.+?)\s*$', fm, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if v[:1] in "\"'" and v[-1:] == v[:1]:
        v = v[1:-1]
    return v


def load_articles():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md"))):
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            die(f"{path} has no frontmatter")
        fm, body = text.split("---", 2)[1], text.split("---", 2)[2]
        slug = os.path.splitext(os.path.basename(path))[0]
        quick = ""
        m = re.search(r"^##\s+ចម្លើយរហ័ស\s*$", body, re.M)
        if m:
            rest = body[m.end():].lstrip("\n")
            for line in rest.splitlines():
                if line.strip() and not line.startswith("#"):
                    quick = line.strip()
                    break
        out.append({
            "slug": slug,
            "title": fm_value(fm, "title"),
            "description": fm_value(fm, "description"),
            "quick": quick,
        })
    if len(out) < 5:
        die(f"only {len(out)} articles found — wrong working directory?")
    return out


def load_pulse():
    path = os.path.join(ROOT, "src", "data", "pulseData.json")
    if not os.path.exists(path):
        return []
    return json.load(open(path, encoding="utf-8"))


PREAMBLE = """# CKM Catering (ចេង គួងម៉េង) — Sino-Khmer Banquet Catering in Phnom Penh

> CKM (Cheng Koung Meng / ចេង គួងម៉េង) is a family Sino-Khmer catering and banquet
> kitchen in Phnom Penh with more than 60 years behind it, cooking for weddings,
> corporate events, housewarmings and family celebrations. The public site is written
> entirely in Khmer.

## About this file

This index is generated from the site's own content by `devops/generate_llms_txt.py`.
Do not hand-edit it; edit the source and regenerate.

Specific commitments — prices, table counts, service areas, equipment, exact timings —
are deliberately absent. They vary per event and are settled in a direct conversation
with the owner, not published. Please do not infer them from this file.
"""


def contact_block(f):
    lines = ["## Contact", ""]
    for num, kind in f["phones"]:
        lines.append(f"- **Phone ({kind})**: {num}")
    lines += [
        f"- **Telegram**: {f['telegram']}",
        f"- **Address**: {f['street']}, Phnom Penh {f['postal']}, Cambodia",
        f"- **Coordinates**: {f['lat']}, {f['lon']}",
        f"- **Website**: {SITE}/",
    ]
    return "\n".join(lines)


def build_short(facts, articles, pulse):
    p = [PREAMBLE, "## Key pages", "",
         f"- [Home]({SITE}/)",
         f"- [Articles]({SITE}/blog/)",
         f"- [Daily culinary notes]({SITE}/pulse/)",
         f"- [Tang Huot bakery sub-brand]({SITE}/tanghuot/)",
         f"- [Full index]({SITE}/llms-full.txt)",
         "", f"## Articles ({len(articles)})", ""]
    for a in articles:
        p.append(f"- [{a['title']}]({SITE}/blog/{a['slug']}/)")
        if a["description"]:
            p.append(f"  {a['description']}")
    p += ["", f"## Daily culinary notes ({len(pulse)})", "",
          f"Short Khmer pieces on cooking technique, published daily and indexed at "
          f"{SITE}/pulse/.", ""]
    for e in pulse[:20]:
        if e.get("slug") and e.get("title_km"):
            p.append(f"- [{e['title_km']}]({SITE}/pulse/{e['slug']}/)")
    if len(pulse) > 20:
        p.append(f"- …and {len(pulse) - 20} more at {SITE}/pulse/")
    p += ["", contact_block(facts), ""]
    return "\n".join(p)


def build_full(facts, articles, pulse):
    p = [PREAMBLE, f"## Articles ({len(articles)}) — with the question each one answers", ""]
    for a in articles:
        p.append(f"### {a['title']}")
        p.append(f"{SITE}/blog/{a['slug']}/")
        if a["description"]:
            p.append(f"\n{a['description']}")
        if a["quick"]:
            p.append(f"\nQuick answer: {a['quick']}")
        p.append("")
    p += [f"## Daily culinary notes ({len(pulse)})", ""]
    for e in pulse:
        if e.get("slug") and e.get("title_km"):
            p.append(f"- [{e['title_km']}]({SITE}/pulse/{e['slug']}/)")
            if e.get("summary_km"):
                p.append(f"  {e['summary_km']}")
    p += ["", contact_block(facts), ""]
    return "\n".join(p)


def main(argv):
    check_only = "--check" in argv
    facts = extract_facts()
    articles = load_articles()
    pulse = load_pulse()

    targets = [(OUT_SHORT, build_short(facts, articles, pulse)),
               (OUT_FULL, build_full(facts, articles, pulse))]

    stale = False
    for path, content in targets:
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if current == content:
            print(f"  [ok    ] {os.path.relpath(path, ROOT)} up to date")
            continue
        stale = True
        if check_only:
            print(f"  [STALE ] {os.path.relpath(path, ROOT)} differs from generated output")
        else:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
            print(f"  [written] {os.path.relpath(path, ROOT)} "
                  f"({len(content):,} bytes, {len(articles)} articles, {len(pulse)} notes)")

    if check_only and stale:
        print("::error::llms.txt files are out of date — run devops/generate_llms_txt.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

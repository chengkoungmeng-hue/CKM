"""Build the Facebook post queue from content this repository already owns.

WHY THIS IS NOT A GENERATOR IN THE GEMINI SENSE
-----------------------------------------------
Nothing here calls a model. Every Khmer sentence a reader will see is either

  (a) already published on ckmkh.com and already through check_content.py, or
  (b) one of the ~20 short strings in HOOKS / QUESTIONS below, which were written
      once from phrasings the site already uses and reviewed once.

AGENTS.md section 15 is blunt about why: an instruction in a prompt is a request, only
a gate is a standard, and the pulse pipeline shipped flat walls of text for weeks
because structure was asked for and not enforced. A daily Facebook post carries the
same exposure with none of the build-time gates, so the safest design is the one where
the model is not in the loop at all. It also costs nothing to run and cannot drift when
a provider updates a model.

SOURCES, measured 2026-08-23
  16  dishes            src/data/homeData.ts        -- name + description + a REAL photo
  40  FAQ pairs         src/content/blog/*.md       -- already marked up as FAQPage
  15  quick answers     src/content/blog/*.md       -- the ## ចម្លើយរហ័ស blocks
  66  banquet topics    devops/pulse_seeds.json     -- written for this exact audience,
                                                       idle since pulse froze 2026-08-23
  = 137 posts before anything new has to be written.

The 16 dish posts come first on purpose: they are the only ones with a genuine
photograph of the food, and section 6 forbids passing an illustration off as the thing
it depicts. Everything after them needs either an AI illustration the owner generates
from the prompt this script emits, or a typographic card.

PLATFORM CONSTRAINTS, from .agents/skills/ckm-seo/references/platform_mechanics.md
(researched 2026-08-19, inside its six-month validity window)
  - Page organic reach is 1.4-2.2% of followers. Groups reach 20-40% of members.
    Groups are the reach engine; the page is the storefront.
  - Album/carousel reaches best (1.6%), then video and single image (1.5%). Link posts
    are worst (1.3%) and Meta itself now advises putting the link in the first comment.
    We post zero links either way -- AGENTS.md section 21.
  - 4:5 portrait, 1080x1350, is the mobile sweet spot. Text on the image under 20%.
  - Engagement bait is demoted, but asking for advice, recommendations or opinions is
    EXPLICITLY exempt. Every QUESTION below is a real open question for that reason.
  - Copy: 40-80 characters for an announcement, 80-150 when you want comments. The
    first 80 characters must carry the point -- Facebook truncates at "See More".

Usage:
    python devops/make_fb_posts.py --batch dishes --count 16
    python devops/make_fb_posts.py --batch faq --count 10
    python devops/make_fb_posts.py --all --out devops/reports/fb_queue.md
"""
import argparse
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_content import (  # noqa: E402
    display_width, check_absolutes, check_hard_specs, check_foreign_scripts,
    check_khmer_clusters, check_doubled_words, ERRORS, WARNINGS,
)

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------- new Khmer
# The ONLY strings here a reader sees that are not already live on the site. Each was
# built from a construction the site already uses -- តើ opens 83 questions across the
# articles, សម្រាប់ 98 phrases, នៅពេល 25 -- so the grammar is borrowed, not invented.
# Section 12 records what writing a Khmer phrase from memory cost once already.
#
# Keep this list SHORT. Twenty strings can be reviewed by a Khmer speaker in one sitting;
# two hundred cannot, and an unreviewed pool is how the register drifts.

HOOKS = [
    "នៅក្នុងពិធីមង្គលការខ្មែរ-ចិន",          # in a Khmer-Chinese wedding
    "សម្រាប់តុពិធីរបស់គ្រួសារ",              # for the family's banquet table
    "មុនពេលសម្រេចចិត្តលើម៉ឺនុយ",             # before deciding on the menu
    "នៅពេលរៀបចំកម្មវិធីនៅផ្ទះ",              # when arranging an event at home
    "រាល់ពិធីជប់លៀងធំៗ",                     # at every large celebration
]

# [DEFECT, fixed 2026-08-23] One flat question pool rotated by index put
# "តើគ្រួសារលោកអ្នកតែងតែជ្រើសរើសមុខម្ហូបណា?" ("which dish does your family always pick")
# under a post about the timing of a monk's meal offering. A closing question that does
# not follow from the post is worse than none: it reads as a template, which is exactly
# what a reader dismisses. Questions are therefore scoped to the KIND of post, and seed
# posts do not get one from here at all -- every seed already carries its own question
# in angle_km, written for that specific topic.
QUESTIONS = {
    # A dish post shows one dish. Ask about dishes.
    "dish": [
        "តើគ្រួសារលោកអ្នកតែងតែជ្រើសរើសមុខម្ហូបណា?",
        "តើចាស់ទុំក្នុងគ្រួសារលោកអ្នកចូលចិត្តមុខម្ហូបណា?",
        "តើមុខម្ហូបណាដែលភ្ញៀវរបស់លោកអ្នកនិយាយច្រើនជាងគេ?",
    ],
    # An FAQ or a quick answer is about a planning problem. Ask about the problem.
    "faq": [
        "តើលោកអ្នកធ្លាប់ជួបបញ្ហានេះដែរឬទេ?",
        "តើលោកអ្នកគ្រោងរៀបចំប៉ុន្មានតុ?",
    ],
}
QUESTIONS["quick"] = QUESTIONS["faq"]

# The fold. platform_mechanics.md: 40-80 characters reads as an announcement, 80-150 is
# where posts earn comments, and 200+ works only for a structured value narrative. 180
# keeps every post inside the range that earns comments.
POST_MAX_CHARS = 180

# Past this a post is an article, not a post. A source that cannot say one whole
# sentence inside it was written for a page and is dropped rather than mangled.
HARD_CEILING = 300

# --------------------------------------------------------------------------- image
IMAGE_STYLE = (
    "8k professional culinary photography, traditional high-end Cambodian Chinese "
    "banquet dish, luxurious presentation, natural warm lighting, authentic Phnom Penh "
    "wedding banquet table setting, steam rising, shallow depth of field, "
    "deep charcoal and warm champagne-gold tones, no text, no watermark, no cgi, "
    "no rendering, 4:5 aspect ratio, 1080x1350"
)
IMAGE_NEGATIVE = (
    "western plating, industrial kitchen, stock-photo chef, fake-looking food, "
    "text overlay, logos, hands in frame, cluttered background, "
    "blue-tinted shadows, orange amber cast"
)

# The palette, authoritative from tailwind.config.mjs, for any card or overlay drawn on
# top of these photographs.
#
# NOTE for whoever maintains C:\Projects\DevOps\Marketing\CKM\Facebook\ASSET_SPEC.md:
# that file specifies #0F172A with #D97706/#F59E0B. Those are Tailwind slate-900 and
# amber-600/500 -- the exact two colours CKM's design system was created to REPLACE. The
# tailwind config says so in its own comments ("取代 slate-900", "取代 amber-600"), and
# AGENTS.md section 9 forbids raw amber/blue/slate accents where a token exists, because
# plain primaries undercut the quiet-luxury positioning. Assets built to that spec will
# not look like the website.
BRAND_HEX = {
    "onyx": "#171717",
    "champagne": "#C5A059",
    "champagne_dark": "#8C6D31",
    "pearl": "#FDFCF8",
}


def subject_en(slug_or_name):
    """An English subject line for the image model.

    [DEFECT, fixed 2026-08-23] The prompt carried the Khmer topic as its SUBJECT. An
    image model has no useful handling of Khmer, so it would have ignored the line and
    returned 121 near-identical generic banquet photographs -- the same failure the
    pulse share cards had, arrived at from the other direction. Every source already
    carries a descriptive English identifier: the seeds have slugs like
    "crispy-fried-whole-fish-banquet", and the articles are named
    "01-traditional-8-course-wedding-menu". Both describe the subject in English
    already, so nothing has to be translated.
    """
    text = re.sub(r"\.mdx?$", "", str(slug_or_name))
    text = re.sub(r"^\d+[-_]", "", text)            # strip an article number prefix
    return re.sub(r"[-_]+", " ", text).strip()


# --------------------------------------------------------------------------- sources
def load_dishes():
    """16 dishes with a real photograph already on the homepage."""
    ts = io.open(os.path.join(ROOT, "src", "data", "homeData.ts"), encoding="utf-8").read()
    pairs = re.findall(
        r'title:\s*"([^"]+)",\s*image:\s*(\w+),\s*desc:\s*"([^"]+)"', ts)
    out = []
    for i, (title, imgvar, desc) in enumerate(pairs, 1):
        out.append({
            "kind": "dish",
            "ref": f"homeData.ts dish {i:02d}",
            "title": title,
            "body": desc,
            # These exist. src/assets/images/home/menu-NN.webp is on the homepage today,
            # so the post needs no AI illustration at all.
            "photo": f"src/assets/images/home/menu-{i:02d}.webp",
            "subject_en": None,
        })
    return out


def _articles():
    return sorted(glob.glob(os.path.join(ROOT, "src", "content", "blog", "*.md")))


def load_faq():
    """Every ### question under the FAQ heading, with its answer."""
    out = []
    for path in _articles():
        text = io.open(path, encoding="utf-8").read()
        m = re.search(r"^## សំណួរដែលសួរញឹកញាប់[^\n]*\n(.*?)(?=^## |\Z)",
                      text, re.S | re.M)
        if not m:
            continue
        block = m.group(1)
        parts = re.split(r"^### ", block, flags=re.M)[1:]
        for p in parts:
            lines = p.strip().split("\n")
            q = re.sub(r"^[០-៩0-9]+\s*[.)។]?\s*", "", lines[0]).strip()
            a = " ".join(l.strip() for l in lines[1:] if l.strip() and not l.startswith("|"))
            a = re.sub(r"[*_`]|\[([^\]]*)\]\([^)]*\)", r"\1", a).strip()
            if q and a:
                out.append({
                    "kind": "faq",
                    "ref": f"{os.path.basename(path)}#{len(out) + 1}",
                    "title": q,
                    "body": a,
                    "photo": None,
                    "subject_en": subject_en(os.path.basename(path)),
                })
    return out


def load_quick_answers():
    out = []
    for path in _articles():
        text = io.open(path, encoding="utf-8").read()
        m = re.search(r"^## ចម្លើយរហ័ស[^\n]*\n+(.+?)(?=\n\n|\n##)", text, re.S | re.M)
        if not m:
            continue
        body = re.sub(r"\s+", " ", m.group(1)).strip()
        body = re.sub(r"[*_`]|\[([^\]]*)\]\([^)]*\)", r"\1", body).strip()
        out.append({
            "kind": "quick",
            "ref": os.path.basename(path),
            "title": "",
            "body": body,
            "photo": None,
            "subject_en": subject_en(os.path.basename(path)),
        })
    return out


def load_seeds():
    """The 66 banquet topics. Idle since pulse froze; written for this audience."""
    raw = json.load(io.open(os.path.join(ROOT, "devops", "pulse_seeds.json"),
                            encoding="utf-8"))
    seeds = raw if isinstance(raw, list) else raw.get("seeds", [])
    return [{
        "kind": "seed",
        "ref": s.get("id", "?"),
        "title": s.get("topic_km", ""),
        "body": s.get("angle_km", ""),
        "photo": None,
        # The slug is already an English description of the dish or occasion.
        "subject_en": subject_en(s.get("slug", s.get("id", ""))),
    } for s in seeds]


SOURCES = {
    "dishes": load_dishes,
    "faq": load_faq,
    "quick": load_quick_answers,
    "seeds": load_seeds,
}


# --------------------------------------------------------------------------- assembly
def truncate_sentence(text, max_chars):
    """Keep whole Khmer sentences. Never cut inside one.

    [DEFECT, fixed 2026-08-23] This used to fall back to cutting at a space when no ។
    fitted, which produced "…នៅក្នុងវប្បធម៌ខ្មែរ លេខ ៨" -- a post that stops mid-thought.
    Khmer puts spaces between phrases, not between words, so a space is not a safe
    boundary for meaning even though it is safe for rendering. Sentence marks are the
    only cut point that leaves the text saying something.

    Returns "" when even the first sentence will not fit, and the caller drops the post
    rather than publishing a fragment. Section 14's rule about cluster-safe truncation
    still holds and is satisfied a fortiori: ។ is never inside a cluster.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text

    sentences = [s.strip() for s in re.split(r"(?<=។)", text) if s.strip()]
    if not sentences:
        return ""

    kept, total = [], 0
    for s in sentences:
        add = len(s) + (1 if kept else 0)
        if total + add > max_chars and kept:
            break
        kept.append(s)
        total += add
        if total > max_chars:
            break  # the first sentence alone overran; take it whole and stop

    # Overrunning the fold with a complete thought beats dropping the post. The 80-180
    # range is where posts earn comments, not a hard limit -- platform_mechanics.md
    # allows 200+ for a structured value narrative, and an FAQ answer is one. Enforcing
    # 180 strictly cost 50 of 137 sources on the first run, including two dish posts
    # that had real photographs. HARD_CEILING only rejects prose that was never a post.
    return " ".join(kept) if total <= HARD_CEILING else ""


def build_post(item, index):
    """One post: Khmer copy, the image instruction, and provenance.

    Returns None when the source will not fit the fold without being cut mid-sentence.
    Dropping a post costs one of 137; publishing a fragment costs credibility.
    """
    hook = HOOKS[index % len(HOOKS)]
    kind = item["kind"]

    if kind == "seed":
        # A seed already IS a post: topic_km is the subject, angle_km is a real question
        # written for that exact subject. Nothing generic is added.
        lead = item["title"]
        body = ""
        question = item["body"]
    else:
        lead = hook if kind == "quick" else item["title"]
        pool = QUESTIONS[kind]
        question = pool[index % len(pool)]

    # Budget the WHOLE post, not the body alone. The 80-180 range is what a reader sees
    # before Facebook folds the rest behind "See More", and the lead and the closing
    # question are part of that. Measured before this was fixed: all 40 FAQ posts and all
    # 15 quick-answer posts overran, up to 317 characters, because only the body was
    # capped. Those two sources are article prose -- written for a page, not a feed. The
    # 66 seed topics needed no trimming at all, which is what you would expect from
    # material that was written for this audience in the first place.
        # [DEFECT, fixed 2026-08-23] A dish's description opens by repeating its own
        # name, so the post said "ម្ហូបក្លែម៦មុខ" as the lead and again as the first
        # words of the body. Strip the echo.
        raw = item["body"]
        if lead and raw.startswith(lead):
            raw = raw[len(lead):].lstrip(" ។")

        overhead = len(lead) + len(question) + 4  # two blank-line separators
        body = truncate_sentence(raw, max(POST_MAX_CHARS - overhead, 60))
        if not body:
            return None

    copy = f"{lead}\n\n{body}\n\n{question}" if body else f"{lead}\n\n{question}"

    # A stable filename per post, so a batch of images generated months apart still
    # lands against the right copy. Derived from the source reference, never from the
    # list position: AGENTS.md section 15 records what position-derived identifiers cost
    # when the pulse ids were reassigned on every run and a day of URLs 404'd.
    # [DEFECT, fixed 2026-08-23] The filename came from item["ref"] alone, and the four
    # FAQ entries taken from one article all share that ref -- so four prompts pointed at
    # one filename and three images would have overwritten the others on generation. The
    # ordinal makes it unique without making it positional: it is the source's own index
    # within its file, not its place in the queue.
    slug = re.sub(r"[^a-z0-9]+", "-", item["ref"].lower()).strip("-")
    filename = f"fb-{kind}-{slug}-{index:03d}.png"

    if item["photo"]:
        image = f"USE EXISTING PHOTO: {item['photo']}"
        prompt = None
    else:
        subject = item.get("subject_en") or "Cambodian Chinese banquet dish"
        prompt = f"{IMAGE_STYLE}. SUBJECT: {subject}. AVOID: {IMAGE_NEGATIVE}"
        image = prompt

    return {
        "kind": kind,
        "ref": item["ref"],
        "copy": copy,
        "chars": len(copy),
        "units": round(display_width(copy), 1),
        "image": image,
        "prompt": prompt,
        "filename": filename,
        "photo": item["photo"],
        "needs_ai_image": item["photo"] is None,
    }


# --------------------------------------------------------------------------- gates
def gate(post):
    """Same checks the site's own content must pass. A post is not a lesser artefact."""
    before = (len(ERRORS), len(WARNINGS))
    where = f"fb:{post['ref']}"
    for fn in (check_foreign_scripts, check_khmer_clusters, check_doubled_words,
               check_absolutes, check_hard_specs):
        fn(where, post["copy"])
    return ERRORS[before[0]:], WARNINGS[before[1]:]


def render(posts, out_path=None):
    lines = ["# CKM Facebook post queue", "",
             "> Generated by `devops/make_fb_posts.py`. Every Khmer sentence is either",
             "> already live on ckmkh.com or one of the reviewed HOOKS/QUESTIONS strings.",
             "> No model was called. Owner review happens on the zh-TW column.", ""]
    for i, p in enumerate(posts, 1):
        lines += [
            f"## {i:03d}. [{p['kind']}] {p['ref']}", "",
            f"- length: {p['chars']} Khmer characters / {p['units']} display units",
            f"- shape: {p.get('fit', '?')}  "f"({'fits the fold' if p.get('fit') == 'fold' else 'long, use as a value post' if p.get('fit') == 'long' else 'too long for one post -- split across a carousel'})",
            f"- image: {'AI prompt below' if p['needs_ai_image'] else 'existing photograph'}",
            "", "### Khmer copy", "", "```", p["copy"], "```", "",
            "### Image", "", "```", p["image"], "```", "",
            "### zh-TW for owner review", "",
            "_(fill in before publishing)_", "", "---", "",
        ]
    text = "\n".join(lines)
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        io.open(out_path, "w", encoding="utf-8", newline="\n").write(text)
    return text


def write_image_json(posts, path):
    """The batch an operator hands to an image model in one go.

    One object per post that needs an illustration, each carrying the filename the post
    expects. Generating a few hundred images once and posting daily afterwards is far
    cheaper in attention than generating one a day, and the filename is what keeps the
    two halves attached months apart.
    """
    items = [{
        "filename": p["filename"],
        "aspect_ratio": "4:5",
        "size": "1080x1350",
        "subject": p["ref"],
        "kind": p["kind"],
        "prompt": p["prompt"],
    } for p in posts if p["needs_ai_image"]]

    payload = {
        "project": "CKM",
        "platform": "Facebook",
        "purpose": "batch image generation for the zero-link Khmer post programme",
        "count": len(items),
        "brand_palette": BRAND_HEX,
        "instructions": (
            "Generate one image per item at the given aspect ratio and save it under the "
            "given filename. Photographs of food only -- no text, no logo, no watermark "
            "burned into the image. These illustrate Khmer-Chinese banquet subjects and "
            "must depict authentic Cambodian banquet reality, never a Western stock "
            "kitchen."
        ),
        "items": items,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, ensure_ascii=False, indent=2))
    return len(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", choices=sorted(SOURCES), help="one source only")
    ap.add_argument("--all", action="store_true", help="every source")
    ap.add_argument("--count", type=int, default=0, help="cap the number of posts")
    ap.add_argument("--out", help="write a markdown queue here")
    ap.add_argument("--image-json", help="write the batch image-prompt file here")
    args = ap.parse_args()

    if not args.batch and not args.all:
        ap.error("pass --batch or --all")

    items = []
    if args.all:
        # Dishes first: they are the only ones with a real photograph.
        for key in ("dishes", "faq", "quick", "seeds"):
            items += SOURCES[key]()
    else:
        items = SOURCES[args.batch]()

    if args.count:
        items = items[:args.count]

    built = [build_post(it, i) for i, it in enumerate(items)]
    posts = [p for p in built if p]
    dropped = len(built) - len(posts)
    if dropped:
        print(f"[FB] dropped {dropped} source(s): the first sentence alone overruns the fold")

    # Order by whether the copy is actually post-shaped, not by source order. Measured
    # 2026-08-23 across all 137: the 66 banquet seeds run 68-113 characters and every one
    # fits the fold, the 16 dishes mostly do, and the FAQ and quick-answer blocks sit at a
    # median of 260 and 227 -- they were written as article prose for a page. Putting the
    # short ones first means the operator spends the first several months on the material
    # that reads as a post, and the long ones wait for a carousel, which is the format
    # that suits them and also reaches best (1.6% against 1.5% for a single image).
    for p in posts:
        p["fit"] = ("fold" if p["chars"] <= POST_MAX_CHARS
                    else "long" if p["chars"] <= 250 else "carousel")
    rank = {"fold": 0, "long": 1, "carousel": 2}
    posts.sort(key=lambda p: (rank[p["fit"]], p["chars"]))
    from collections import Counter
    print("[FB] shape: " + ", ".join(f"{k}={v}" for k, v in Counter(
        p["fit"] for p in posts).most_common()))

    errs = warns = 0
    for p in posts:
        e, w = gate(p)
        errs += len(e)
        warns += len(w)
        for rule, where, _, msg in e + w:
            print(f"   [{rule}] {where}: {msg[:110]}")

    with_photo = sum(1 for p in posts if not p["needs_ai_image"])
    print(f"[FB] {len(posts)} posts | {with_photo} with a real photograph | "
          f"{len(posts) - with_photo} need an AI illustration")
    print(f"[FB] gates: {errs} errors, {warns} warnings")
    lengths = sorted(p["chars"] for p in posts)
    if lengths:
        print(f"[FB] copy length: min {lengths[0]}, median {lengths[len(lengths)//2]}, "
              f"max {lengths[-1]} Khmer characters")

    if args.out:
        render(posts, args.out)
        print(f"[FB] written: {args.out}")

    if args.image_json:
        n = write_image_json(posts, args.image_json)
        print(f"[FB] written: {args.image_json} ({n} prompts)")

    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main())

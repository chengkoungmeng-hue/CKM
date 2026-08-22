import os
import json
import time
import urllib.request
import re
import xml.etree.ElementTree as ET
import unicodedata
import hashlib
import sys
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime

sys.stdout.reconfigure(encoding='utf-8')

_cached_gemini_key = None


def get_gemini_api_key():
    """Retrieve GEMINI_API_KEY lazily from environment or .env file.

    Cached after the first resolution so subsequent calls avoid disk/env overhead.
    Kept lazy so importing date/width utility functions from this script does not
    emit misleading '(len: 0)' messages into CI logs in steps without API keys.
    """
    global _cached_gemini_key
    if _cached_gemini_key is not None:
        return _cached_gemini_key

    key = os.environ.get("GEMINI_API_KEY", "").strip().strip("\"'").strip()
    if not key and os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    key = line.strip().split("=", 1)[1].strip().strip("\"'").strip()
    _cached_gemini_key = key
    return _cached_gemini_key


# Sources are chosen to match what CKM actually cooks: Khmer heritage dishes and
# Cantonese/Teochew banquet cuisine. The previous set (Just One Cookbook, Epicurious,
# BBC Good Food) produced Palm Springs date shakes and Polish cream cake under a
# Khmer-Chinese banquet brand.
#
# Thai and Vietnamese sources are deliberately excluded. Cambodia's relations with both
# neighbours are politically sensitive and a catering brand has nothing to gain by
# publishing their cuisine. EXCLUDE_REGEX enforces this at the article level too, in case
# a source occasionally strays.
FEEDS = [
    {
        "source_name": "Auntie Emily's Kitchen",
        "category_en": "Cantonese Banquet & Home Classics",
        "category_km": "ម្ហូបចិននិងទាវជីវ",
        "url": "https://auntieemily.com/feed/"
    },
    {
        "source_name": "Christine's Recipes",
        "category_en": "Hong Kong & Cantonese Soups and Braises",
        "category_km": "ម្ហូបចិននិងទាវជីវ",
        "url": "https://en.christinesrecipes.com/feeds/posts/default?alt=rss"
    },
    {
        "source_name": "China Sichuan Food",
        "category_en": "Chinese Regional Techniques & Seasonings",
        "category_km": "គ្រឿងផ្សំនិងរសជាតិ",
        "url": "https://www.chinasichuanfood.com/feed/"
    },
    {
        "source_name": "Omnivore's Cookbook",
        "category_en": "Chinese Home Cooking & Technique",
        "category_km": "គ្រឿងផ្សំនិងរសជាតិ",
        "url": "https://omnivorescookbook.com/feed/"
    },
    {
        "source_name": "The Woks of Life",
        "category_en": "Cantonese, Shanghainese & Sichuan Family Cooking",
        "category_km": "ម្ហូបចិននិងទាវជីវ",
        "url": "https://thewoksoflife.com/feed/"
    },
    {
        "source_name": "The Hong Kong Cookery",
        "category_en": "Hong Kong Classics & Pastry Fillings",
        "category_km": "សិល្បៈអាហារអាស៊ី",
        "url": "https://www.thehongkongcookery.com/feeds/posts/default?alt=rss"
    },
    # Added 2026-08-15. Surveyed 25 candidates; this was the only one added, and the
    # only one that needed no widening of EXCLUDE_REGEX to be safe. 116 of 120 archived
    # posts survive the filter, 115 of them with bilingual titles (so slugs stay
    # descriptive), and the repertoire is CKM's own: 紅燒鮑魚海參花膠煲, 客家酿豆腐卜,
    # 糖水, 南乳炸雞翅.
    #
    # Rejected, recorded so they are not re-surveyed:
    #   christinesrecipes.com (Chinese edition) -- the SAME BLOG as the configured
    #     en.christinesrecipes.com. 20 of 25 items identical, timestamps seconds apart.
    #     Dedupe keys on source_link, which differs per edition, so every dish would
    #     have published twice.
    #   tasteasianfood.com  -- 5.9/mo and 112 archived, but heavily Malay and Indian
    #     (Nasi Minyak, Ayam Masak, Aloo Matar) which EXCLUDE_REGEX does not catch.
    #     Would need ~15 new exclusion terms; that is how the old source set ended up
    #     producing Palm Springs date shakes.
    #   anncoojournal.com   -- Western baking (pound cake, banana pie) under a banquet brand.
    #   siftandsimmer.com   -- bubble tea and bagels.
    #   chinesecookingdemystified.substack.com -- excellent technique writing, but Substack
    #     serves one page only (no archive depth) and many posts are essays rather than
    #     dishes, and the generation prompt is dish-centric ("Source dish: ...").
    #   redhousespice.com, rasamalaysia.com -- HTTP 403 to scripted fetches; a GitHub
    #     Actions IP will fare no better.
    {
        "source_name": "Huang Kitchen",
        "category_en": "Malaysian-Chinese Home & Banquet Cooking",
        "category_km": "ម្ហូបចិននិងទាវជីវ",
        "url": "https://www.huangkitchen.com/feed/"
    }
]

# Measured 2026-08-14 — effective yield after EXCLUDE_REGEX, from each feed's own
# publishing history. One article a day needs 30/month.
#
#   Omnivore's Cookbook   19.3/mo    Christine's Recipes    9.9/mo
#   The Woks of Life       7.3/mo    China Sichuan Food     3.2/mo
#   The Hong Kong Cookery  2.5/mo    ------------------------------
#                                    total                 42.2/mo
#
# Cambodia Recipe and Auntie Emily are kept despite being dormant (last posts roughly
# 6 months and 3 years old): they are the most on-brand sources in the list, their back
# catalogue is still unconsumed, and a dormant feed costs nothing but one HTTP request.
# Re-measure if the pipeline starts reporting "no new items" several days running.
#
# Re-measured 2026-08-15. Two corrections to the reading above:
#
# 1. Monthly rate is the wrong headline number. The pipeline publishes at most one item
#    a day, so what matters is whether an unseen candidate exists, not the total. A
#    Monte Carlo over these measured rates (2000 trials x 365 days, modelling each RSS
#    window as finite and items pushed out of it as permanently lost) returned ZERO
#    zero-output days, and barely touched the dormant reserve. Supply is not the
#    constraint and has not been.
#
# 2. The real fragility was concentration, and archive depth has since answered it.
#    Omnivore's Cookbook alone is 43% of arrivals; without it the same simulation gives
#    48 zero-output days a year, and without it and Christine's, 166. But MAX_FEED_DEPTH
#    now reaches ~1,124 filtered items across these feeds -- about three years of daily
#    publishing from the back catalogue alone -- so even the total loss of every active
#    source degrades slowly rather than stopping the site.

FOOD_KEYWORDS = [
    "food", "cuisine", "recipe", "recipes", "cooking", "gourmet", "restaurant", 
    "flavor", "flavors", "seafood", "dim sum", "soup", "curry", "banquet", 
    "chef", "dining", "delicacy", "ingredient", "herb", "herbs", "spice", 
    "spices", "taste", "meal", "dish", "dishes", "cake", "pie", "wine", 
    "cocktail", "dessert", "menu", "feast", "gastronomy", "khmer", "chinese", "asian",
    "餐飲", "冰淇淋", "美食", "料理", "甜點", "食材"
]

# NOTE: FOOD_REGEX is not applied anywhere — only EXCLUDE_REGEX gates the feed items.
# That is the correct behaviour now that every source is a dedicated recipe blog: a
# title-must-contain-"soup"/"recipe" rule would reject exactly the on-brand posts
# ("Typhoon Shelter Fried Crab 避風塘炒蟹", "Easy Char Siu 簡易叉燒", "Dandan Noodles 擔擔麵").
# Kept only so the keyword list is available if a general-interest source is ever added.
FOOD_REGEX = re.compile(r'(' + '|'.join(re.escape(k) for k in FOOD_KEYWORDS) + r')', re.IGNORECASE)
_EXCLUDE_TERMS = (
    # Off-topic / non-culinary
    r'crypto|fast food|burger|pizza|delivery app|flight|hotel room|brain-computer|'
    r'tech billionaire|cloud computing|leasing market|auction|stock market|movie|movies|'
    r'film|films|cinema|actor|actress|hollywood|netflix|trailer|tv show|celebrity|'
    r'director|oscar|entertainment|pub crawl|pub|bar crawl|'
    r'xbox|project scorpio|football|soccer|fans on final|swallow does not make|persuasion is often|'
    # Western dishes that do not belong under a Khmer-Chinese banquet brand
    r'cobbler|mac and cheese|hot dog|taco|bourbon|viking|cherry cake|cherry cobbler|'
    r'cherry pie|casserole|pancakes|waffles|sandwich|edinburgh|western recipe|western food|'
    r'tiramisu|croissant|brownie|cupcake|pasta|spaghetti|lasagna|risotto|gnocchi|fettuccine|macaroni|'
    r'smoothie|milkshake|frappe|slushie|parfait|ice cream|popsicle|'
    # Vietnamese — excluded on geopolitical grounds, not culinary ones
    r'vietnam|vietnamese|saigon|hanoi|da nang|hue|pho|com tam|goi cuon|banh mi|banh xeo|'
    r'banh cuon|bun bo|bun cha|cha gio|nuoc cham|nuoc mam|summer roll|rice paper roll|'
    # Thai — same reason
    r'thai|thailand|bangkok|phuket|chiang mai|isaan|som tam|tom yum|tom kha|pad thai|'
    r'khao soi|massaman|panang|larb|laab|green curry|thai basil|'
    # Japanese / Korean — off-brand for a Khmer-Chinese banquet caterer
    r'matcha|hojicha|onigiri|bibimbap|tteokbokki|kimchi|ramen|sushi|tempura'
)
# NOTE: plain "curry" is deliberately NOT excluded — Khmer red curry (ការីខ្មែរ) is a
# core CKM dish. Only the specifically Thai curry names are filtered.
def _with_inflections(terms):
    """Let each exclusion term match its singular and plural alike.

    [REGRESSION] The list was written as a mix of singulars and plurals and compiled as
    \\b(term|term|…)\\b, so the closing \\b failed against any other form and the term
    simply did not fire. Measured 2026-08-15: "Mango Chicken Summer Rolls" passed the
    filter and published, even though `summer roll` is on the list — and it is Vietnamese,
    which §15 excludes on explicit geopolitical grounds, not culinary ones. The same hole
    let through Fish Tacos, Wagyu Burgers, Almond Croissants, Fudge Brownies and, in the
    other direction, Belgian Waffle against the plural entry `waffles`.

    Seven of nine probe titles evaded the filter this way. Normalise each term to its
    stem, then match an optional -s/-es. `actress` and other -ss words are left alone so
    the stem is not mangled.
    """
    out = []
    for t in terms.split("|"):
        t = t.strip()
        if not t:
            continue
        if t.endswith("s") and not t.endswith("ss") and len(t) > 4:
            t = t[:-1]
        out.append(t + r"(?:e?s)?")
    return "|".join(out)


# NOTE: `hue` (the Vietnamese city) already carried a false-positive risk against the
# English word "hue"; the inflection suffix extends that to "hues". Left as-is because
# neither appears in a recipe title in practice, but it is the one term here where a
# wider match could misfire.
EXCLUDE_REGEX = re.compile(r'\b(' + _with_inflections(_EXCLUDE_TERMS) + r')\b',
                           re.IGNORECASE)

# Chinese dishes whose English names collide with the Western terms above. The
# 2026-08-14 run skipped its entire candidate set, and two of the seven were
# these: "Scallion Pancakes" caught by `pancakes`, and "Hong Kong Clubhouse
# Sandwich 公司三文治" caught by `sandwich`. Both came from the Chinese-language
# feeds and are squarely on brand.
#
# Deliberately narrow. This is not a way in for Western food -- the exclusions
# exist because an earlier source set produced Palm Springs date shakes under a
# Khmer-Chinese banquet brand -- only a way through for dishes that were never
# Western to begin with. Add a term here when a specific dish is misjudged, not
# when the yield feels low; the fix for low yield is another Chinese-language
# feed, not a wider sieve.
_ALLOW_TERMS = (
    r'scallion pancake|spring onion pancake|green onion pancake|cong you bing|'
    # `pancakes` in the exclusion list targets the Western breakfast stack. Chinese
    # savoury 餅 are a different food that happens to share the English word, and
    # "Crispy Corn Pancake" from a Chinese recipe blog was caught once the inflection
    # fix made `pancakes` actually fire. Japanese okonomiyaki is deliberately NOT
    # allowed through here -- it is off-brand for other reasons.
    r'corn pancake|'
    r'蔥油餅|葱油饼|三文治'
)
ALLOW_REGEX = re.compile(_ALLOW_TERMS, re.IGNORECASE)

# Dishes that plausibly appear on a Khmer-Chinese banquet table, as opposed to a
# weeknight home-cooking post. Matched against the SOURCE TITLE only, which the feeds
# write bilingually, so both the English and the Chinese name are listed. This is a
# ranking hint, never a filter — see BANQUET_FIT_BONUS_DAYS at the selection site for
# why it must stay bounded.
_BANQUET_TERMS = (
    # Banquet proteins and the dried/luxury goods a wedding menu is built around
    r'abalone|sea cucumber|fish maw|scallop|lobster|crab|prawn|shrimp|'
    r'whole fish|steamed fish|garoupa|grouper|squab|pigeon|'
    r'roast pork|roast duck|roast goose|crispy pork|suckling pig|char siu|'
    r'soy sauce chicken|white cut chicken|braised|red braised|clay pot|claypot|'
    r'shark.?fin|bird.?s nest|dried scallop|conpoy|black moss|'
    # Banquet formats and courses
    r'banquet|wedding|new year|reunion dinner|double.?boiled|poon choi|'
    r'longevity noodle|e.?fu noodle|yee mein|lotus leaf|glutinous rice|'
    r'dim sum|tong sui|sweet soup|herbal soup|stuffed tofu|wonton|'
    # The brand's own cuisine. A Cambodian dish is the most banquet-fit thing the feeds
    # can produce, and the sources do carry them; measured against the 36 published
    # source titles, four Cambodian/Khmer dishes scored no bonus at all until this line.
    r'khmer|cambodian|phnom penh|amok|'
    # Chinese names, for the bilingual feeds
    r'鮑魚|海參|花膠|瑤柱|乳豬|燒肉|叉燒|燒鵝|燒鴨|白切雞|豉油雞|紅燒|清蒸|'
    r'髮菜|伊麵|荷葉|糯米飯|盆菜|喜宴|團年|燉湯|糖水|雲吞|餛飩|釀豆腐'
)
BANQUET_REGEX = re.compile(_BANQUET_TERMS, re.IGNORECASE)


# --- Banquet seeds: the 5:2 rotation ---------------------------------------------
#
# MEASURED 2026-08-22, Search Console, 90 days (2026-05-23 -> 2026-08-20,
# sc-domain:ckmkh.com). Site totals 1,574 impressions / 36 clicks over 61 pages:
#
#     section                pages w/ impressions   impressions   clicks
#     home                                     2         1,069       29
#     blog (15 posts)                         28           282        4
#     pulse (36 posts)                        23            63        1
#
# Filtered to Cambodia — the actual market — the whole of pulse produced TWO
# impressions in ninety days (/pulse/pulse-19/ and /pulse/zucchini-garlic-sauce-pulse-03/,
# one each) and zero clicks. Only two Khmer queries carry real volume: ម្ហូបការ
# (254 impressions, 11 clicks, position 3.8) and មុខម្ហូបការ (59 / 1 / 5.2).
#
# The diagnosis is NOT that the pulse body is bad — the prompt already forces a link to
# Khmer-Chinese banquet practice, and that half works. It is that the SEED is a foreign
# home-cooking dish pulled from an RSS feed, so the TITLE is about wok technique or a
# Hong Kong pastry. The title is what ranks, and the seed decides the title. Nobody in
# Cambodia searches those strings, so the page cannot be found however well it is written.
#
# So the seed itself has to change for most of the week. Owner directive 2026-08-22:
# five banquet-topic articles and two food articles per week, one article a day.
#
# The RSS machinery below is untouched and still runs on food days: archive walking,
# parse_any_date, EXCLUDE/ALLOW_REGEX, the banquet-fit bonus and the candidate fallback
# loop all remain. What changes is that on five days out of seven the pipeline does not
# consult the network at all to choose a subject — it takes the next unused entry from
# devops/pulse_seeds.json.

# The four Khmer categories a pulse entry may carry. Three are still attached to a live
# feed above; ម្ហូបខ្មែរប្រណីត belonged to the Cambodia Recipe feed, which was pruned when
# it went dormant, and is still the category on 7 published entries. Written out here
# because the seed file has no feed to inherit a category from, and because a typo in a
# seed's category would otherwise reach the page as a new, one-off hashtag.
PULSE_CATEGORIES = (
    "ម្ហូបខ្មែរប្រណីត",
    "ម្ហូបចិននិងទាវជីវ",
    "គ្រឿងផ្សំនិងរសជាតិ",
    "សិល្បៈអាហារអាស៊ី",
)

SEED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pulse_seeds.json")

# A seed has no source URL, but source_link is the de-duplication key the whole pipeline
# matches on (and check_content.py requires the field to be non-empty). Give each seed a
# stable synthetic key in the same namespace. It is never rendered — pulse/[id].astro
# stopped rendering source_link on 2026-08-22 — and it is deliberately not http:// so that
# nothing can mistake it for a page to fetch.
SEED_LINK_PREFIX = "ckm-seed:"

# Monday. The rotation is anchored to a fixed Monday so that banquet_slot_index() is a
# pure function of the calendar and a re-run on the same day lands on the same seed.
SEED_ROTATION_EPOCH = date(2026, 8, 24)
BANQUET_DAYS_PER_WEEK = 5          # Monday-Friday banquet, Saturday-Sunday food = 5:2

# The cron fires at 20:47 UTC, which is 03:47 the NEXT day in Phnom Penh. The slot has to
# be decided on the date the article is published locally, not on the UTC date, or the
# rotation would be one day out of step with the calendar the owner reads.
PHNOM_PENH_TZ = timezone(timedelta(hours=7))

# At most three seeds are buffered per run, mirroring the candidate fallback loop the RSS
# path uses: if Gemini rejects one topic across all its attempts, the next topic is tried
# rather than the run failing. Three is what the API budget affords — see API_CALL_BUDGET.
SEED_CANDIDATE_LIMIT = 3


def publication_date(now=None):
    """The Phnom Penh calendar date this run publishes on."""
    return (now or datetime.now(timezone.utc)).astimezone(PHNOM_PENH_TZ).date()


def is_banquet_slot(day):
    """True on the five banquet days of the week (Monday-Friday)."""
    return day.weekday() < BANQUET_DAYS_PER_WEEK


def banquet_slot_index(day):
    """How many banquet slots have elapsed since the epoch, counting `day` itself.

    Total for every date, including weekends and dates before the epoch — divmod floors,
    so a date in the past yields a negative index and the caller's modulo still lands
    inside the seed list. Deterministic: the same date always returns the same index, so
    re-running a day picks the same seed.
    """
    weeks, rem = divmod(day.toordinal() - SEED_ROTATION_EPOCH.toordinal(), 7)
    return weeks * BANQUET_DAYS_PER_WEEK + min(rem, BANQUET_DAYS_PER_WEEK)


def seed_link(seed):
    """The de-duplication key for a seed. Stable for the life of the seed's id."""
    return SEED_LINK_PREFIX + seed["id"]


_SEED_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_pulse_seeds(path=SEED_FILE):
    """Read and VALIDATE devops/pulse_seeds.json. Raises on anything malformed.

    Validation is a gate, not a courtesy. The whole point of this change is that the seed
    decides the title, so a seed carrying a typo'd category, an English word or a broken
    Khmer cluster propagates straight into a published page — and pulse grows by one page
    a day, so it would keep doing so. Raising here turns the run red, which is the only
    signal that reaches a person (section 15: a failure that cannot turn a run red will
    not be noticed).

    What is checked, and why each one:
      - id / slug unique          two seeds sharing an id share a de-duplication key, so
                                  the second would be silently treated as already used.
      - slug shape                it becomes the permanent URL path segment. Section 3
                                  requires descriptive slugs; generate_seo_slug keeps only
                                  the first 7 segments, so a longer slug would be
                                  truncated into something the file does not say.
      - category in PULSE_CATEGORIES  it is rendered as a hashtag on three page types.
      - Khmer fields non-empty, free of Latin letters, and free of any script that is not
        Khmer/ASCII (find_foreign_scripts). Sections 10 and 13.

    `slug` is the one field that is deliberately Latin: it is a URL path, exactly like
    every existing pulse and blog slug, and Khmer cannot produce one.
    """
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)

    seeds = doc.get("seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("%s carries no seeds" % path)

    seen_ids, seen_slugs, problems = set(), set(), []
    for i, seed in enumerate(seeds):
        where = "seed %d (%s)" % (i, seed.get("id", "no id"))
        sid, slug = seed.get("id"), seed.get("slug")

        if not sid:
            problems.append("%s has no id" % where)
        elif sid in seen_ids:
            problems.append("%s repeats id %r" % (where, sid))
        else:
            seen_ids.add(sid)

        if not slug or not _SEED_SLUG.match(slug):
            problems.append("%s slug %r is not a lowercase hyphenated path segment"
                            % (where, slug))
        elif len(slug.split("-")) > 7:
            problems.append("%s slug %r has more than 7 segments; generate_seo_slug "
                            "would truncate it" % (where, slug))
        elif slug in seen_slugs:
            problems.append("%s repeats slug %r" % (where, slug))
        else:
            seen_slugs.add(slug)

        if seed.get("category_km") not in PULSE_CATEGORIES:
            problems.append("%s category_km %r is not one of the four published "
                            "categories" % (where, seed.get("category_km")))

        for field in ("topic_km", "angle_km"):
            value = seed.get(field)
            if not value or not isinstance(value, str):
                problems.append("%s is missing %s" % (where, field))
                continue
            if re.search(r"[A-Za-z]", value):
                problems.append("%s.%s contains a Latin letter; section 10 allows none "
                                "in Khmer copy" % (where, field))
            for hit in find_foreign_scripts(value):
                problems.append("%s.%s: %s" % (where, field, hit))

    if problems:
        raise ValueError("%s failed validation:\n  - %s"
                         % (path, "\n  - ".join(problems)))
    return seeds


def seed_candidate(seed):
    """Shape a seed like a feed candidate so one code path handles both downstream.

    `title_en` exists only for logging and for generate_seo_slug's collision handling;
    nothing English reaches the page. `pubDate` is None because a seed has no upstream
    publication date — the caller stamps the run's own timestamp.
    """
    return {
        "kind": "seed",
        "seed_id": seed["id"],
        "slug_en": seed["slug"],
        "topic_km": seed["topic_km"],
        "angle_km": seed["angle_km"],
        "title_en": seed["slug"].replace("-", " "),
        "desc_en": "",
        "link": seed_link(seed),
        "category_km": seed["category_km"],
        "pubDate": None,
    }


def select_seed_candidates(seeds, existing_links, day, limit=SEED_CANDIDATE_LIMIT):
    """The day's banquet topics, in rotation order, skipping ones already published.

    Deterministic in the date: the same date starts at the same index. Walking forward
    from there (rather than picking at random, or always taking the first unused) is what
    keeps 66 seeds from repeating inside a quarter while still tolerating a seed being
    consumed out of order by a re-run.

    Returns [] when every seed has been published, which the caller treats as a reason to
    fall through to the food path rather than as a failure.
    """
    start = banquet_slot_index(day) % len(seeds)
    out = []
    for k in range(len(seeds)):
        seed = seeds[(start + k) % len(seeds)]
        if seed_link(seed) in existing_links:
            continue
        out.append(seed_candidate(seed))
        if len(out) >= limit:
            break
    return out


def unused_seed_count(seeds, existing_links):
    """Runway signal for banquet days, the counterpart of the RSS path's queue depth."""
    return sum(1 for s in seeds if seed_link(s) not in existing_links)


def sanitize_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', text)
    return cleaned.strip()


def sanitize_source_title(text):
    """Reduce a source title to characters Hanuman can actually draw.

    [REGRESSION] `source_title_en` is rendered verbatim on the pulse detail page, under
    the label \u1794\u17d2\u179a\u1797\u1796\u178a\u17be\u1798\u17a2\u1793\u17d2\u178f\u179a\u1787\u17b6\u178f\u17b7 (pulse/[id].astro). It is stored straight from the feed,
    and feeds title their posts bilingually \u2014 so Khmer readers were served
    "Pickled Daikon \u5927\u6839\u306e\u6f2c\u7269" and "Umeboshi Onigiri \u2026 \u5c0f\u6885\u306e\u304a\u306b\u304e\u308a", whose CJK and kana
    Hanuman cannot render and which therefore reached them as tofu boxes. That is exactly
    the failure \u00a713 of AGENTS.md exists to prevent; it was simply never checked on this
    field, because the field is not one of the Khmer ones.

    Latent for as long as every source titled its posts in English alone. Adding a
    bilingual source made it the norm rather than the exception: 115 of Huang Kitchen's
    116 archived titles carry Chinese, as do 13 of The Hong Kong Cookery's 23.

    Latin, digits and ordinary punctuation survive; everything else is dropped. The
    untouched original is always recoverable from `source_link`, and slugs are unaffected
    because they are assigned once at insert and never recomputed.
    """
    if not text:
        return ""
    kept = "".join(ch for ch in text
                   if ord(ch) < 0x0250            # Latin, incl. accented
                   or ch in "\u2018\u2019\u201c\u201d\u2013\u2014\u2026")
    return re.sub(r"\s{2,}", " ", kept).strip(" -\u2013\u2014|,;:")

def generate_seo_slug(title_en, item_id, taken=()):
    """Build a PERMANENT slug for a pulse item.

    The slug must never encode the item's position in the list. It used to be
    f"{words}-{item_id}", and because item_id was reassigned by list position on
    every run, adding one article silently rewrote all 20 URLs — every previously
    indexed pulse URL 404'd the next day while notify_indexing.py submitted the
    new ones to Google and Bing. Slugs are permanent identifiers: assign once,
    never recompute.

    Collisions are resolved with a short deterministic hash of the source link,
    never with a positional counter.
    """
    nfkd_form = unicodedata.normalize('NFKD', title_en or "")
    ascii_text = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', ascii_text).strip().lower()
    words = [w for w in re.sub(r'[\s-]+', '-', cleaned).split('-') if w][:7]
    base = '-'.join(words)
    if not base:
        return item_id
    if base not in taken:
        return base
    suffix = hashlib.sha1((title_en or item_id).encode('utf-8')).hexdigest()[:6]
    return f"{base}-{suffix}"


def set_action_output(**kwargs):
    """Expose results to the GitHub Actions job so later steps can branch on them.

    The pipeline previously ran cache-purge + IndexNow + GSC submission with
    `if: always()`, so it pinged the search engines every single day even when
    nothing had changed and even when generation had failed. That is a wasted
    IndexNow quota and a repeated "this changed" signal for URLs that did not.
    """
    out = os.getenv("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as fh:
        for key, value in kwargs.items():
            fh.write("%s=%s\n" % (key, value))


def next_pulse_id(existing):
    """Return the next never-before-used pulse id.

    Monotonic: ids are never reused and never shift, so /pulse/pulse-NN/ stays
    pointing at the same article for the life of the site.
    """
    highest = 0
    for item in existing:
        m = re.match(r"^pulse-(\d+)$", str(item.get("id", "")))
        if m:
            highest = max(highest, int(m.group(1)))
    return "pulse-%02d" % (highest + 1)


def parse_any_date(raw):
    """Parse a feed timestamp in either format the sources actually emit.

    WordPress feeds emit RFC 2822 ("Fri, 14 Aug 2026 14:13:27 +0000"). Blogspot emits
    ISO 8601 ("2026-08-11T22:04:01.612-07:00"), and the extraction loop keeps the LAST
    matching element, which on Blogspot is the Atom <updated> field — so even The Hong
    Kong Cookery, whose feed carries a perfectly good RFC 2822 <pubDate>, arrives here
    as ISO. parsedate_to_datetime rejects ISO outright.

    Measured 2026-08-15: 47 of the 88 queued items (Christine's Recipes 24, The Hong
    Kong Cookery 23) failed to parse and collapsed to datetime.min, which sorted both
    Blogspot sources to the back of the queue for a parsing failure rather than for
    their age.

    Always returns a timezone-aware datetime. Unrecognised input sorts last rather
    than raising, because sorted() raises mid-sort and takes the whole run with it.
    """
    if not raw or not isinstance(raw, str):
        return datetime.min.replace(tzinfo=timezone.utc)
    for parse in (parsedate_to_datetime, datetime.fromisoformat):
        try:
            d = parse(raw.strip())
        except Exception:
            continue
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    return datetime.min.replace(tzinfo=timezone.utc)


# Gemini occasionally returns Khmer text with Thai, Chinese or Japanese fragments
# spliced in (e.g. หัวใจ, วัฒนธรรม, 環境的控制與使用醬料調配提升風味). Hanuman cannot
# render those, so they ship as tofu boxes to a Khmer-reading audience. Reject the
# generation rather than commit it.
# WHITELIST, not blacklist. An enumerated blacklist of Thai/CJK/Kana/Devanagari let
# Hebrew through — "עוד" and "צ" shipped inside Khmer words on a generated article,
# because nobody thought to list Hebrew. There is no end to the scripts a model can
# emit, so allow only what this site legitimately contains and reject everything else.
#
# Allowed: Khmer, Khmer symbols, ASCII (digits, punctuation, the rare brand name),
# and standard whitespace/typographic punctuation.
ALLOWED_RANGES = [
    (0x1780, 0x17FF),   # Khmer
    (0x19E0, 0x19FF),   # Khmer symbols
    (0x0020, 0x007E),   # printable ASCII
    (0x00A0, 0x00FF),   # latin-1 supplement (é, ñ in source titles, « » quotes)
    (0x2000, 0x206F),   # general punctuation (…, —, quotes)
    (0x2190, 0x21FF),   # arrows (used in markdown tables)
    (0x2500, 0x25FF),   # box drawing / geometric (■ bullets in prose)
]
ALLOWED_CHARS = set("\n\r\t")


def _script_name(cp):
    for lo, hi, name in (
        (0x0E00, 0x0E7F, "Thai"), (0x0900, 0x097F, "Devanagari"),
        (0x0980, 0x09FF, "Bengali"), (0x4E00, 0x9FFF, "CJK"),
        (0x3040, 0x30FF, "Kana"), (0x0590, 0x05FF, "Hebrew"),
        (0x0600, 0x06FF, "Arabic"), (0x0400, 0x04FF, "Cyrillic"),
        (0xAC00, 0xD7AF, "Hangul"), (0x0370, 0x03FF, "Greek"),
    ):
        if lo <= cp <= hi:
            return name
    return "U+%04X" % cp


# Gemini's Khmer is structurally contaminated with Thai — Khmer and Thai share a great
# deal of Indic-derived vocabulary and the model interchanges them. Prompting does not
# fix it: three consecutive attempts, with the offending words named explicitly in the
# prompt, all came back with Thai. So repair deterministically in code.
#
# Longest-first: multi-word phrases must be replaced before their constituent words.
THAI_TO_KHMER = [
    ("。", "។"),            # CJK full stop -> Khmer khan (recurs often)
    ("，", "។"),            # CJK comma -> Khmer khan
    ("รากผักชี", "ឬសជីវ៉ាន់ស៊ុយ"),   # coriander root
    ("วัฒนธรรม", "វប្បធម៌"),         # culture
    ("ผักชี", "ជីវ៉ាន់ស៊ុយ"),          # coriander
    ("หัวใจ", "បេះដូង"),             # heart
    ("จากการ", "ពីការ"),             # from the act of
    ("ช่วย", "ជួយ"),                 # to help
    ("ความ", "ភាព"),                 # -ness (nominaliser)
    ("การ", "ការ"),                  # act of  (Thai การ -> Khmer ការ)
    ("และ", "និង"),                  # and
    ("ของ", "របស់"),                 # of
    ("ใน", "ក្នុង"),                  # in
    ("ที่", "ដែល"),                   # that/which
    ("เป็น", "ជា"),                   # to be
    ("มี", "មាន"),                    # to have
]


def repair_khmer(text):
    """Replace recurring Thai fragments with their Khmer equivalents.

    Anything left over after this is genuinely unknown and must be rejected — we do not
    blind-strip foreign characters, because deleting a word from the middle of a sentence
    leaves grammatically broken Khmer that reads worse than tofu boxes.
    """
    if not isinstance(text, str):
        return text
    for thai, khmer in THAI_TO_KHMER:
        text = text.replace(thai, khmer)
    return text


def repair_khmer_deep(value):
    if isinstance(value, list):
        return [repair_khmer_deep(v) for v in value]
    return repair_khmer(value)


def find_foreign_scripts(*texts):
    """Return every character that is not Khmer, ASCII or standard punctuation."""
    hits = []
    for text in texts:
        for chunk in (text if isinstance(text, list) else [text]):
            if not isinstance(chunk, str):
                continue
            for i, ch in enumerate(chunk):
                if ch in ALLOWED_CHARS:
                    continue
                cp = ord(ch)
                if any(lo <= cp <= hi for lo, hi in ALLOWED_RANGES):
                    continue
                hits.append("%s %r near: %s"
                            % (_script_name(cp), ch, chunk[max(0, i - 15):i + 10]))
    return hits

# Restored 2026-08-22, later the same day, and this comment replaces the tombstone that
# stood here for a few hours.
#
# What was removed in the morning was not the fetch — it was an UNCREDITED fetch. Thirty
# five photographs from seven recipe blogs sat in public/images/pulse/ with no licence,
# no credit and no way for a rights holder to find anyone to ask. Deleting the fetch
# removed the exposure, and it also removed the only thing that made a pulse entry look
# like an article about something.
#
# It comes back with the four things that were missing, and it is the four things, not
# the fetch, that decide whether this is defensible:
#
#   1. A CREDIT. The entry records image_source_link, and the page renders the source
#      alongside the photograph. check_content.py's check_pulse_image() makes a rehosted
#      photograph without that link an ERROR, so an uncredited one cannot reach the
#      build again — the morning's state is now unreachable rather than merely undone.
#   2. A LOCAL COPY. rehost_source_image() downloads and re-encodes; nothing hotlinks
#      the source's server, and a takedown is a file deletion we control.
#   3. COMMENTARY, NOT RESTATEMENT. The basis for using someone else's photograph is
#      that the page comments on the subject rather than reproducing the source's work.
#      Google's scaled-content-abuse policy names TRANSLATING and does not name
#      commentary, which is the same distinction from the other direction. So the
#      generator now rejects output that takes a recipe's shape — see RECIPE_STEP_LINE.
#   4. rel="nofollow" on the outbound credit link (the page component's side).
#
# Restored verbatim from 9acf00a^ rather than rewritten, so the tier order is the one
# that was actually measured against these feeds: media:content or enclosure first,
# then an <img> in the description, then the page's og:image. Only the third tier costs
# an HTTP request, and it runs on the selected candidates only (section 15).
#
# `fallback` is now "" at every call site. It used to be a rotating blog image, which
# put a photograph of a CKM dish on an article about somebody else's — an unrelated
# picture presented as the subject. An empty return means "no photograph", and the
# caller draws the entry's own share card instead.
def extract_image_multitier(item, fallback, item_link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    if item is not None:
        for elem in item:
            if 'content' in elem.tag or 'thumbnail' in elem.tag or 'enclosure' in elem.tag:
                img_url = elem.attrib.get('url', '')
                if img_url and img_url.startswith("http"):
                    return img_url
        for elem in item:
            if 'encoded' in elem.tag or 'description' in elem.tag or 'summary' in elem.tag:
                html_text = elem.text or ""
                m = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif))["\']', html_text, re.IGNORECASE)
                if m:
                    return m[0]

    if item_link and item_link.startswith("http"):
        try:
            req = urllib.request.Request(item_link, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
            if not m:
                m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html)
            if m and m.group(1).startswith("http"):
                return m.group(1)
        except Exception:
            pass

    return fallback


def verify_live_url(url):
    if not url or not url.startswith("http"):
        return False
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in (200, 301, 302)
    except Exception as e:
        if "403" in str(e) or "406" in str(e) or "301" in str(e) or "302" in str(e):
            return True
        return False

# --- Gemini call budget ---------------------------------------------------------
#
# The old structure nested two loops: 4 models x 4 attempts inside call_gemini_api_robust,
# and the content-quality retry called it 3 times. Worst case that is 48 requests in one
# run, against a 20 requests/day cap on the Flash tier. It would have exhausted the quota
# on any bad day and then silently produced nothing.
#
# Measured quotas (2026-08-14):
#   gemini-3.7-flash        5 RPM / 250K TPM /  20 RPD
#   gemini-3.6-flash        5 RPM / 250K TPM /  20 RPD
#   gemini-3.5-flash        5 RPM / 250K TPM /  20 RPD
#   gemini-3.5-flash-lite  15 RPM / 250K TPM / 500 RPD
#
# Design: one model per quality-attempt, walking DOWN the ladder. Each model gets a
# single retry, and only for 429/503 (rate limit / overloaded) — every other failure
# moves straight to the next model instead of burning three more requests on it.
# Flash Lite is last because its 500/day cap cannot realistically run out, so the
# pipeline always has a working fallback even if every Flash tier is exhausted.
#
# Worst case per run: 4 models x 2 = 8 requests. Typical: 1.
# Order is by MEASURED reliability, not by version number. Across 5 generations on
# 2026-08-14, gemini-3.7-flash was rate-limited or unavailable on every single attempt
# and gemini-3.6-flash then succeeded every time — so leading with 3.7 spent two wasted
# requests before every article. 3.6 first cuts a generation from 3 calls to 1.
# 3.7 stays in the ladder so the pipeline picks it up again once it frees capacity.
# Re-measure occasionally; this order is an observation, not a permanent truth.
#
# Re-measured 2026-08-15 from the last three production run logs, and the picture has
# already inverted — read the paragraph above as history, not as current fact:
#
#   2026-08-14 18:47   [gemini-3.6-flash] accepted (call 1)
#   2026-08-14 21:05   [gemini-3.6-flash] unavailable x2 -> [gemini-3.7-flash] accepted
#   2026-08-15 02:52   [gemini-3.6-flash] rate-limit x1  -> [gemini-3.6-flash] accepted
#
# So 3.6 was rate-limited or unavailable in two runs of three, which is the opposite of
# what was observed on 2026-08-14, and 3.7 — described above as the unreliable one — is
# what caught the run 3.6 dropped. End-to-end failure rate is still 0%.
#
# The order is deliberately NOT changed on three samples. The ladder exists precisely so
# that a model going soft is absorbed rather than fatal, and that is exactly what these
# logs show it doing. Change the order only on a measured, sustained shift.
#
# Trimmed to two rungs on 2026-08-22 (owner directive). The arithmetic that follows is
# the part worth keeping straight, because the ladder's length and API_CALL_BUDGET are
# the same knob seen from two ends:
#
#   worst case per candidate = sum over quality-attempts of (rungs remaining x 2 subcalls)
#     4 rungs: attempt1 4x2 + attempt2 3x2 + attempt3 2x2 = 18 calls
#     2 rungs: attempt1 2x2 + attempt2 1x2 + attempt3 1x2 =  8 calls
#
# So under the unchanged budget of 25 the shorter ladder covers THREE candidates fully
# where the longer one covered one and a fraction. That is why SEED_CANDIDATE_LIMIT is 3:
# on a banquet day the fallback loop can genuinely try all three topics without the budget
# cutting it off mid-way. The RSS path still buffers 5 candidates and can still be stopped
# by the budget at the fourth — unchanged behaviour, and acceptable, because a food-day
# candidate that fails is followed by another one tomorrow.
#
# Typical cost is still 1 call. The budget bites only on a day when the model is refusing
# everything, which is exactly when it should.
#
# The down-walking retry still holds with two rungs. call_gemini_api_robust slices
# MODEL_LADDER[min(start, len-1):], so attempt 1 starts at 3.7, attempt 2 at 3.6, and
# attempt 3 clamps to 3.6 — the floor, not a restart at the top. The property the rule
# protects is that a rejection never sends the same prompt back to the model that just
# got it wrong while a lower rung is still untried; that is intact.
MODEL_LADDER = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]
API_CALL_BUDGET = 25          # hard ceiling for a single pipeline run

# The old gate was 450 characters — far below anything the model has ever returned
# (real output runs ~1,900), so it never rejected a single thin response. Set it where
# it actually bites: below this, the piece cannot be carrying four developed sections.
MIN_CONTENT_CHARS = 1200

# The prompt asks for "exactly 4 sections, each with its own descriptive Khmer
# subheading", and nothing checked whether that arrived. Measured 2026-08-15 across the
# six entries generated since the prompt was rewritten: only ONE carried four
# subheadings, the other five carried none. Length and script purity were gated, so a
# structurally flat wall of text passed every check and published.
#
# This is the same lesson as the length gate: an instruction in the prompt is a request,
# and a request the model can decline is not a standard. Anything the output must have
# needs a gate, or it holds only when the model feels like it.
MIN_CONTENT_SECTIONS = 4
SECTION_HEADING = re.compile(r"^\s{0,3}#{2,4}\s+\S", re.M)

# --- The commentary gate ---------------------------------------------------------
#
# What this page is, in one sentence: a Khmer-Chinese banquet caterer's COMMENTARY on a
# dish, not a restatement of the source article. That distinction carries two loads at
# once, and both of them are the reason a gate exists rather than a line in the prompt.
#
#   Value: Google's scaled-content-abuse policy names "scraping feeds … and applying
#   automated transformations such as synonymising or TRANSLATING" as low value. It
#   names translating. It does not name commentary. A pipeline that publishes one
#   machine-written page a day is on the wrong side of that line the moment its output
#   is a restatement of its input.
#   Licence: the basis for rehosting the source's photograph (see extract_image_multitier)
#   is that the page comments on the subject. If the body is the source's recipe in
#   Khmer, the photograph is being used to illustrate a copy, and the argument collapses.
#
# So the shape has to be checked, and the clearest machine-detectable signal of
# restatement is that the body has taken a RECIPE's form: a numbered step sequence, or a
# list of ingredients with quantities. Neither belongs in commentary — a caterer writing
# about why a technique works does not tell the reader to add two tablespoons of sugar.
#
# Calibrated 2026-08-22 against all 36 entries live in src/data/pulseData.json: ZERO
# would be rejected, at either threshold, so the gate does not fire on the commentary the
# site already publishes. Four synthetic recipe-shaped controls (Khmer numbered steps,
# Latin numbered steps, Khmer ingredient list, Latin ingredient list) are all rejected.
# Three near-miss controls pass: a sentence quoting a guest count, a piece whose four
# `### ១.`-style subheadings are numbered, and a markdown comparison table — the last two
# matter because section 14 REQUIRES numbered subheadings and a comparison table, so a
# gate that fired on either would be unusable.
#
# The heading case is what makes the anchor non-negotiable: `### ១. បច្ចេកទេស…` is the
# house style, so the numeral must be at the START of the line for it to count as a step.
# A markdown heading begins with '#', so it can never match.
RECIPE_FORM_MIN_LINES = 3
RECIPE_STEP_LINE = re.compile(
    r"^\s{0,3}(?:[0-9]{1,2}|[០-៩]{1,2})\s*[.)។៖]\s+\S", re.M)

# A measurement unit, Khmer or Latin. Deliberately units of MASS, VOLUME and COUNT only:
# ម៉ោង (hours), នាទី (minutes) and នាក់ (guests) are excluded because a duration or a head
# count is ordinary planning commentary, and where it is a hard spec, section 11's
# check_hard_specs already covers it — that is a different rule with a different severity.
_RECIPE_UNIT = (
    r"(?:ក្រាម"                    # gram
    r"|គីឡូ(?:ក្រាម)?"           # kilogram, and the common misspelling below it
    r"|គីលូ(?:ក្រាម)?"
    r"|មីលីលីត្រ"          # millilitre
    r"|លីត្រ"                    # litre
    r"|ស្លាបព្រា"              # spoon
    r"|ពែង"                        # cup
    r"|កែវ"                        # glass
    r"|ដុំ"                        # lump / piece
    r"|គ្រាប់"                    # seed / piece
    r"|mls?|kg|g|tbsp|tsp|cups?|oz|lbs?)")

# The negative lookahead covers LATIN only, on purpose. It stops the bare "g" and "l"
# alternatives matching the first letter of an ordinary English word after a numeral.
# It must NOT cover Khmer: the tablespoon is written ស្លាបព្រាបាយ -- the spoon unit with a
# word appended -- so a Khmer lookahead would reject the single most common unit in a
# Khmer ingredient list, which is precisely what this gate is looking for.
RECIPE_QTY_LINE = re.compile(
    r"^\s{0,3}[-*•·]?\s*[^\n]{0,40}?"
    r"(?:[0-9]+(?:[.,][0-9]+)?|[០-៩]+)\s*" + _RECIPE_UNIT
    + r"(?![A-Za-z])", re.M)


def recipe_form_hits(text):
    """(numbered step lines, quantity lines) — the two shapes a recipe takes."""
    return (len(RECIPE_STEP_LINE.findall(text or "")),
            len(RECIPE_QTY_LINE.findall(text or "")))

# Pulse titles reach the search result exactly like article titles do, so they answer to
# the same budget — and it is measured in RENDERED WIDTH, not len(). Khmer base consonants
# are nearly as wide as CJK while 22 of its codepoints have zero advance width, so counting
# characters is wrong in both directions.
#
# display_width is IMPORTED rather than reimplemented. The per-codepoint table it uses was
# measured in a browser and lives in exactly one place; a second copy here would drift from
# the checker and the two would disagree about what passes.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_content import display_width  # noqa: E402

# Each rejection tells the model what actually went wrong. Keyed by reject_reason so a
# new rejection cannot silently inherit another one's explanation.
RETRY_GUIDANCE = {
    "generation-failed":
        "It did not meet the output rules.",
    "generation-too-short":
        "The content_km field was truncated or too short. Emit the full 450-600 Khmer "
        "words as valid JSON, and do not stop early.",
    "generation-unstructured":
        "The content_km field did not contain four markdown subheadings. Format each of the "
        "four sections with a line starting with '### ' followed by a descriptive Khmer title.",
    "foreign-script-in-output":
        "It contained non-Khmer characters. Every character of every Khmer field must be "
        "Khmer script. Check each word before you emit it.",
    "title-too-long":
        "The title was too long for a Google search result. Make title_km markedly "
        "shorter -- Khmer consonants render wide, so cut words, do not just trim.",
    "english-in-output":
        "It contained English words in Khmer copy. Write the dish name in Khmer script; "
        "do not add the English name in brackets.",
    "summary-too-long":
        "The summary was too long for a Google snippet. Cut it down -- state the technique "
        "and drop decorative adjectives.",
    "repeated-opener":
        "The title or summary opened with the same phrase as other published entries. Start "
        "it a different way -- name the dish, lead with the ingredient, or ask a question.",
    "recipe-form-in-output":
        "It was written as a RECIPE, not as commentary. Remove every numbered step and "
        "every ingredient line with a quantity. This page is a caterer's commentary on "
        "the dish for a Cambodian banquet audience: explain why the technique works, "
        "what it costs to hold at a banquet's scale, and how a Khmer-Chinese wedding "
        "table serves it. Do not restate the source's method.",
    "title-missing-demand-root":
        "The title did not contain any of the Khmer words Cambodian readers actually "
        "search for. Rewrite title_km so it contains one of ម្ហូបការ, មុខម្ហូប or ពិធី "
        "written exactly that way. Keep the whole title short, and do NOT put that word "
        "at the very start -- the opening of the title is checked against every "
        "already-published entry as well.",
}

# --- The title gate --------------------------------------------------------------
#
# Section 15: an instruction in the prompt is a request; only a gate is a standard. The
# prompt below asks for a title carrying a term Cambodian readers search for, and asking
# is what the four-subheading requirement did for six entries before MIN_CONTENT_SECTIONS
# existed — honoured once out of six.
#
# These three roots are the ones MEASURED to carry volume in Cambodia over the 90 days to
# 2026-08-20 (the block above FEEDS has the numbers): ម្ហូបការ at 254 impressions and
# ម្ហូបការ's parent forms, មុខម្ហូបការ at 59, and ពិធី as the head of the occasion terms the
# banquet seeds are built around. Note ម្ហូបការ is a substring of មុខម្ហូបការ and មុខម្ហូប of
# មុខម្ហូបការ, so a title naming the full phrase satisfies the gate several times over —
# that is intended, not a bug.
#
# Cost against the 60-unit title budget, measured with display_width: ម្ហូបការ is 7.1
# units, មុខម្ហូប 7.5, ពិធី 3.6. A real 50-unit Khmer title has room for any of them.
#
# FOOD-SLOT DAYS ARE EXEMPT. A recipe piece about a braise is not about ម្ហូបការ, and
# forcing the word in would produce a title that misdescribes its own page — the intent
# mismatch section 18 records for /blog/01-…, where an exactly-matching title took 0
# clicks from 48 impressions. A dishonest title is worse than an unfound one.
# Measured in Search Console over 90 days to 2026-08-20, Cambodia only:
#   ម្ហូបការ    254 impressions, 11 clicks, position 3.8
#   មុខម្ហូបការ   59 impressions,  1 click,  position 5.2
# Those two are the only Khmer strings on this site with demonstrated volume, and
# both contain ម្ហូប. ពិធី is NOT in that class -- it appears only inside
# ពិធីឡើងផ្ទះ and ពិធីឡើងគេហដ្ឋានថ្មី at one impression each -- so it is accepted
# only alongside a food term. Twenty-eight of the 66 seeds are occasion topics
# whose natural title carries ពិធី and nothing else; letting that alone satisfy
# the gate would pass titles with no catering term at all, which is the intent
# mismatch section 18 records for /blog/01- (exact keyword match, 48 impressions,
# zero clicks).
TITLE_FOOD_ROOT = "ម្ហូប"
TITLE_STRONG_ROOTS = ("ម្ហូបការ", "មុខម្ហូប")
TITLE_OCCASION_ROOT = "ពិធី"


def title_carries_demand(title):
    """A banquet-day title must be findable: either a measured catering term, or
    an occasion term paired with a food term. An occasion alone is not enough."""
    if any(root in title for root in TITLE_STRONG_ROOTS):
        return True
    return TITLE_OCCASION_ROOT in title and TITLE_FOOD_ROOT in title

PULSE_TITLE_MAX_UNITS = 60
PULSE_SUMMARY_MAX_UNITS = 155
PULSE_OPENER_PREFIX = 10
PULSE_OPENER_CAP = 2
_api_calls_made = 0


def _gemini_once(prompt, model, timeout=45):
    """Exactly one request. Returns (text, error_kind). No internal retry."""
    global _api_calls_made
    if _api_calls_made >= API_CALL_BUDGET:
        return None, "budget-exhausted"
    _api_calls_made += 1

    api_key = get_gemini_api_key()
    # The key travels in the x-goog-api-key header, not `?key=`. Both authenticate, but a
    # key in the query string reaches proxy and access logs, and the `except` below turns
    # exceptions into strings — several urllib errors carry the request URL, which would
    # print the key straight into the CI log.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            res = json.loads(resp.read().decode("utf-8"))
        return res["candidates"][0]["content"]["parts"][0]["text"].strip(), None
    except Exception as e:
        msg = str(e)
        if "429" in msg:
            return None, "rate-limit"
        if "503" in msg or "500" in msg or "timed out" in msg.lower():
            return None, "unavailable"
        return None, msg[:80]


def call_gemini_api_robust(prompt, min_content_len=300, start=0):
    """Walk the model ladder until one returns usable JSON. Budget-bounded.

    `start` skips the first N models. The content-quality retry loop passes the attempt
    number, so attempt 2 begins one rung down the ladder instead of asking the same
    model to correct work it just got wrong. Every rejection used to restart at
    MODEL_LADDER[0], and since gemini-3.6-flash reliably returns *something*, all three
    attempts landed on the same model: a Khmer-quality regression in that one model was
    therefore permanent and unrecoverable, on a provider-side update with no warning.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        print("ERROR: GEMINI_API_KEY is missing!", flush=True)
        return None

    for model in MODEL_LADDER[min(start, len(MODEL_LADDER) - 1):]:
        for sub in range(2):                      # one retry, transient failures only
            text, kind = _gemini_once(prompt, model)

            if kind == "budget-exhausted":
                print(f"API budget of {API_CALL_BUDGET} calls reached — stopping.", flush=True)
                return None

            if text:
                try:
                    parsed = json.loads(text.replace("```json", "").replace("```", "").strip())
                    if len(parsed.get("content_km", "")) >= min_content_len:
                        print(f"[{model}] accepted (call {_api_calls_made}).", flush=True)
                        return text
                    print(f"[{model}] content too short — next model.", flush=True)
                except Exception:
                    print(f"[{model}] unparseable JSON — next model.", flush=True)
                break                             # a bad answer is the model's fault, move on

            if kind in ("rate-limit", "unavailable") and sub == 0:
                wait = 8 if kind == "rate-limit" else 4
                print(f"[{model}] {kind} — retrying once in {wait}s.", flush=True)
                time.sleep(wait)
                continue

            print(f"[{model}] {kind} — falling back to next model.", flush=True)
            break

    print("All models exhausted without a usable response.", flush=True)
    return None


# --- Feed archive depth ---------------------------------------------------------
#
# A feed's default URL returns only its most recent page — 10 items for the WordPress
# sources, 25 for the Blogspot ones, 99 in total. That is ample while a source is still
# publishing, and worth nothing once it stops. It is also how this pipeline dies: not
# with an error, but one feed going quiet at a time until no unseen item is left, with
# every run still reporting success.
#
# Both platforms expose their archives. Measured 2026-08-15, walking 12 pages of each
# of the seven configured feeds: 1,380 items, 1,124 surviving EXCLUDE_REGEX — roughly
# 11x the first-page-only depth, and about three years of daily publishing from the
# back catalogue alone, before counting anything published from today onward. The walk
# was truncated at 12 pages, so the true depth is greater.
#
# Depth is reached LAZILY. Page 0 of every feed is fetched first and is enough on an
# ordinary day; the pipeline only walks deeper when a shallower pass turned up nothing
# unseen. So the common case costs exactly what it costs today.
FEED_PAGE_SIZE = 25
MAX_FEED_DEPTH = 12


def paginated_feed_url(base, page):
    """The URL for page `page` of a feed's archive. Page 0 is the feed's own URL.

    Returns None when the feed's platform is not recognised, in which case that source
    simply contributes its first page and nothing deeper.
    """
    if page == 0:
        return base
    if "/feeds/posts/default" in base or "blogspot" in base:      # Blogspot / Atom
        sep = "&" if "?" in base else "?"
        return "%s%sstart-index=%d&max-results=%d" % (
            base, sep, 1 + page * FEED_PAGE_SIZE, FEED_PAGE_SIZE)
    stripped = base.rstrip("/")
    if stripped.endswith("/feed"):                                # WordPress
        return "%s/?paged=%d" % (stripped, page + 1)
    return None


def fetch_feed_page(feed, page, seen_links):
    """Parse one page of one feed. Exactly one HTTP request, and no per-item requests.

    verify_live_url is not called here. It used to run for every candidate — up to two
    extra HTTP requests each, ~188 per run to publish a single article — and it is only
    ever needed for the ONE item that actually gets published. It runs at selection time
    instead, which is what makes walking the archives affordable at all.

    The raw XML element IS carried on the candidate, as `_xml_item`. That is what lets
    extract_image_multitier mine media:content and the description for a photograph at
    selection time without going back to the network — the two cheap tiers cost nothing
    once the page is already parsed, and only the og:image tier needs a request. The key
    is prefixed with an underscore because it is working state: it is never copied into
    the entry written to pulseData.json.
    """
    url = paginated_feed_url(feed["url"], page)
    if url is None:
        return []

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
    except Exception as e:
        # A dead page deep in an archive is ordinary and must not be fatal; a dead
        # page 0 is worth saying out loud, because that is a source going away.
        if page == 0:
            print(f"Error fetching feed {feed['url']}: {e}", flush=True)
        return []

    items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    out = []
    for item in items:
        title = ""
        for child in item:
            if child.tag.endswith("title") and child.text:
                title = child.text.strip()
                break

        link = ""
        for child in item:
            if child.tag.endswith("link"):
                if child.text and child.text.strip().startswith("http"):
                    link = child.text.strip()
                elif "href" in child.attrib and child.attrib["href"].startswith("http"):
                    link = child.attrib["href"].strip()
        if not link:
            guid = item.find("guid") or item.find("{http://www.w3.org/2005/Atom}id")
            if guid is not None and guid.text and guid.text.strip().startswith("http"):
                link = guid.text.strip()

        if not link or not link.startswith("http") or link in seen_links or not title:
            continue

        if EXCLUDE_REGEX.search(title) and not ALLOW_REGEX.search(title):
            continue

        desc_text = ""
        pubDate = ""
        for child in item:
            tag = child.tag.lower()
            if "desc" in tag or "summary" in tag or "content" in tag:
                desc_text += " " + (child.text or "")
            elif "date" in tag or "published" in tag or "updated" in tag:
                pubDate = child.text or pubDate

        seen_links.add(link)
        out.append({
            "title_en": title,
            "desc_en": desc_text[:400],
            "link": link,
            "pubDate": pubDate or "Sun, 09 Aug 2026 12:00:00 +0000",
            "category_km": feed["category_km"],
            "_depth": page,
            "_xml_item": item,
        })
    return out


def fetch_verified_gourmet_rss_items(existing_links=frozenset(), max_depth=MAX_FEED_DEPTH):
    """Collect candidates, going deeper into the archives only when it is necessary.

    Returns (candidates, depth_reached). Stops as soon as at least one candidate is
    unseen, so a healthy day costs one HTTP request per feed — exactly what it cost
    before archive depth existed.
    """
    collected = []
    seen_links = set()

    for page in range(max_depth):
        for feed in FEEDS:
            collected.extend(fetch_feed_page(feed, page, seen_links))

        if page == 0 and not collected:
            # Not "nothing new" — nothing AT ALL. Every feed failed to yield a single
            # item, which is a DNS, TLS, timeout or blocked-runner problem, not an
            # editorial one. These two states used to emit the same reason string, so a
            # total infrastructure outage was indistinguishable from a quiet day. Return
            # immediately rather than walking 11 more pages of the same failure.
            print("::error::Every feed returned zero items on its first page. This is a "
                  "fetch failure, not an empty backlog.", flush=True)
            return collected, page, False

        unseen = [c for c in collected if c["link"].strip() not in existing_links]
        if unseen:
            if page > 0:
                print(f"Nothing unseen on the recent pages — reached archive depth "
                      f"{page} to find {len(unseen)} candidate(s).", flush=True)
            return collected, page, True

    print(f"Walked all {max_depth} archive pages of every feed and found nothing "
          f"unseen. The back catalogue is exhausted.", flush=True)
    return collected, max_depth, True

def render_pulse_cards(items):
    """Draw each entry's share card and point its image_url at the result.

    Renamed 2026-08-22 from sync_and_download_images, which no longer described
    anything it did: nothing is downloaded any more. The old body fetched the source
    blog's photograph over HTTP, re-encoded it to WebP and rehosted it under
    public/images/pulse/ — an unlicensed, uncredited copy of a third party's photograph
    on a commercial site. devops/render_pulse_card.py draws a 1200x675 PNG from the
    entry's own Khmer text instead, so nothing external is reproduced.

    write_card() and card_filename() are imported rather than reimplemented: the card's
    layout, its palette and its cluster-safe Khmer wrapping live in exactly one place,
    and a second copy here would drift from the one the --all rebuild uses.

    The import is deliberately LAZY. check_pulse_health.py imports parse_any_date from
    this module, and render_pulse_card.py pulls in Pillow at its own module scope; a
    top-level import here would make Pillow a hard requirement of merely importing this
    file. That is the same reasoning as get_gemini_api_key's lazy key lookup.

    Idempotent: an entry whose card already exists on disk and is already referenced is
    left alone, so a run does not rewrite forty PNGs and churn their mtimes into the
    commit. Returns the list of entries whose card could NOT be written, so the caller
    can refuse to publish an entry that would ship a 404 og:image (AGENTS.md section 6).
    """
    from render_pulse_card import OUT_DIR as CARD_DIR, card_filename, write_card

    os.makedirs(CARD_DIR, exist_ok=True)
    failed = []
    for item in items:
        item_id = item.get("id", "?")

        # An entry illustrated by a rehosted source photograph keeps it. The card is the
        # fallback for entries that have no photograph to show — every banquet-seed day,
        # which has no source at all, and any feed day whose source yielded no usable
        # image. Without this guard the card would be drawn over the photograph on the
        # very next run, because the loop below treats "image_url is not my card" as
        # "needs a card".
        credited = (item.get("image_source_link") or "").strip()
        current = item.get("image_url") or ""
        if credited and current.startswith("/") and os.path.exists(
                os.path.join("public", current.lstrip("/"))):
            continue

        filename = card_filename(item)
        on_disk = os.path.join(CARD_DIR, filename)
        expected_url = card_site_url(on_disk)

        if item.get("image_url") == expected_url and os.path.exists(on_disk):
            continue

        try:
            written = write_card(item, CARD_DIR)
        except Exception as e:
            # Not fatal here — an old entry failing must not cost today's article. The
            # caller decides, because only it knows which entry is the new one.
            print(f"::error::Could not render the share card for {item_id}: {e}",
                  flush=True)
            failed.append(item)
            continue

        item["image_url"] = card_site_url(written)
        print(f"Rendered share card for {item_id}: {item['image_url']} "
              f"({os.path.getsize(written) // 1024} KB)", flush=True)

    return failed


def card_site_url(path):
    """Site-absolute URL for a file written under public/.

    Derived from the path write_card actually returns rather than from a second copy of
    the directory constant, so the two can never disagree about where cards live.
    AGENTS.md section 3's trailing-slash rule governs page links; an asset URL is a file
    and takes none.
    """
    return "/" + os.path.relpath(path, "public").replace(os.sep, "/")


# The size and shape limits the download has to satisfy. All three came out of the
# original implementation and are kept because each one is a defect it caught:
#   * a source page's og:image is often a site-wide header banner rather than the dish,
#     and a banner is wide and short — hence the aspect and height floor;
#   * Cambodian mobile is the audience (section 8 self-hosts nothing it can avoid), so
#     the file is re-encoded down to 800px and under 48 KB rather than served as found;
#   * a portrait photograph is centre-cropped to 16:9 so the card and the photograph
#     occupy the same slot in the layout.
PHOTO_MAX_WIDTH = 800
PHOTO_MAX_KB = 48
PHOTO_MIN_HEIGHT = 300
PHOTO_MAX_ASPECT = 2.8


def rehost_source_image(entry, source_image_url):
    """Download the source article's photograph, re-encode it, and store it locally.

    Returns the path written, or None if there is nothing usable — in which case the
    caller falls back to the generated share card. Returning None rather than raising is
    deliberate: a missing photograph costs an illustration, not the day's article.

    Nothing hotlinks. The site serves its own copy, which is what makes a takedown a
    file deletion under our control rather than a request to somebody else's server.
    The credit for it is recorded by the caller as image_source_link; check_content.py
    fails the build on a photograph stored without one.

    Pillow is imported lazily for the same reason render_pulse_cards does it:
    check_pulse_health.py imports parse_any_date from this module, and a top-level
    Pillow import would make it a hard requirement of merely importing this file.
    """
    if not source_image_url or not source_image_url.startswith("http"):
        return None

    import io
    from PIL import Image

    out_dir = os.path.join("public", "images", "pulse")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "%s.webp" % (entry.get("slug") or entry.get("id")))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    try:
        req = urllib.request.Request(source_image_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            img_bytes = resp.read()

        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        w, h = img.width, img.height
        if h < PHOTO_MIN_HEIGHT or (w / float(h)) > PHOTO_MAX_ASPECT:
            print("Source image for %s is a %dx%d banner, not a photograph of the dish "
                  "— falling back to the share card." % (entry.get("id", "?"), w, h),
                  flush=True)
            return None

        if (w / float(h)) < 1.0:                      # portrait: centre-crop to 16:9
            new_h = int(w / (16.0 / 9.0))
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        if img.width > PHOTO_MAX_WIDTH:
            new_h = int(img.height * (PHOTO_MAX_WIDTH / float(img.width)))
            img = img.resize((PHOTO_MAX_WIDTH, new_h), Image.Resampling.LANCZOS)

        for q in range(80, 20, -5):
            img.save(target, "WEBP", quality=q, optimize=True)
            if (os.path.getsize(target) / 1024.0) <= PHOTO_MAX_KB:
                break

        print("Rehosted the source photograph for %s: %s (%d KB, %dx%d)"
              % (entry.get("id", "?"), target, os.path.getsize(target) // 1024,
                 img.width, img.height), flush=True)
        return target
    except Exception as e:
        print("Could not rehost the source photograph for %s (%s) — falling back to the "
              "share card." % (entry.get("id", "?"), e), flush=True)
        if os.path.exists(target):
            # A half-written file would pass check_content.py's existence check and
            # ship a broken og:image, which is the defect section 6 records.
            try:
                os.remove(target)
            except OSError:
                pass
        return None


# --- The generation prompt -------------------------------------------------------
#
# Two subjects, one set of rules. The banquet-seed brief and the recipe brief differ only
# in what they point the writer at; the language rules, the promotional limits, the
# thin-content bans and the output contract are SHARED CONSTANTS so that hardening one
# hardens both. They were a single f-string before 2026-08-22; splitting the subject out
# rather than copying the whole prompt is what stops the two drifting apart, which is the
# same reasoning that keeps display_width in one file with two consumers.

PROMPT_IDENTITY = """
You are the senior Khmer culinary editor for CKM Catering (ចេង គួងម៉េង), a family
banquet kitchen in Phnom Penh with 60 years behind it. You are writing for readers in
Cambodia who are planning a wedding, a family ceremony or a company gathering.
"""

# Exactly as spelled in src/data/homeData.ts. Section 12: dish names must match that file
# character for character. បាយខ្ចប់ស្លឹកឈូក in particular — ខ្ចប់ is "to wrap"; ខ្ទប់ is not
# the word and was live on the homepage.
PROMPT_MENU_DISHES = (
    "ជ្រូកខ្វៃនិងនំប៉័ង, ស៊ុបប៉ាវហឺ១០មុខ, ត្រីតុកកែចំហ៊ុយទឹកស៊ីអ៊ីវ, បាយខ្ចប់ស្លឹកឈូក, "
    "ញាំជើងទាបង្គោរមិក, តុងយាំបង្កងទន្លេ, កូនជ្រូកខ្វៃទាំងមូល, ទាខ្វៃហុងកុង, "
    "បង្អែមខ្មែរបុរាណ"
)

PROMPT_PROMOTIONAL_LIMITS = """
PROMOTIONAL LIMITS — THE HARDEST RULE HERE
We market this business on the owner's behalf and we CANNOT VERIFY HIS OPERATIONS, so the
article must never commit him to anything. Nothing you write may promise, on CKM's behalf:
 - a price, a deposit, a discount, or any figure of money;
 - a capacity: a number of tables, a number of guests, a minimum or a maximum booking;
 - a service area, a district, a travel radius, or a delivery promise;
 - equipment or technology: no modern or automated kitchen, no digital temperature
   monitoring, no refrigerated transport, no named machine;
 - a certification, an inspection, an award or a licence;
 - unlimited or fully customised menus, international fusion on request, or any form of
   "we can make any dish you want";
 - online booking, online payment, online plan selection, or an invoice guarantee;
 - any unconditional guarantee. NEVER write the Khmer for "one hundred percent" of
   anything, and never "no hidden costs". An absolute is rejected outright.
Never state a profit margin or a cost breakdown. Do not write about tipping, about packing
leftovers home, about bargaining, or about anything being cheap.

Instead: state what is GENERALLY TRUE of a Khmer-Chinese banquet kitchen and of careful
practice, and route every specific commitment to a direct conversation — invite the reader
to speak with CKM on Telegram or by telephone to settle the details of their own event.
That invitation is the correct ending for any question the reader would otherwise expect a
number for.

The ONE scheduling figure you may state is the booking lead time, and it is exactly
'២ ទៅ ៤ សប្តាហ៍' before the event. Never any other span, and always followed by an
invitation to contact CKM and confirm the date.

Figures that are planning advice TO THE READER — how much floor space a guest needs, how
far the kitchen should sit from the tables — are not commitments about what CKM supplies
and are welcome.
"""

PROMPT_THIN_CONTENT_BANS = """
BANNED, BECAUSE THEY MAKE CONTENT THIN
- Filler adjectives standing in for information: "ឆ្ងាញ់ណាស់", "ល្អឥតខ្ចោះ",
  "ប្រណីតបំផុត" with nothing concrete attached.
- Sentences that would be equally true of any dish or any event on earth.
- Hard technical specifications: no temperatures in degrees, no electrical ratings, no
  exact hold times. Describe judgement and craft in words instead.
- Inventing a fixed number where practice varies. Simmer times and where a course sits in
  a meal depend on the size of the ingredient and on family custom — say so rather than
  making one up.
- A RECIPE'S FORM. No numbered steps, and no ingredient list with quantities. This is
  commentary on the dish, not instructions for making it. The answer is checked
  mechanically for both shapes and is rejected outright if either appears.
"""

PROMPT_LANGUAGE_RULES = """
LANGUAGE — ABSOLUTE
1. 100% Khmer script. ZERO Chinese characters. ZERO raw English words — and a bracketed
   English gloss beside the Khmer is still an English word. Do not write one.
2. ZERO Thai script (ก-๛), ZERO Japanese kana, ZERO Devanagari. Khmer and Thai share
   Indic vocabulary and your training data mixes them. Do NOT emit ช่วย, หัวใจ,
   วัฒนธรรม, จากการ, รากผักชี or any other Thai word. If you are unsure of a Khmer word,
   describe the idea in plain Khmer rather than borrowing a Thai one.
3. Address the reader as 'លោកអ្នក' — never bare 'អ្នក'. Refer to the team as 'យើងខ្ញុំ'.
4. Humble and specific. No hype: never '第一', 'ល្អបំផុតក្នុងពិភពលោក', 'គ្មានអ្នកណាប្រៀបបាន'.
5. Watch for doubled words: 'លោកលោកអ្នក' has shipped before.
"""

PROMPT_OUTPUT_CONTRACT = """
OUTPUT — JSON ONLY, no commentary, no markdown fences:
   - "title_km": 30-55 characters. %(title_rule)s
     Vary the opening across articles — do not start every title the same way. The first
     ten characters of the title and of the summary are checked against every entry
     already published, and a third repeat is rejected.
   - "summary_km": 150-200 characters. State the actual insight, so a reader who reads only
     this line still learns something.
   - "content_km": 450-600 Khmer words, in exactly 4 sections. Each section MUST begin with
     its own descriptive markdown subheading starting with '### ' in Khmer (for example:
     '### ១. ...'), following the four points above in order. Each section must contain at
     least one concrete, checkable statement.
   - "key_points_km": exactly 3 items. Each must state a specific technique or judgement a
     reader could act on. Not summaries of the article, and not slogans.
"""

SEED_TITLE_RULE = (
    "The title MUST contain at least one of these Khmer terms, written exactly so: "
    "ម្ហូបការ, មុខម្ហូប, ពិធី. This is checked in code and the answer is rejected without "
    "it — these are the terms Cambodian readers actually type into a search box. Put it "
    "where it reads naturally, NOT necessarily at the start."
)

FOOD_TITLE_RULE = (
    "Lead with the technique or the insight, not the foreign dish name."
)

SEED_BRIEF = """
TODAY'S SUBJECT IS A BANQUET TOPIC, NOT A RECIPE.

Topic: %(topic)s
The question a reader planning a banquet is actually asking: %(angle)s

WHAT MAKES THE PIECE WORTH PUBLISHING
Every article must do all four of these, in this order:
1. ANSWER THE QUESTION. Open by answering the reader's question plainly, in a way they
   could act on today. Do not warm up first.
2. EXPLAIN WHY THE ANSWER IS WHAT IT IS. Give the reasoning a banquet kitchen works from:
   how a dish behaves across many tables, why a course sits where it sits, what changes
   when the guest count rises. Explain the principle, not just the instruction.
3. MAKE IT USEFUL IN CAMBODIA. Honour ចាស់ទុំ in any advice about the menu. Address dry
   season heat and wet season rain for anything outdoors. Answer real Phnom Penh
   logistics where they apply: approval inside a បុរី, parking, narrow access lanes.
   Where a dish is relevant, name a real one from CKM's own menu: %(dishes)s.
4. TELL THE READER WHAT TO DO NEXT, and route anything specific to their own event —
   dates, counts, budgets — to a direct conversation on Telegram or by telephone.
"""

FOOD_BRIEF = """
A recipe blog has published the article below. Do NOT translate it. Translation of a
foreign recipe is thin content and will be treated as such by search engines and by
readers. Your job is to write an ORIGINAL Khmer feature that uses this dish only as a
starting point, and whose value comes from something the source article does not have:
the perspective of a Khmer-Chinese banquet kitchen.

WHAT MAKES THE PIECE WORTH PUBLISHING
Every article must do all four of these, in this order:
1. NAME THE TECHNIQUE. Identify the one transferable cooking principle at work — control
   of heat, the order ingredients enter the wok, how a broth is clarified, how a protein
   is kept from drying, how a sauce is balanced. Explain WHY it works, not just what to do.
2. CONNECT IT TO KHMER-CHINESE BANQUET COOKING. Which dish already on a Cambodian
   wedding table uses this same principle? Name real dishes: %(dishes)s. Draw a real
   parallel or a real contrast — never a vague "this is similar to Khmer cooking".
3. MAKE IT USEFUL TO A CAMBODIAN READER. What changes when you cook this in Phnom Penh —
   which ingredient is easy to find at a local market and which needs a substitute, how
   the humidity or heat affects it, what to do differently when cooking for many guests
   rather than for one family.
4. SAY WHERE IT FITS IN A MEAL. Opening, main, palate-cleanser, or closing — and why.

ALSO BANNED for this piece: restating the source recipe step by step — never produce an
ingredient list or a numbered method — and mentioning the source blog, the source
country, or that this is adapted at all.

Source dish: %(title_en)s
Source notes: %(desc_en)s
"""


def build_prompt(candidate):
    """The full prompt for one candidate. Shared rules, subject-specific brief."""
    if candidate.get("kind") == "seed":
        brief = SEED_BRIEF % {"topic": candidate["topic_km"],
                              "angle": candidate["angle_km"],
                              "dishes": PROMPT_MENU_DISHES}
        title_rule = SEED_TITLE_RULE
    else:
        brief = FOOD_BRIEF % {"dishes": PROMPT_MENU_DISHES,
                              "title_en": candidate["title_en"],
                              "desc_en": candidate["desc_en"]}
        title_rule = FOOD_TITLE_RULE

    return "".join([
        PROMPT_IDENTITY,
        brief,
        PROMPT_THIN_CONTENT_BANS,
        PROMPT_PROMOTIONAL_LIMITS,
        PROMPT_LANGUAGE_RULES,
        PROMPT_OUTPUT_CONTRACT % {"title_rule": title_rule},
    ])


def update_pulse_daily():
    out_file = "src/data/pulseData.json"
    existing_pulse = []
    if os.path.exists(out_file):
        with open(out_file, "r", encoding="utf-8") as f:
            existing_pulse = json.load(f)

    existing_links = set(p.get("source_link", "").strip() for p in existing_pulse if p.get("source_link"))

    # --- Which slot is today? ------------------------------------------------------
    #
    # Five banquet-seed days then two RSS food days per seven-day cycle (owner directive
    # 2026-08-22), decided from the PHNOM PENH calendar date. Deciding from the date and
    # not from a counter is what makes a re-run idempotent: the same day always resolves
    # to the same slot and starts at the same seed.
    #
    # load_pulse_seeds() raises on a malformed seed file, which turns the run red. That is
    # deliberate — section 15: a failure that cannot turn a run red will not be noticed,
    # and a bad seed would otherwise publish a bad title.
    seeds = load_pulse_seeds()
    pub_day = publication_date()
    slot = "banquet" if is_banquet_slot(pub_day) else "food"
    seed_candidates = []

    if slot == "banquet":
        seed_candidates = select_seed_candidates(seeds, existing_links, pub_day)
        if not seed_candidates:
            # 66 seeds at five a week is roughly three months. Running out is a
            # content-planning problem, not an outage, so fall through to the food path —
            # something still publishes — but say so loudly enough that it gets actioned.
            print("::warning::Every banquet seed in devops/pulse_seeds.json has already "
                  "been published. Falling back to the food slot today; add more seeds.",
                  flush=True)
            slot = "food"

    seeds_remaining = unused_seed_count(seeds, existing_links)
    print("\nSlot for %s (%s): %s. %d of %d banquet seeds unused."
          % (pub_day.isoformat(), pub_day.strftime("%A"), slot,
             seeds_remaining, len(seeds)), flush=True)

    # A banquet-seed day needs NO network to choose its subject: the feeds are not
    # fetched, and verify_live_url is never reached because `unseen` stays empty below.
    if slot == "banquet":
        raw_items, depth_reached, feeds_healthy = [], 0, True
    else:
        raw_items, depth_reached, feeds_healthy = fetch_verified_gourmet_rss_items(existing_links)

    # [REGRESSION] Take the NEWEST unseen item, not the first one in FEEDS order.
    #
    # Selection used to be `for item in raw_items: ... break`, and raw_items is built
    # by walking FEEDS in order, so the queue was feed-ordered rather than date-ordered.
    # Measured 2026-08-15 against the live feeds, with 88 unseen items queued: the next
    # 14 days would have published content 182 to 1,399 days old, and
    # omnivorescookbook.com — the most active source at ~18 posts/month — would not have
    # been reached until day 48. Its RSS window holds 10 items at ~0.6/day, so an item
    # survives there about 17 days: roughly 28 posts would have scrolled out unread
    # before the pipeline ever arrived at that feed.
    #
    # The two kinds of supply have different shelf lives, and that is the whole argument.
    # An active feed's items are PERISHABLE — not taken, they fall out of the window and
    # are gone. A dormant feed's back catalogue is not: those items sit there
    # indefinitely. So spend the perishable supply first and let the dormant catalogue be
    # the reserve that covers a lean day — which is precisely the headroom this pipeline
    # was short of. Sorting by date gets that with no special case: fresh outranks stale,
    # and stale is reached only when nothing fresh is left.
    #
    # This is display-independent. Identity (id + slug) is still assigned once at insert,
    # and the listing still orders on added_at.
    # Undated or unrecognised timestamps sort last rather than jumping the queue.
    # Banquet fit is a TIE-BREAK WITH A BOUND, not a filter, and the bound is what keeps
    # the perishability argument above intact.
    #
    # The feeds are home-cooking blogs, so a fair share of what arrives is a weeknight
    # dish that reads oddly under a wedding-banquet brand. Preferring the banquet-shaped
    # ones raises the average without writing a new rule about supply. But a HARD filter
    # would break the paragraph above: banquet dishes are a minority of an active feed's
    # output, so filtering would leave the perishable items unspent, they would scroll out
    # of the 10-item RSS window unread, and the pipeline would end up living off the
    # dormant archive — the exact failure mode the date sort was introduced to fix.
    #
    # So the bonus is expressed in the same unit as the sort key: a banquet-fit item is
    # treated as if it were BANQUET_FIT_BONUS_DAYS newer than it is. It can therefore
    # overtake a home-cooking post published up to that many days earlier and nothing
    # older. Measured shelf life of an item in Omnivore's Cookbook's window is ~17 days
    # (10 items at ~0.6/day), so 21 days keeps the reordering inside roughly one window:
    # a fresh perishable item is never held back long enough to be lost, and no item from
    # the dormant archive can ever jump ahead of a fresh one.
    #
    # Matching is on the source title only, which is what EXCLUDE_REGEX already reads;
    # no extra request, and no new failure mode. A miss costs nothing — an unmatched
    # dish simply sorts on its date, exactly as every item did before.
    BANQUET_FIT_BONUS_DAYS = 21
    UNDATED = datetime.min.replace(tzinfo=timezone.utc)

    def selection_rank(item):
        d = parse_any_date(item.get("pubDate", ""))
        if d == UNDATED:
            # parse_any_date returns datetime.min for a timestamp it cannot read. The
            # bonus must not lift it off that floor: the sentinel exists so an item with
            # no usable date sorts behind every item that has one, banquet dish or not.
            return d
        if BANQUET_REGEX.search(item.get("title_en", "") or ""):
            return d + timedelta(days=BANQUET_FIT_BONUS_DAYS)
        return d

    unseen = [it for it in raw_items if it["link"].strip() not in existing_links]
    # sorted() is stable, so items sharing a rank keep their FEEDS order.
    unseen.sort(key=selection_rank, reverse=True)

    # The runway signal reported to the workflow summary. On a banquet day the analogous
    # number is how many seed topics are left, not how many feed items are queued.
    queue_depth = seeds_remaining if slot == "banquet" else len(unseen)

    # Liveness is checked HERE, on the candidates about to be processed, rather than on
    # every candidate during the fetch. Collect up to 5 live candidates so that if one
    # fails quality gates, the pipeline can fall back to the next dish.
    #
    # The candidate's source photograph is resolved HERE, on the handful of candidates
    # about to be processed, for the same reason verify_live_url is: doing it during the
    # fetch cost ~188 requests to publish one article. Two of the three tiers read the
    # already-parsed feed entry and cost nothing; only the og:image tier makes a request.
    # It is only a URL at this point — nothing is downloaded until an entry exists to
    # attach it to, which is after generation.
    #
    # A banquet seed has no source and therefore no photograph, by construction: it is
    # not a feed item, so this loop never sees it and its image_url stays absent. Its
    # illustration is the share card render_pulse_cards() draws at the end.
    #
    # On a banquet day this already holds today's seed topics and `unseen` is empty, so
    # the loop runs zero times: no HTTP request is made to choose a subject.
    valid_candidates = list(seed_candidates)
    for cand in unseen:
        if verify_live_url(cand["link"]):
            # "" rather than a stand-in image: no photograph is a legitimate outcome and
            # the card covers it. A borrowed CKM photograph would misrepresent the dish.
            cand["image_url"] = extract_image_multitier(
                cand.get("_xml_item"), "", cand["link"])
            valid_candidates.append(cand)
            if len(valid_candidates) >= 5:
                break
        else:
            print(f"Candidate URL did not resolve, trying the next: {cand['link'][:70]}", flush=True)

    print(f"\nQueue: {len(unseen)} unseen candidate(s) of {len(raw_items)} fetched, "
          f"archive depth {depth_reached}, {len(valid_candidates)} verified live.", flush=True)

    if not valid_candidates:
        if not unseen:
            reason = "archive-exhausted"
            print("\nEVERY archive page of EVERY feed is exhausted — the current sources "
                  "have nothing left to publish. A new source is required.", flush=True)
        else:
            reason = "all-candidates-dead"
            print(f"\n{len(unseen)} unseen candidate(s) exist but NONE resolved to a live "
                  "URL. That points at a network or user-agent problem, not at supply.",
                  flush=True)
        taken = {p.get("slug") for p in existing_pulse if p.get("slug")}
        for entry in existing_pulse:
            if not entry.get("id"):
                entry["id"] = next_pulse_id(existing_pulse)
            if not entry.get("slug"):
                entry["slug"] = generate_seo_slug(
                    entry.get("source_title_en", ""), entry["id"], taken)
                taken.add(entry["slug"])
        # Nothing new today, but any entry still pointing at a rehosted photograph gets
        # its card drawn here, so the migration completes without a separate backfill.
        # A failure is reported and tolerated: this path publishes nothing, so there is
        # no new entry to protect, and the run already exits non-zero below.
        render_pulse_cards(existing_pulse)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(existing_pulse, f, ensure_ascii=False, indent=2)
        print("Dataset unchanged — no deploy or indexing needed.", flush=True)
        set_action_output(changed="false", reason=reason, slot=slot,
                          queue_depth=queue_depth, archive_depth=depth_reached)
        print(f"::error::The pulse published nothing today (reason: {reason}).", flush=True)
        return 1

    api_key = get_gemini_api_key()
    print(f"Loaded Gemini API Key for Pulse Pipeline (len: {len(api_key)})", flush=True)

    successful_candidate = None
    title_km = summary_km = content_km = ""
    key_points_km = []
    item_to_process = None

    for cand_idx, candidate in enumerate(valid_candidates, 1):
        item_to_process = candidate
        label = (item_to_process["topic_km"] if item_to_process.get("kind") == "seed"
                 else item_to_process["title_en"])
        print(f"\nProcessing candidate {cand_idx}/{len(valid_candidates)} "
              f"({slot} slot): {label}", flush=True)

        prompt = build_prompt(item_to_process)

        MAX_ATTEMPTS = 3
        title_km = summary_km = content_km = ""
        key_points_km = []
        reject_reason = "generation-failed"
        reject_detail = []
        candidate_succeeded = False

        for attempt in range(1, MAX_ATTEMPTS + 1):
            attempt_prompt = prompt
            if attempt > 1:
                attempt_prompt += (
                    "\n\nRETRY %d/%d. Your previous answer was REJECTED. %s\nSpecifics: %s\n"
                    "Rewrite the whole answer, keeping every other rule above."
                    % (attempt, MAX_ATTEMPTS,
                       RETRY_GUIDANCE.get(reject_reason, RETRY_GUIDANCE["generation-failed"]),
                       "; ".join(reject_detail[:5]) or "none recorded")
                )

            # Pacing delay keeps the free tier from rate-limiting us.
            time.sleep(10)
            khmer_json = call_gemini_api_robust(attempt_prompt,
                                                min_content_len=MIN_CONTENT_CHARS,
                                                start=attempt - 1)

            title_km = summary_km = content_km = ""
            key_points_km = []
            if khmer_json:
                try:
                    clean_json = khmer_json.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_json)
                    title_km = sanitize_text(parsed.get("title_km", ""))
                    summary_km = sanitize_text(parsed.get("summary_km", ""))
                    content_km = sanitize_text(parsed.get("content_km", ""))
                    key_points_km = [sanitize_text(pt) for pt in parsed.get("key_points_km", []) if pt]
                except Exception as e:
                    print(f"Attempt {attempt}: JSON parse error: {e}", flush=True)

            if not content_km or len(content_km) < MIN_CONTENT_CHARS:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: content too short — retrying.", flush=True)
                reject_detail = ["response was truncated or unparseable"]
                reject_reason = "generation-too-short"
                continue

            sections = len(SECTION_HEADING.findall(content_km))
            if sections < MIN_CONTENT_SECTIONS:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: only {sections} subheading(s), "
                      f"need {MIN_CONTENT_SECTIONS} — retrying.", flush=True)
                reject_detail = ["the piece had %d markdown subheadings; the four sections "
                                 "must each carry their own Khmer subheading" % sections]
                reject_reason = "generation-unstructured"
                continue

            # The commentary gate. Checked here, straight after the structure gate,
            # because it decides what KIND of piece this is — there is no point trimming
            # a title on a body that should not be published at all.
            steps, quantities = recipe_form_hits(content_km)
            if steps >= RECIPE_FORM_MIN_LINES or quantities >= RECIPE_FORM_MIN_LINES:
                shape = ("%d numbered step lines" % steps if steps >= RECIPE_FORM_MIN_LINES
                         else "%d ingredient lines carrying quantities" % quantities)
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: the body took a recipe's shape "
                      f"({shape}) — that is a restatement of the source, not commentary. "
                      f"Retrying.", flush=True)
                reject_detail = ["the body contained %s. This page comments on the dish "
                                 "for a Cambodian banquet audience; it must not reproduce "
                                 "the source's method as steps or as an ingredient list "
                                 "with quantities" % shape]
                reject_reason = "recipe-form-in-output"
                continue

            # Deterministic repair pass before judging the output.
            # image_alt is no longer generated (there is no photograph to describe); it
            # is set to title_km at insert, so it is covered by the title's own check.
            pre = find_foreign_scripts(title_km, summary_km, content_km, key_points_km)
            if pre:
                title_km = repair_khmer(title_km)
                summary_km = repair_khmer(summary_km)
                content_km = repair_khmer(content_km)
                key_points_km = repair_khmer_deep(key_points_km)
                print(f"Attempt {attempt}: repaired {len(pre)} foreign character(s) via the "
                      "Thai-to-Khmer map.", flush=True)

            reject_detail = find_foreign_scripts(title_km, summary_km, content_km, key_points_km)
            if reject_detail:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: unmapped non-Khmer script remains — retrying.", flush=True)
                for h in reject_detail[:4]:
                    print("   - %s" % h, flush=True)
                print("   (add these to THAI_TO_KHMER if they recur)", flush=True)
                reject_reason = "foreign-script-in-output"
                continue

            # The title gate. Banquet-seed days only — see title_carries_demand for why a
            # food-slot recipe piece is exempt rather than forced into a title that
            # misdescribes it.
            #
            # Checked BEFORE the length gate on purpose. Both gates push the title in
            # opposite directions, and a title that is missing the term has to be
            # rewritten anyway, whereas a title that is merely too long is trimmed. Asking
            # for the rewrite first means the trim happens once, against the final wording.
            if (item_to_process.get("kind") == "seed"
                    and not title_carries_demand(title_km)):
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: the title carries no term "
                      f"Cambodian readers search for — needs ម្ហូបការ or មុខម្ហូប, or "
                      f"ពិធី together with ម្ហូប. Retrying. Title was: {title_km}",
                      flush=True)
                reject_detail = ["the title %r contained no term Cambodian readers "
                                 "search for. It needs ម្ហូបការ or មុខម្ហូប, or ពិធី "
                                 "together with ម្ហូប; an occasion word on its own is "
                                 "not enough, because the page then cannot be found "
                                 "however well it is written" % title_km]
                reject_reason = "title-missing-demand-root"
                continue

            title_w = display_width(title_km)
            if title_w > PULSE_TITLE_MAX_UNITS:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: title is {title_w:.1f} display units "
                      f"(max {PULSE_TITLE_MAX_UNITS}) — Google would truncate it. Retrying.",
                      flush=True)
                reject_detail = ["the title was too long for a search result; it must be at "
                                 "most %d display units, and Khmer consonants are wide"
                                 % PULSE_TITLE_MAX_UNITS]
                reject_reason = "title-too-long"
                continue

            english = sorted(set(re.findall(r"[A-Za-z]{3,}", title_km + " " + summary_km)))
            if english:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: English words in Khmer copy: "
                      f"{', '.join(english[:6])} — retrying.", flush=True)
                reject_detail = ["these English words appeared in the Khmer title or summary: "
                                 + ", ".join(english[:6])
                                 + ". A bracketed gloss of the dish name is still an English "
                                   "word. Write the dish name in Khmer script only."]
                reject_reason = "english-in-output"
                continue

            summary_w = display_width(summary_km)
            if summary_w > PULSE_SUMMARY_MAX_UNITS:
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: summary is {summary_w:.1f} display "
                      f"units (max {PULSE_SUMMARY_MAX_UNITS}) — retrying.", flush=True)
                reject_detail = ["the summary was too long for a search snippet; keep it under "
                                 "%d display units and drop decorative adjectives before facts"
                                 % PULSE_SUMMARY_MAX_UNITS]
                reject_reason = "summary-too-long"
                continue

            opener_clash = None
            for field, key in (("title", "title_km"), ("summary", "summary_km")):
                value = title_km if field == "title" else summary_km
                opener = value[:PULSE_OPENER_PREFIX]
                if len(opener) < PULSE_OPENER_PREFIX:
                    continue
                clash = [e.get("id", "?") for e in existing_pulse
                         if (e.get(key) or "")[:PULSE_OPENER_PREFIX] == opener]
                if len(clash) >= PULSE_OPENER_CAP:
                    opener_clash = (field, opener, clash)
                    break
            if opener_clash:
                field, opener, clash = opener_clash
                print(f"Attempt {attempt}/{MAX_ATTEMPTS}: {field} opens with {opener!r}, already "
                      f"used by {len(clash)} entries ({', '.join(sorted(clash)[:3])}) — retrying.",
                      flush=True)
                reject_detail = ["the %s opened with %r, which %d already-published entries also "
                                 "use. Open with a different construction — name the dish, lead "
                                 "with the ingredient, or state the technique."
                                 % (field, opener, len(clash))]
                reject_reason = "repeated-opener"
                continue

            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: clean Khmer output accepted.", flush=True)
            candidate_succeeded = True
            break

        if candidate_succeeded:
            successful_candidate = item_to_process
            break
        else:
            print(f"WARNING: Candidate {cand_idx} ({item_to_process['title_en']}) rejected across all {MAX_ATTEMPTS} attempts ({reject_reason}). Trying next candidate in queue...", flush=True)

    if not successful_candidate:
        print(f"WARNING: All {len(valid_candidates)} candidates were rejected by the quality gate. "
              "Preserving existing dataset rather than publishing broken Khmer.", flush=True)
        set_action_output(changed="false", reason="all-candidates-rejected", slot=slot,
                          queue_depth=queue_depth, archive_depth=depth_reached)
        print(f"::error::Generation failed for all {len(valid_candidates)} candidate dishes.", flush=True)
        return 1



    new_id = next_pulse_id(existing_pulse)
    taken = {p.get("slug") for p in existing_pulse if p.get("slug")}
    is_seed = item_to_process.get("kind") == "seed"

    # A banquet seed brings its own slug (a Latin URL path segment, like every other pulse
    # and blog slug). It still goes through generate_seo_slug so that collision handling
    # stays in ONE place: the seed file cannot know which slugs are already taken, and a
    # duplicate slug would generate two pages at one URL.
    slug_source = item_to_process["slug_en"] if is_seed else item_to_process["title_en"]

    now_rfc2822 = format_datetime(datetime.now(timezone.utc))

    new_entry = {
        "id": new_id,
        "slug": generate_seo_slug(slug_source, new_id, taken),
        "title_km": title_km,
        "summary_km": summary_km,
        "content_km": content_km,
        "key_points_km": key_points_km,
        "category": item_to_process["category_km"],
        # Filled just below (a rehosted source photograph) or by render_pulse_cards()
        # at the end (the share card, drawn FROM this entry's Khmer text, so it cannot
        # be rendered any earlier). Exactly one of the two always wins.
        "image_url": "",
        # Non-empty ONLY when image_url is a rehosted third party's photograph, and then
        # it is the article that photograph came from. This is the field the page's
        # credit component keys off, which is why it is separate from source_link:
        # source_link is the de-duplication key and is set for every entry, including a
        # card-illustrated one that has nothing to credit. check_content.py's
        # check_pulse_image() makes the two states an error in both directions — a
        # photograph without a credit, and a credit under a picture that reproduces
        # nothing.
        "image_source_link": "",
        # True of either illustration: the share card sets the dish title in large type,
        # and on a photograph of the dish the title is what the picture shows. Short
        # enough to be read aloud, and Khmer, which an English source title is not.
        "image_alt": title_km,
        # For a feed item this is the source URL; for a banquet seed it is the synthetic
        # ckm-seed: key. Either way it is the de-duplication key and nothing else — it has
        # not been rendered on the page since 2026-08-22.
        "source_link": item_to_process["link"],
        # A banquet seed has no upstream article, so there is no source to name. Empty
        # rather than the seed's own slug: inventing an English "source" for a piece
        # written from a Khmer topic would be a false statement about where it came from.
        # The field is kept so every entry in pulseData.json has the same shape, which is
        # what CateringPulse.astro's PulseItem interface expects.
        #
        # For a feed item it is rendered nowhere now but is still sanitised: it is stored
        # for the record and section 13 applies to anything that could be displayed later.
        "source_title_en": "" if is_seed else sanitize_source_title(item_to_process["title_en"]),
        # A seed has no upstream publication date; this run IS its publication.
        "pub_date": item_to_process["pubDate"] or now_rfc2822,
        # When this reached the site, as distinct from when the source blog
        # published it. Sorting on pub_date alone buried today's article at
        # position 26 of 27, on page 3 of the listing: the source post was from
        # February. A recipe's age is not news, but its arrival here is.
        "added_at": now_rfc2822,
    }

    # A feed entry is illustrated by the source article's own photograph where one can be
    # had: it shows the dish the piece is about, which a card cannot. It is downloaded and
    # re-encoded to a local file — nothing hotlinks the source's server — and the article
    # it came from is recorded so the page can credit it.
    #
    # Three outcomes, and every one of them is a valid entry:
    #   feed item, photograph obtained  -> photograph + credit
    #   feed item, no usable photograph -> share card, no credit (nothing to credit)
    #   banquet seed                    -> share card, no credit (there is no source)
    # A failed download therefore costs an illustration, never the day's article.
    if not is_seed:
        photo_path = rehost_source_image(new_entry, item_to_process.get("image_url", ""))
        if photo_path:
            new_entry["image_url"] = card_site_url(photo_path)
            new_entry["image_source_link"] = item_to_process["link"]

    def parse_item_date(item):
        # added_at wins where present; entries from before it existed fall back
        # to pub_date and keep their order relative to each other. added_at is
        # always RFC 2822, but a legacy pub_date copied from a Blogspot feed is
        # ISO 8601, so both formats have to be accepted here too.
        # parse_any_date also guarantees an aware datetime: a naive one cannot be
        # compared against an aware one, and sorted() raises TypeError mid-sort
        # rather than degrading.
        return parse_any_date(item.get("added_at") or item.get("pub_date", ""))

    # Sort for display order only. Identity (id + slug) is assigned once at
    # insert and is never recomputed — reordering must not move any URL.
    updated_list = sorted([new_entry] + existing_pulse, key=parse_item_date, reverse=True)

    failed_cards = render_pulse_cards(updated_list)
    # Identity, not equality: `in` would compare dicts by value.
    if any(e is new_entry for e in failed_cards):
        # An entry with no card has no og:image. AGENTS.md section 6 records what that
        # costs: all 15 blog posts once shipped a 404 preview to Facebook and Telegram,
        # the two channels this business actually runs on. Refuse to publish rather than
        # commit an entry that would do it again — and refuse LOUDLY, because section 15
        # is explicit that a failure which cannot turn a run red will not be noticed.
        # A card failure is local and deterministic (missing font, missing Pillow), so it
        # will recur every run until a person fixes it.
        print("::error::The share card for the new entry could not be rendered; "
              "publishing it would ship a 404 og:image.", flush=True)
        set_action_output(changed="false", reason="card-render-failed", slot=slot,
                          queue_depth=queue_depth, archive_depth=depth_reached)
        return 1

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(updated_list, f, ensure_ascii=False, indent=2)
        
    print(f"SUCCESS: Added 1 new Khmer {slot}-slot article to {out_file}!", flush=True)
    # queue_depth is the runway signal: on a food day, how many unseen feed candidates
    # were available; on a banquet day, how many seed topics remain unpublished. A steady
    # figure means the machine is fed; a figure trending toward zero is the only early
    # warning that the supply is drying up.
    set_action_output(changed="true", new_slug=new_entry["slug"], new_id=new_entry["id"],
                      reason="published", slot=slot, queue_depth=queue_depth,
                      archive_depth=depth_reached)
    return 0

if __name__ == "__main__":
    sys.exit(update_pulse_daily())

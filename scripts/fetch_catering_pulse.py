import os
import json
import time
import urllib.request
import re
import xml.etree.ElementTree as ET
import unicodedata
import hashlib
import sys
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime

sys.stdout.reconfigure(encoding='utf-8')

# Load GEMINI_API_KEY from environment or .env file
env_key = os.environ.get("GEMINI_API_KEY", "")
if not env_key and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                env_key = line.strip().split("=", 1)[1]

print(f"Loaded Gemini API Key for Pulse Pipeline (len: {len(env_key)})", flush=True)

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
        "source_name": "Cambodia Recipe",
        "category_en": "Khmer Heritage Home Cooking",
        "category_km": "ម្ហូបខ្មែរប្រណីត",
        "url": "https://cambodiarecipe.com/feed/"
    },
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
    # Western dishes that do not belong under a Khmer-Chinese banquet brand
    r'cobbler|mac and cheese|hot dog|taco|bourbon|viking|cherry cake|cherry cobbler|'
    r'cherry pie|casserole|pancakes|waffles|sandwich|edinburgh|western recipe|western food|'
    r'tiramisu|croissant|brownie|cupcake|'
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
EXCLUDE_REGEX = re.compile(r'\b(' + _EXCLUDE_TERMS + r')\b', re.IGNORECASE)

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
    r'蔥油餅|葱油饼|三文治'
)
ALLOW_REGEX = re.compile(_ALLOW_TERMS, re.IGNORECASE)

VALID_FALLBACKS = [
    f"/images/blog_{i:02d}_inline_khmer.webp" for i in range(1, 13)
]

def sanitize_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', text)
    return cleaned.strip()

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
    (0x00A0, 0x00A0),   # nbsp
    (0x2000, 0x206F),   # general punctuation (…, —, quotes)
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
MODEL_LADDER = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]
API_CALL_BUDGET = 10          # hard ceiling for a single pipeline run

# The old gate was 450 characters — far below anything the model has ever returned
# (real output runs ~1,900), so it never rejected a single thin response. Set it where
# it actually bites: below this, the piece cannot be carrying four developed sections.
MIN_CONTENT_CHARS = 1200
_api_calls_made = 0


def _gemini_once(prompt, model, timeout=45):
    """Exactly one request. Returns (text, error_kind). No internal retry."""
    global _api_calls_made
    if _api_calls_made >= API_CALL_BUDGET:
        return None, "budget-exhausted"
    _api_calls_made += 1

    # The key travels in the x-goog-api-key header, not `?key=`. Both authenticate, but a
    # key in the query string reaches proxy and access logs, and the `except` below turns
    # exceptions into strings — several urllib errors carry the request URL, which would
    # print the key straight into the CI log.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": env_key},
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
    if not env_key:
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

    Neither verify_live_url nor extract_image_multitier is called here. Both used to
    run for every candidate — up to two extra HTTP requests each, ~188 per run to
    publish a single article — and both are only ever needed for the ONE item that
    actually gets published. They now run at selection time instead, which is what
    makes walking the archives affordable at all.

    The raw XML element is carried on the candidate as `_xml_item` so the image can
    still be extracted from it later without refetching.
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
            "image_url": "",          # resolved at selection time
            "_xml_item": item,
            "_depth": page,
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

def sync_and_download_images(items):
    output_dir = "public/images/pulse"
    os.makedirs(output_dir, exist_ok=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # This function used to slurp every file in the directory into memory (25 MB of
    # WebP) so it could copy image bytes to a new filename whenever an item's slug
    # changed. Slugs no longer change, so that machinery is gone — it existed only to
    # paper over the URL churn, and it is what produced 33 orphaned image files.

    for item in items:
        item_id = item.get("id", "pulse-01")
        slug = item.get("slug", item_id)
        img_url = item.get("image_url", "")
        
        ext = ".jpg"
        if ".webp" in img_url.lower():
            ext = ".webp"
        elif ".png" in img_url.lower():
            ext = ".png"

        target_filename = f"{slug}{ext}"
        target_filepath = os.path.join(output_dir, target_filename)

        if img_url.startswith("http"):
            try:
                req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    img_bytes = resp.read()
                
                target_webp = f"{slug}.webp"
                target_webp_path = os.path.join(output_dir, target_webp)
                
                # Aspect ratio & height anti-fool check (reject thin website header banners)
                from PIL import Image
                import io
                img_obj = Image.open(io.BytesIO(img_bytes))
                if img_obj.mode in ("RGBA", "P"):
                    img_obj = img_obj.convert("RGB")
                    
                w, h = img_obj.width, img_obj.height
                aspect = w / float(h)
                
                if h < 300 or aspect > 2.8:
                    print(f"Downloaded image for {item_id} is thin banner ({w}x{h}). Using fallback image.", flush=True)
                    item["image_url"] = "/images/blog_01_inline_khmer.webp"
                else:
                    # Crop to 16:9 if vertical image
                    if aspect < 1.0:
                        new_h = int(w / (16.0 / 9.0))
                        top = (h - new_h) // 2
                        img_obj = img_obj.crop((0, top, w, top + new_h))
                    
                    # Resize max_width to 800px for ultra-fast Cambodian 3G/4G loading (<50KB)
                    if img_obj.width > 800:
                        new_h = int(img_obj.height * (800 / float(img_obj.width)))
                        img_obj = img_obj.resize((800, new_h), Image.Resampling.LANCZOS)
                        
                    for q in range(80, 20, -5):
                        img_obj.save(target_webp_path, "WEBP", quality=q, optimize=True)
                        if (os.path.getsize(target_webp_path) / 1024.0) <= 48:
                            break
                            
                    item["image_url"] = f"/images/pulse/{target_webp}"
            except Exception as e:
                print(f"Image download fallback for {item_id}: {e}", flush=True)
                if not os.path.exists(target_filepath):
                    item["image_url"] = "/images/blog_01_inline_khmer.webp"
        elif img_url.startswith("/images/pulse/"):
            # Already downloaded and already correctly named — nothing to do.
            # Rewriting it with identical bytes on every run only churned mtimes.
            existing = os.path.join(output_dir, os.path.basename(img_url))
            if not os.path.exists(existing):
                print(f"Missing local image for {item_id}: {img_url}", flush=True)

def update_pulse_daily():
    out_file = "src/data/pulseData.json"
    existing_pulse = []
    if os.path.exists(out_file):
        with open(out_file, "r", encoding="utf-8") as f:
            existing_pulse = json.load(f)

    existing_links = set(p.get("source_link", "").strip() for p in existing_pulse if p.get("source_link"))
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
    def parse_feed_date(item):
        return parse_any_date(item.get("pubDate", ""))

    unseen = [it for it in raw_items if it["link"].strip() not in existing_links]
    # sorted() is stable, so items sharing a timestamp keep their FEEDS order.
    unseen.sort(key=parse_feed_date, reverse=True)

    # Liveness is checked HERE, on the one item about to be published, rather than on
    # every candidate during the fetch. Walk down the queue until one resolves, so a
    # single dead link costs the next-best article instead of the whole day.
    item_to_process = None
    for cand in unseen:
        if verify_live_url(cand["link"]):
            item_to_process = cand
            break
        print(f"Candidate URL did not resolve, trying the next: {cand['link'][:70]}", flush=True)

    if item_to_process is not None:
        fallback_img = VALID_FALLBACKS[len(existing_pulse) % len(VALID_FALLBACKS)]
        item_to_process["image_url"] = extract_image_multitier(
            item_to_process.get("_xml_item"), fallback_img, item_to_process["link"])

    print(f"\nQueue: {len(unseen)} unseen candidate(s) of {len(raw_items)} fetched, "
          f"archive depth {depth_reached}.", flush=True)

    if not item_to_process:
        # Reaching here now means something much stronger than it used to. Selection
        # walks every archive page of every feed before giving up, so this is not
        # "nothing new today" — it is "there is nothing left anywhere", or "everything
        # left is a dead link". Both need a human; neither should look like a quiet day.
        if not unseen:
            reason = "archive-exhausted"
            print("\nEVERY archive page of EVERY feed is exhausted — the current sources "
                  "have nothing left to publish. A new source is required.", flush=True)
        else:
            reason = "all-candidates-dead"
            print(f"\n{len(unseen)} unseen candidate(s) exist but NONE resolved to a live "
                  "URL. That points at a network or user-agent problem, not at supply.",
                  flush=True)
        # Do NOT renumber. Existing ids and slugs are live, indexed URLs.
        # Only backfill an identifier if one is genuinely missing.
        taken = {p.get("slug") for p in existing_pulse if p.get("slug")}
        for entry in existing_pulse:
            if not entry.get("id"):
                entry["id"] = next_pulse_id(existing_pulse)
            if not entry.get("slug"):
                entry["slug"] = generate_seo_slug(
                    entry.get("source_title_en", ""), entry["id"], taken)
                taken.add(entry["slug"])
        sync_and_download_images(existing_pulse)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(existing_pulse, f, ensure_ascii=False, indent=2)
        print("Dataset unchanged — no deploy or indexing needed.", flush=True)
        # len(unseen), not 0: in the all-candidates-dead case candidates DO exist and
        # the distinction is the whole diagnostic value of this field.
        set_action_output(changed="false", reason=reason, queue_depth=len(unseen),
                          archive_depth=depth_reached)
        # Exit non-zero. Every one of these three states needs a person: the sources are
        # spent, the network is broken, or every candidate URL is dead. None of them
        # resolves itself, and a green run for any of them is precisely how this pipeline
        # would stop publishing without anyone noticing.
        print(f"::error::The pulse published nothing today (reason: {reason}).", flush=True)
        return 1

    print(f"\nProcessing 1 NEW article with Rate Limiting & Anti-Fool Guard: {item_to_process['title_en']}", flush=True)
    
    prompt = f"""
You are the senior Khmer culinary editor for CKM Catering (ចេង គួងម៉េង), a family
banquet kitchen in Phnom Penh with 60 years behind it.

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
   wedding table uses this same principle? Name real dishes: ជ្រូកខ្វៃ, ស៊ុបប៉ាវហឺ,
   ត្រីចំហុយទឹកស៊ីអ៊ីវ, បាយខ្ចប់ស្លឹកឈូក, ញាំជើងទា, តុងយាំបង្កងទន្លេ. Draw a real parallel
   or a real contrast — never a vague "this is similar to Khmer cooking".
3. MAKE IT USEFUL TO A CAMBODIAN READER. What changes when you cook this in Phnom Penh —
   which ingredient is easy to find at a local market and which needs a substitute, how
   the humidity or heat affects it, what to do differently when cooking for many guests
   rather than for one family.
4. SAY WHERE IT FITS IN A MEAL. Opening, main, palate-cleanser, or closing — and why.

BANNED, BECAUSE THEY MAKE CONTENT THIN
- Restating the source recipe step by step. Never produce an ingredient list or a
  numbered method.
- Filler adjectives standing in for information: "ឆ្ងាញ់ណាស់", "ល្អឥតខ្ចោះ",
  "ប្រណីតបំផុត" with nothing concrete attached.
- Sentences that would be equally true of any dish on earth.
- Promising anything on the owner's behalf: no prices, no guarantees, no claims about
  CKM's equipment, no "we can make any dish you want".
- Hard technical specifications: no temperatures in degrees, no electrical ratings, no
  exact hold times. Describe judgement and craft in words instead.

LANGUAGE — ABSOLUTE
1. 100% Khmer script. ZERO Chinese characters. ZERO raw English words.
2. ZERO Thai script (ก-๛), ZERO Japanese kana, ZERO Devanagari. Khmer and Thai share
   Indic vocabulary and your training data mixes them. Do NOT emit ช่วย, หัวใจ,
   วัฒนธรรม, จากการ, รากผักชี or any other Thai word. If you are unsure of a Khmer word,
   describe the idea in plain Khmer rather than borrowing a Thai one.
3. Address the reader as 'លោកអ្នក'. Refer to the team as 'យើងខ្ញុំ'.
4. Humble and specific. No hype: never '第一', 'ល្អបំផុតក្នុងពិភពលោក', 'គ្មានអ្នកណាប្រៀបបាន'.
5. Do not mention the source blog, the source country, or that this is adapted.

OUTPUT — JSON ONLY, no commentary, no markdown fences:
   - "title_km": 30-55 characters. Lead with the technique or the insight, not the foreign
     dish name. Vary the opening across articles — do not start every title with 'សិល្បៈនៃ'.
   - "summary_km": 150-200 characters. State the actual insight, so a reader who reads only
     this line still learns something.
   - "content_km": 450-600 Khmer words, in exactly 4 sections, each with its own descriptive
     Khmer subheading, following the four points above in order. Each section must contain at
     least one concrete, checkable statement.
   - "key_points_km": exactly 3 items. Each must state a specific technique or judgement a
     cook could act on. Not summaries of the article, and not slogans.
   - "image_alt": 15-25 Khmer words describing what is visible in the photograph — the dish,
     its main ingredients, its presentation. Not keywords.

Source dish: {item_to_process['title_en']}
Source notes: {item_to_process['desc_en']}
"""
    # Roughly half of Gemini's responses splice a Thai fragment into the Khmer, and a
    # single rejection used to cost the whole day's article. Retry within the run,
    # feeding the exact offending characters back so the model can correct itself.
    MAX_ATTEMPTS = 3
    title_km = summary_km = content_km = image_alt = ""
    key_points_km = []
    reject_reason = "generation-failed"
    # Bound before the loop because the retry prompt below reads it on attempt 2+.
    # Every `continue` in the body assigns it first, so this is belt-and-braces — but
    # that invariant is invisible at the point of use, and one new early `continue`
    # would turn the retry path into a NameError.
    reject_detail = []

    for attempt in range(1, MAX_ATTEMPTS + 1):
        attempt_prompt = prompt
        if attempt > 1:
            attempt_prompt += (
                "\n\nRETRY %d/%d. Your previous answer was REJECTED because it contained "
                "non-Khmer characters: %s\nRewrite it completely. Every character of every "
                "Khmer field must be Khmer script. Check each word before you emit it."
                % (attempt, MAX_ATTEMPTS, "; ".join(reject_detail[:5]))
            )

        # Pacing delay keeps the free tier from rate-limiting us.
        time.sleep(10)
        khmer_json = call_gemini_api_robust(attempt_prompt,
                                            min_content_len=MIN_CONTENT_CHARS,
                                            start=attempt - 1)

        title_km = summary_km = content_km = image_alt = ""
        key_points_km = []
        if khmer_json:
            try:
                clean_json = khmer_json.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_json)
                title_km = sanitize_text(parsed.get("title_km", ""))
                summary_km = sanitize_text(parsed.get("summary_km", ""))
                content_km = sanitize_text(parsed.get("content_km", ""))
                image_alt = sanitize_text(parsed.get("image_alt", ""))
                key_points_km = [sanitize_text(pt) for pt in parsed.get("key_points_km", []) if pt]
            except Exception as e:
                print(f"Attempt {attempt}: JSON parse error: {e}", flush=True)

        if not content_km or len(content_km) < MIN_CONTENT_CHARS:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: content too short — retrying.", flush=True)
            reject_detail = ["response was truncated or unparseable"]
            reject_reason = "generation-too-short"
            continue

        # Deterministic repair pass before judging the output.
        pre = find_foreign_scripts(title_km, summary_km, content_km, image_alt, key_points_km)
        if pre:
            title_km = repair_khmer(title_km)
            summary_km = repair_khmer(summary_km)
            content_km = repair_khmer(content_km)
            image_alt = repair_khmer(image_alt)
            key_points_km = repair_khmer_deep(key_points_km)
            print(f"Attempt {attempt}: repaired {len(pre)} foreign character(s) via the "
                  "Thai-to-Khmer map.", flush=True)

        reject_detail = find_foreign_scripts(title_km, summary_km, content_km, image_alt, key_points_km)
        if reject_detail:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}: unmapped non-Khmer script remains — retrying.", flush=True)
            for h in reject_detail[:4]:
                print("   - %s" % h, flush=True)
            print("   (add these to THAI_TO_KHMER if they recur)", flush=True)
            reject_reason = "foreign-script-in-output"
            continue

        print(f"Attempt {attempt}/{MAX_ATTEMPTS}: clean Khmer output accepted.", flush=True)
        break
    else:
        print(f"WARNING: {MAX_ATTEMPTS} attempts all rejected ({reject_reason}). "
              "Preserving existing dataset rather than publishing broken Khmer.", flush=True)
        set_action_output(changed="false", reason=reject_reason,
                          queue_depth=len(unseen), archive_depth=depth_reached)
        print(f"::error::Generation failed {MAX_ATTEMPTS}/{MAX_ATTEMPTS} times "
              f"({reject_reason}). Gemini is unavailable, rate-limited, or its Khmer has "
              f"drifted below the quality gate.", flush=True)
        return 1

    new_id = next_pulse_id(existing_pulse)
    taken = {p.get("slug") for p in existing_pulse if p.get("slug")}
    new_entry = {
        "id": new_id,
        "slug": generate_seo_slug(item_to_process["title_en"], new_id, taken),
        "title_km": title_km,
        "summary_km": summary_km,
        "content_km": content_km,
        "key_points_km": key_points_km,
        "category": item_to_process["category_km"],
        "image_url": item_to_process["image_url"],
        "image_alt": image_alt or title_km,
        "source_link": item_to_process["link"],
        "source_title_en": item_to_process["title_en"],
        "pub_date": item_to_process["pubDate"],
        # When this reached the site, as distinct from when the source blog
        # published it. Sorting on pub_date alone buried today's article at
        # position 26 of 27, on page 3 of the listing: the source post was from
        # February. A recipe's age is not news, but its arrival here is.
        "added_at": format_datetime(datetime.now(timezone.utc)),
    }

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

    sync_and_download_images(updated_list)
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(updated_list, f, ensure_ascii=False, indent=2)
        
    print(f"SUCCESS: Added 1 new verified Khmer gourmet article to {out_file}!", flush=True)
    # queue_depth is the runway signal: how many unseen candidates were available today.
    # A steady figure means the machine is fed; a figure trending toward zero is the
    # only early warning that the sources are drying up.
    set_action_output(changed="true", new_slug=new_entry["slug"], new_id=new_entry["id"],
                      reason="published", queue_depth=len(unseen),
                      archive_depth=depth_reached)
    return 0

if __name__ == "__main__":
    sys.exit(update_pulse_daily())

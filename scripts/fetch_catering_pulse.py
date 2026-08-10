import os
import json
import time
import urllib.request
import re
import xml.etree.ElementTree as ET
import unicodedata
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load GEMINI_API_KEY from environment or .env file
env_key = os.environ.get("GEMINI_API_KEY", "")
if not env_key and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                env_key = line.strip().split("=", 1)[1]

print(f"Loaded Gemini API Key for Pulse Pipeline (len: {len(env_key)})", flush=True)

FEEDS = [
    {
        "source_name": "Just One Cookbook",
        "category_en": "Authentic Japanese Gourmet & Fine Dining",
        "category_km": "សិល្បៈអាហារអាស៊ី",
        "url": "https://www.justonecookbook.com/feed/"
    },
    {
        "source_name": "Epicurious Gourmet",
        "category_en": "Epicurious Gourmet Culinary & Recipes",
        "category_km": "គ្រឿងផ្សំនិងរសជាតិ",
        "url": "https://www.epicurious.com/feed/rss"
    },
    {
        "source_name": "BBC Good Food",
        "category_en": "BBC Seasonal Gastronomy & Chef Recipes",
        "category_km": "សិល្បៈអាហារអាស៊ី",
        "url": "https://www.bbcgoodfood.com/feed/rss"
    }
]

FOOD_KEYWORDS = [
    "food", "cuisine", "recipe", "recipes", "cooking", "gourmet", "restaurant", 
    "flavor", "flavors", "seafood", "dim sum", "soup", "curry", "banquet", 
    "chef", "dining", "delicacy", "ingredient", "herb", "herbs", "spice", 
    "spices", "taste", "meal", "dish", "dishes", "cake", "pie", "wine", 
    "cocktail", "dessert", "menu", "feast", "gastronomy", "khmer", "chinese", "asian",
    "餐飲", "冰淇淋", "美食", "料理", "甜點", "食材"
]

FOOD_REGEX = re.compile(r'(' + '|'.join(re.escape(k) for k in FOOD_KEYWORDS) + r')', re.IGNORECASE)
EXCLUDE_REGEX = re.compile(
    r'\b(crypto|fast food|burger|pizza|delivery app|flight|hotel room|brain-computer|tech billionaire|cloud computing|leasing market|auction|stock market|movie|movies|film|films|cinema|actor|actress|hollywood|netflix|trailer|tv show|celebrity|director|oscar|entertainment|pub crawl|pub|bar crawl|cobbler|mac and cheese|hot dog|taco|bourbon|viking|cherry cake|cherry cobbler|cherry pie|casserole|pancakes|waffles|sandwich|edinburgh|western recipe|western food|vietnam|vietnamese|saigon|pho|com tam|goi cuon|hanoi|da nang|banh mi|thai|thailand|som tam|tom yum|pad thai|bangkok|phuket|chiang mai|green curry)\b', 
    re.IGNORECASE
)

VALID_FALLBACKS = [
    f"/images/blog_{i:02d}_inline_khmer.webp" for i in range(1, 13)
]

def sanitize_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', text)
    return cleaned.strip()

def generate_seo_slug(title_en, item_id):
    if not title_en:
        return item_id
    nfkd_form = unicodedata.normalize('NFKD', title_en)
    ascii_text = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', ascii_text).strip().lower()
    slug = re.sub(r'[\s-]+', '-', cleaned)
    words = [w for w in slug.split('-') if w][:7]
    short_slug = '-'.join(words)
    if not short_slug:
        return item_id
    return f"{short_slug}-{item_id}"

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

def call_gemini_api_robust(prompt, min_content_len=300):
    """
    Enterprise-grade Gemini API caller with:
    1. Exponential backoff on HTTP 429 (Rate Limit).
    2. Multi-model fallback (gemini-2.0-flash-lite -> gemini-2.0-flash -> gemini-1.5-flash).
    3. Anti-fool guard: Rejects dummy fallback text and retries if response length < min_content_len.
    """
    if not env_key:
        print("ERROR: GEMINI_API_KEY is missing!", flush=True)
        return None
    
    models = ["gemini-3.6-flash", "gemini-3-flash-preview", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={env_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    raw_text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
                    # Anti-fool check: Validate JSON structure and content length
                    clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_json)
                    content_km = parsed.get("content_km", "")
                    
                    if len(content_km) >= min_content_len and "សិល្បៈនៃការចម្អិន" not in parsed.get("title_km", ""):
                        return raw_text
                    else:
                        print(f"[{model} attempt {attempt+1}] Response failed anti-fool check (len: {len(content_km)}). Retrying...", flush=True)
                        time.sleep(3)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    sleep_time = 5 * (attempt + 1)
                    print(f"[{model} attempt {attempt+1}] HTTP 429 Rate Limit hit. Backing off for {sleep_time}s...", flush=True)
                    time.sleep(sleep_time)
                else:
                    print(f"[{model} attempt {attempt+1}] API Error: {e}", flush=True)
                    time.sleep(3)
                    
    return None

def fetch_verified_gourmet_rss_items():
    collected = []
    seen_links = set()
    fallback_idx = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for feed in FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                xml_data = resp.read()
            
            root = ET.fromstring(xml_data)
            items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
            
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

                if EXCLUDE_REGEX.search(title):
                    print(f"Skipping excluded Western/Entertainment article: {title[:50]}...", flush=True)
                    continue

                desc_text = ""
                pubDate = ""
                for child in item:
                    tag = child.tag.lower()
                    if "desc" in tag or "summary" in tag or "content" in tag:
                        desc_text += " " + (child.text or "")
                    elif "date" in tag or "published" in tag or "updated" in tag:
                        pubDate = child.text or pubDate

                if not verify_live_url(link):
                    continue

                seen_links.add(link)
                fallback_img = VALID_FALLBACKS[fallback_idx % len(VALID_FALLBACKS)]
                fallback_idx += 1

                img_url = extract_image_multitier(item, fallback_img, link)

                collected.append({
                    "title_en": title,
                    "desc_en": desc_text[:400],
                    "link": link,
                    "pubDate": pubDate or "Sun, 09 Aug 2026 12:00:00 +0000",
                    "category_km": feed["category_km"],
                    "image_url": img_url
                })
        except Exception as e:
            print(f"Error fetching feed {feed['url']}: {e}", flush=True)
            
    return collected

def sync_and_download_images(items):
    output_dir = "public/images/pulse"
    os.makedirs(output_dir, exist_ok=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    temp_map = {}
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "rb") as f:
                        temp_map[filename] = f.read()
                except Exception:
                    pass

    for item in items:
        item_id = item.get("id", "pulse-01")
        img_url = item.get("image_url", "")
        
        ext = ".jpg"
        if ".webp" in img_url.lower():
            ext = ".webp"
        elif ".png" in img_url.lower():
            ext = ".png"

        target_filename = f"{item_id}{ext}"
        target_filepath = os.path.join(output_dir, target_filename)

        if img_url.startswith("http"):
            try:
                req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    img_bytes = resp.read()
                
                target_webp = f"{item_id}.webp"
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
            old_filename = os.path.basename(img_url)
            if old_filename in temp_map:
                with open(target_filepath, "wb") as out_f:
                    out_f.write(temp_map[old_filename])
                item["image_url"] = f"/images/pulse/{target_filename}"

def update_pulse_daily():
    out_file = "src/data/pulseData.json"
    existing_pulse = []
    if os.path.exists(out_file):
        with open(out_file, "r", encoding="utf-8") as f:
            existing_pulse = json.load(f)

    existing_links = set(p.get("source_link", "").strip() for p in existing_pulse if p.get("source_link"))
    raw_items = fetch_verified_gourmet_rss_items()
    
    item_to_process = None
    for item in raw_items:
        if item["link"].strip() not in existing_links:
            item_to_process = item
            break

    if not item_to_process:
        print("\nNo new RSS items found today. All fetched articles are already in dataset.", flush=True)
        for idx, entry in enumerate(existing_pulse, 1):
            p_id = f"pulse-{idx:02d}"
            entry["id"] = p_id
            if not entry.get("slug") or entry["slug"] == p_id:
                entry["slug"] = generate_seo_slug(entry.get("source_title_en", ""), p_id)
        sync_and_download_images(existing_pulse)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(existing_pulse, f, ensure_ascii=False, indent=2)
        return

    print(f"\nProcessing 1 NEW article with Rate Limiting & Anti-Fool Guard: {item_to_process['title_en']}", flush=True)
    
    prompt = f"""
You are a master Khmer culinary editor for CKM Catering (ចេង គួងម៉េង) in Phnom Penh (60 years of experience).
Task: Adapt this international gourmet food article into 100% PURE KHMER with a strict focus on Khmer traditional recipes (ម្ហូបខ្មែរ), Chinese & Teochew banquet specialties (ម្ហូបចិន/ទាវជីវ), and Asian fine dining (អាហារអាស៊ី).

STRICT GOURMET DIRECTIVES:
1. ABSOLUTELY ZERO Chinese characters (100% 0 漢字/中文).
2. ABSOLUTELY ZERO raw English words (100% 0 English vocabulary).
3. 100% PURE FOOD FOCUS: Discuss ingredients, simmering techniques, broth balance, aromas, spice layers, and culinary artistry.
4. ABSOLUTELY NO wedding planning logistics, NO tent/generator setups, NO Western health/hygiene lectures.
5. Honorifics: Use 'លោកអ្នក' for reader, 'យើងខ្ញុំ' for CKM team.
6. Output JSON ONLY with keys:
   - "title_km": High SEO Value Khmer Title focusing on Khmer/Asian gourmet food (30-55 chars).
   - "summary_km": Concise Khmer intro summary (150-200 chars).
   - "content_km": Detailed and comprehensive 500-600 word Khmer feature story divided into 4 distinct paragraphs with clear, descriptive Khmer subheadings, explaining preparation, simmering, presentation, and flavor profiles in rich detail.
   - "key_points_km": An array of exactly 3 bulleted takeaway points about flavor, technique, and ingredients in Khmer.

Article Title: {item_to_process['title_en']}
Article Summary: {item_to_process['desc_en']}
"""
    # Enforce robust 10-second pacing delay before calling API to fully bypass free-tier rate limits
    time.sleep(10)
    
    khmer_json = call_gemini_api_robust(prompt, min_content_len=450)
    
    title_km = ""
    summary_km = ""
    content_km = ""
    key_points_km = []
    
    if khmer_json:
        try:
            clean_json = khmer_json.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_json)
            title_km = sanitize_text(parsed.get("title_km", ""))
            summary_km = sanitize_text(parsed.get("summary_km", ""))
            content_km = sanitize_text(parsed.get("content_km", ""))
            raw_pts = parsed.get("key_points_km", [])
            key_points_km = [sanitize_text(pt) for pt in raw_pts if pt]
        except Exception as e:
            print(f"JSON parse error: {e}", flush=True)

    if not content_km or len(content_km) < 450:
        print("WARNING: Gemini generation failed anti-fool check. Preserving existing dataset without corrupting items.", flush=True)
        return

    new_entry = {
        "id": "pulse-01",
        "slug": generate_seo_slug(item_to_process["title_en"], "pulse-01"),
        "title_km": title_km,
        "summary_km": summary_km,
        "content_km": content_km,
        "key_points_km": key_points_km,
        "category": item_to_process["category_km"],
        "image_url": item_to_process["image_url"],
        "source_link": item_to_process["link"],
        "source_title_en": item_to_process["title_en"],
        "pub_date": item_to_process["pubDate"]
    }
    
    updated_list = [new_entry] + existing_pulse[:11]
    
    for idx, entry in enumerate(updated_list, 1):
        p_id = f"pulse-{idx:02d}"
        entry["id"] = p_id
        entry["slug"] = generate_seo_slug(entry.get("source_title_en", ""), p_id)
        
    sync_and_download_images(updated_list)
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(updated_list, f, ensure_ascii=False, indent=2)
        
    print(f"SUCCESS: Added 1 new verified Khmer gourmet article to {out_file}!", flush=True)

if __name__ == "__main__":
    update_pulse_daily()

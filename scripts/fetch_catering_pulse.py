import os
import json
import time
import urllib.request
import re
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load GEMINI_API_KEY from .env
env_key = os.environ.get("GEMINI_API_KEY", "")
if not env_key and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                env_key = line.strip().split("=", 1)[1]

print(f"Loaded Gemini API Key (len: {len(env_key)})")

FEEDS = [
    {
        "category_en": "Luxury Wedding Banquet Aesthetics",
        "category_km": "រចនាម្ហូបការប្រណីត",
        "url": "https://wedluxe.com/feed/"
    },
    {
        "category_en": "Off-Premise Catering Operations",
        "category_km": "សេវាកម្មធ្វើម្ហូបចល័ត",
        "url": "https://www.cfe-news.com/feed"
    }
]

INCLUDE_KEYWORDS = ["wedding", "banquet", "catering", "off-premise", "food safety", "hygiene", "menu", "event", "chef", "kitchen", "reception", "dining", "dish"]
EXCLUDE_KEYWORDS = ["fast food", "burger", "pizza", "delivery app", "hotel room", "flight", "bar", "pub", "crypto"]

VALID_FALLBACKS = [
    f"/images/blog_{i:02d}_inline_khmer.webp" for i in range(1, 13)
]

def sanitize_text(text):
    """Remove residual Chinese characters and unwanted jargon."""
    if not text:
        return ""
    # Strip CJK characters ([\u4e00-\u9fff])
    cleaned = re.sub(r'[\u4e00-\u9fff]+', '', text)
    return cleaned.strip()

def extract_image_multitier(item, fallback, item_link):
    # Tier 1: Check media:content / enclosure tags
    for elem in item:
        if 'content' in elem.tag or 'thumbnail' in elem.tag or 'enclosure' in elem.tag:
            img_url = elem.attrib.get('url', '')
            if img_url and img_url.startswith("http"):
                return img_url

    # Tier 2: Check content:encoded / description img src
    for elem in item:
        if 'encoded' in elem.tag or 'description' in elem.tag:
            html_text = elem.text or ""
            m = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif))["\']', html_text, re.IGNORECASE)
            if m:
                return m[0]
                
    # Tier 3: Fetch article page and scrape og:image
    if item_link and item_link.startswith("http"):
        try:
            req = urllib.request.Request(item_link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
            if not m:
                m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html)
            if m and m.group(1).startswith("http"):
                return m.group(1)
        except Exception as e:
            pass

    # Tier 4: Fallback to valid grounded local image
    return fallback

def fetch_rss_items():
    raw_items = []
    fallback_idx = 0
    for feed in FEEDS:
        try:
            req = urllib.request.Request(
                feed["url"],
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
            
            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            
            count = 0
            for item in items:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                desc = item.find("description").text if item.find("description") is not None else ""
                pubDate = item.find("pubDate").text if item.find("pubDate") is not None else ""
                
                full_text = (title + " " + desc).lower()
                if not any(k in full_text for k in INCLUDE_KEYWORDS):
                    continue
                if any(k in full_text for k in EXCLUDE_KEYWORDS):
                    continue
                
                fallback_img = VALID_FALLBACKS[fallback_idx % len(VALID_FALLBACKS)]
                fallback_idx += 1
                
                img_url = extract_image_multitier(item, fallback_img, link.strip())
                
                raw_items.append({
                    "title_en": title.strip(),
                    "desc_en": desc.strip()[:300],
                    "link": link.strip(),
                    "pubDate": pubDate.strip(),
                    "category_km": feed["category_km"],
                    "image_url": img_url
                })
                count += 1
                if count >= 10:
                    break
            print(f"Fetched {count} clean items from {feed['category_en']}")
        except Exception as e:
            print(f"Error fetching {feed['url']}: {e}")
            
    return raw_items

def call_gemini_api(prompt):
    if not env_key:
        return None
    
    models_to_try = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={env_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                time.sleep(2)
    return None

def main():
    out_file = "src/data/pulseData.json"
    existing_pulse = []
    if os.path.exists(out_file):
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                existing_pulse = json.load(f)
        except Exception as e:
            print(f"Warning loading existing pulse data: {e}")
            existing_pulse = []

    # Clean existing list to exclude any removed categories if necessary
    existing_pulse = [x for x in existing_pulse if x.get("category") != "អនាម័យនិងសុវត្ថិភាពម្ហូបអាហារ"]
    existing_links = set(x.get("source_link", "").strip() for x in existing_pulse)

    raw_items = fetch_rss_items()
    
    # Pick exactly 1 candidate item per day that is NOT yet localized
    item_to_process = None
    for item in raw_items:
        if item["link"].strip() not in existing_links:
            item_to_process = item
            break

    if not item_to_process:
        print("\nNo new RSS items found today. All fetched articles are already in dataset.")
        # Save re-indexed list just in case
        for idx, entry in enumerate(existing_pulse, 1):
            entry["id"] = f"pulse-{idx:02d}"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(existing_pulse, f, ensure_ascii=False, indent=2)
        return

    print(f"\nProcessing 1 NEW article for daily Khmer AI localization: {item_to_process['title_en']}")
    
    prompt = f"""
You are a senior professional Khmer editor for CKM Catering (ចេង គួងម៉េង) in Phnom Penh.
Task: Translate and adapt this international catering article into 100% PURE KHMER.

STRICT LANGUAGE & PERSONA DIRECTIVES:
1. ABSOLUTELY ZERO Chinese characters (100% 0 漢字/中文).
2. ABSOLUTELY ZERO raw English words (100% 0 English vocabulary). Translate all terms into natural, elegant Khmer.
   - Replace 'Catering' with 'សេវាកម្មធ្វើម្ហូប'
   - Replace 'Banquet' with 'ពិធីជប់លៀង' or 'ម្ហូបការ'
   - Replace 'Menu' with 'បញ្ជីមុខម្ហូប'
   - Replace 'Chef' with 'ក្រុមចុងភៅ'
   - Replace 'VIP' with 'ភ្ញៀវកិត្តិយស'
3. Honorifics: Use 'លោកអ្នក' for reader, 'យើងខ្ញុំ' for CKM team.
4. Output JSON ONLY with keys:
   - "title_km": Fully translated title in Khmer (NO English words, NO Chinese characters).
   - "summary_km": Concise Khmer summary (100-150 characters).
   - "key_points_km": An array of exactly 3 bulleted key takeaway points in Khmer.

Article Title: {item_to_process['title_en']}
Article Summary: {item_to_process['desc_en']}
"""
    khmer_json = call_gemini_api(prompt)
    
    title_km = ""
    summary_km = ""
    key_points_km = []
    
    if khmer_json:
        try:
            clean_json = khmer_json.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_json)
            title_km = sanitize_text(parsed.get("title_km", ""))
            summary_km = sanitize_text(parsed.get("summary_km", ""))
            raw_pts = parsed.get("key_points_km", [])
            key_points_km = [sanitize_text(pt) for pt in raw_pts if pt]
        except Exception as e:
            print(f"JSON parse error: {e}")
    
    # Clean Pure Khmer Fallback (0 Chinese, 0 English)
    if not title_km or len(title_km) < 5:
        category_label = item_to_process["category_km"]
        title_km = f"បច្ចុប្បន្នភាព និងបទដ្ឋាន{category_label}អន្តរជាតិ សម្រាប់កម្មវិធីមង្គលការ"
        summary_km = f"បទដ្ឋាន និងការណែនាំថ្មីៗអំពីសេវាកម្មធ្វើម្ហូប និងការរៀបចំកម្មវិធីប្រកបដោយអនាម័យ និងគុណភាពខ្ពស់ សម្រាប់លោកអ្នក។"
        key_points_km = [
            "ការអនុវត្តស្តង់ដារអនាម័យអន្តរជាតិក្នុងការរៀបចំម្ហូបអាហារ",
            "ការគ្រប់គ្រងសីតុណ្ហភាព និងគុណភាពគ្រឿងផ្សំយ៉ាងម៉ត់ចត់",
            "ការផ្តល់ជូនបទពិសោធន៍បដិសណ្ឋារកិច្ចដ៏ល្អឥតខ្ចោះជូនភ្ញៀវកិត្តិយស"
        ]

    new_entry = {
        "id": "pulse-01",
        "title_km": title_km,
        "summary_km": summary_km,
        "key_points_km": key_points_km,
        "category": item_to_process["category_km"],
        "image_url": item_to_process["image_url"],
        "source_link": item_to_process["link"],
        "source_title_en": item_to_process["title_en"],
        "pub_date": item_to_process["pubDate"]
    }
    
    # Prepend new article to top of list
    updated_pulse = [new_entry] + existing_pulse
    
    # Re-assign sequential IDs (pulse-01, pulse-02, ...)
    for idx, entry in enumerate(updated_pulse, 1):
        entry["id"] = f"pulse-{idx:02d}"

    # Retain top 36 articles maximum
    updated_pulse = updated_pulse[:36]

    os.makedirs("src/data", exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(updated_pulse, f, ensure_ascii=False, indent=2)

    print(f"\nSuccessfully added 1 daily article to {out_file}! Total articles: {len(updated_pulse)}")

if __name__ == "__main__":
    main()

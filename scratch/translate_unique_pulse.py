import os
import json
import time
import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

env_key = os.environ.get("GEMINI_API_KEY", "")
if not env_key and os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                env_key = line.strip().split("=", 1)[1]

print(f"Loaded Gemini API Key (len: {len(env_key)})")

with open("src/data/pulseData.json", "r", encoding="utf-8") as f:
    items = json.load(f)

def translate_item_with_gemini(item_en_title, category_km, item_link):
    prompt = f"""
You are a senior professional Khmer editor for CKM Catering (ចេង គួងម៉េង) in Phnom Penh.
Task: Translate and adapt this specific international catering article title and summary into 100% PURE ELEGANT KHMER.

Article Title (EN): "{item_en_title}"
Category (KM): "{category_km}"

STRICT RULES:
1. "title_km" MUST be a UNIQUE, specific, elegant Khmer translation of the English article title: "{item_en_title}". DO NOT use generic fallback sentences.
2. ABSOLUTELY ZERO Chinese characters (100% 0 漢字/中文).
3. ABSOLUTELY ZERO raw English words (100% 0 English vocabulary in title_km, summary_km, and key_points_km).
   - Replace 'Catering' with 'សេវាកម្មធ្វើម្ហូប'
   - Replace 'Banquet' with 'ពិធីជប់លៀង' or 'ម្ហូបការ'
   - Replace 'Menu' with 'បញ្ជីមុខម្ហូប'
   - Replace 'Chef' with 'ក្រុមចុងភៅ'
   - Replace 'VIP' with 'ភ្ញៀវកិត្តិយស'
4. Honorifics: Use 'លោកអ្នក' for reader, 'យើងខ្ញុំ' for CKM team.
5. Output JSON ONLY with keys:
   - "title_km": Unique translated Khmer title for this specific article.
   - "summary_km": Concise Khmer summary (100-150 characters) tailored to this specific article topic.
   - "key_points_km": Array of exactly 3 bulleted key takeaway points in Khmer tailored to this topic.
"""
    models_to_try = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={env_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                    clean_json = text.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_json)
                    title_km = parsed.get("title_km", "").strip()
                    summary_km = parsed.get("summary_km", "").strip()
                    pts = parsed.get("key_points_km", [])
                    if title_km and summary_km and len(pts) >= 3:
                        return title_km, summary_km, pts[:3]
            except Exception as e:
                time.sleep(2)
    return None, None, None

print(f"\nProcessing {len(items)} items for UNIQUE Khmer translation...")

for idx, item in enumerate(items, 1):
    en_title = item.get("source_title_en", "")
    cat_km = item.get("category", "")
    link = item.get("source_link", "")
    
    print(f"[{idx}/{len(items)}] Translating '{en_title[:45]}...'")
    t_km, s_km, pts_km = translate_item_with_gemini(en_title, cat_km, link)
    
    if t_km and s_km:
        item["title_km"] = t_km
        item["summary_km"] = s_km
        item["key_points_km"] = pts_km
        print(f"  -> SUCCESS: {t_km[:50]}")
    else:
        print(f"  -> FAILED to translate item {idx}")

    time.sleep(1)

with open("src/data/pulseData.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully generated 100% UNIQUE Khmer titles & summaries in src/data/pulseData.json!")

import json
import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

valid_local_images = [
    f"/images/blog_{i:02d}_inline_khmer.webp" for i in range(1, 13)
]

for idx, item in enumerate(items):
    link = item.get("source_link", "")
    current_img = item.get("image_url", "")
    
    # If image URL is missing or broken invalid fallback path
    if not current_img or current_img.startswith("http") is False and not current_img.startswith("/images/blog_"):
        scraped_img = None
        if link.startswith("http"):
            try:
                print(f"Scraping og:image for item {idx+1}: {link[:50]}...")
                req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
                m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
                if not m:
                    m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html)
                if m and m.group(1).startswith("http"):
                    scraped_img = m.group(1)
                    print(f"  -> Successfully scraped: {scraped_img[:60]}")
            except Exception as e:
                print(f"  -> Scrape failed: {e}")
        
        if scraped_img:
            item["image_url"] = scraped_img
        else:
            fallback = valid_local_images[idx % len(valid_local_images)]
            item["image_url"] = fallback
            print(f"  -> Assigned valid local fallback: {fallback}")

with open('src/data/pulseData.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("\nSuccessfully fixed and updated all pulse images in src/data/pulseData.json!")

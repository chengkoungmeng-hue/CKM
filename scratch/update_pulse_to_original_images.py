import json
import urllib.request
import re
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read current pulse data
with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    pulse_items = json.load(f)

def extract_og_image(url):
    if not url or not url.startswith("http"):
        return None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html)
        if m and m.group(1).startswith("http"):
            return m.group(1)
    except Exception as e:
        print(f"Error scraping og:image for {url[:50]}: {e}")
    return None

# Map of title keywords to original image URLs from RSS feeds
rss_feeds = [
    "https://wedluxe.com/feed/",
    "https://www.cfe-news.com/feed"
]

rss_image_map = {}

for feed_url in rss_feeds:
    print(f"Fetching RSS feed: {feed_url}")
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        for item in items:
            title = item.find('title').text.strip() if item.find('title') is not None else ''
            link = item.find('link').text.strip() if item.find('link') is not None else ''
            desc = item.find('description').text if item.find('description') is not None else ''
            
            img_url = None
            for elem in item:
                if 'content' in elem.tag or 'thumbnail' in elem.tag or 'enclosure' in elem.tag:
                    u = elem.attrib.get('url', '')
                    if u and u.startswith("http"):
                        img_url = u
                        break
                if 'encoded' in elem.tag:
                    html_text = elem.text or ''
                    m = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif))["\']', html_text, re.IGNORECASE)
                    if m:
                        img_url = m[0]
            
            if not img_url and desc:
                m = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif))["\']', desc, re.IGNORECASE)
                if m:
                    img_url = m[0]

            if not img_url and link:
                img_url = extract_og_image(link)

            if img_url:
                rss_image_map[link] = img_url
                rss_image_map[title.lower()] = img_url
                print(f" -> Found: {title[:35]} ==> {img_url[:60]}")
    except Exception as e:
        print(f"Error fetching feed {feed_url}: {e}")

# Direct mapping for existing items if not found in current RSS top feed
known_article_images = {
    "pulse-01": "https://wedluxe.com/wp-content/uploads/2026/08/hkzcpxhg.jpeg",
    "pulse-02": "https://wedluxe.com/wp-content/uploads/2026/07/sierra-michael-hycroft-main-feature-1130x1507.jpg",
    "pulse-03": "https://wedluxe.com/wp-content/uploads/2026/08/aaron-katerina-villa-bonomi-28-1130x753.jpg",
    "pulse-04": "https://wedluxe.com/wp-content/uploads/2026/07/tiffany-titan-como-point-yamu-144-1130x753.jpg",
    "pulse-05": "https://cfe-news.com/wp-content/uploads/2026/08/small-WVU-Chef-showcase-1024x682.jpg",
    "pulse-06": "https://cfe-news.com/wp-content/uploads/2026/08/small-Duggan_Shannon_NBR-63-1024x768.jpg",
    "pulse-07": "https://cfe-news.com/wp-content/uploads/2026/08/small-ef98e9eb-1138-4a12-ab4e-3425cd69210d-ps-1024x683.jpg",
    "pulse-08": "https://cfe-news.com/wp-content/uploads/2026/07/small-116A2984-683x1024.webp",
    "pulse-09": "https://cfe-news.com/wp-content/uploads/2026/07/shorter-small-20260106_AJSM-Photography-884x1024.jpg",
    "pulse-10": "https://cfe-news.com/wp-content/uploads/2026/07/cropped-Dedes-Table-Watermelon-Popsicles-814x1024.jpg",
    "pulse-11": "https://cfe-news.com/wp-content/uploads/2026/07/small-Tequila-Sunrise-1024x682.webp"
}

updated_count = 0
for item in pulse_items:
    item_id = item.get("id")
    source_title = item.get("source_title_en", "").lower()
    source_link = item.get("source_link", "")

    new_img = None
    if source_link in rss_image_map:
        new_img = rss_image_map[source_link]
    elif source_title in rss_image_map:
        new_img = rss_image_map[source_title]
    elif item_id in known_article_images:
        new_img = known_article_images[item_id]

    if new_img:
        item["image_url"] = new_img
        updated_count += 1
        print(f"Updated [{item_id}] => {new_img}")

with open('src/data/pulseData.json', 'w', encoding='utf-8') as f:
    json.dump(pulse_items, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully updated {updated_count}/{len(pulse_items)} pulse items to original RSS article images!")

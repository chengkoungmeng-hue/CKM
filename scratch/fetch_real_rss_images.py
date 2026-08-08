import urllib.request
import re
import xml.etree.ElementTree as ET
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

FEEDS = [
    {
        "category_km": "រចនាម្ហូបការប្រណីត",
        "url": "https://wedluxe.com/feed/"
    },
    {
        "category_km": "សេវាកម្មធ្វើម្ហូបចល័ត",
        "url": "https://www.cfe-news.com/feed"
    }
]

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
        print(f"Error scraping {url[:50]}: {e}")
    return None

def fetch_rss_articles():
    articles = []
    for feed in FEEDS:
        print(f"Fetching RSS: {feed['url']}")
        req = urllib.request.Request(feed['url'], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            for item in items[:10]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                desc = item.find('description').text if item.find('description') is not None else ''
                
                # Extract image
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
                
                if not img_url:
                    print(f"Scraping og:image from webpage for: {title[:40]}...")
                    img_url = extract_og_image(link)

                articles.append({
                    "title_en": title.strip(),
                    "link": link.strip(),
                    "pubDate": pubDate.strip(),
                    "category": feed["category_km"],
                    "image_url": img_url,
                    "desc": desc[:300]
                })
        except Exception as e:
            print(f"Error fetching feed {feed['url']}: {e}")

    return articles

if __name__ == "__main__":
    arts = fetch_rss_articles()
    print(f"\nFetched {len(arts)} total RSS articles:")
    for a in arts:
        print(f"- Title: {a['title_en'][:40]}")
        print(f"  Link:  {a['link']}")
        print(f"  Image: {a['image_url']}")

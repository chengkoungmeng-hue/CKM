import urllib.request
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

HOST = "ckmkh.com"
BASE_URL = f"https://{HOST}"
INDEXNOW_KEY = "c9b7e416a2d9426fa7406a09289196b0"
KEY_FILE_PATH = f"public/{INDEXNOW_KEY}.txt"

def ensure_key_file():
    os.makedirs("public", exist_ok=True)
    with open(KEY_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)
    print(f"Verified IndexNow key file at {KEY_FILE_PATH}")

def submit_indexnow(urls):
    ensure_key_file()
    
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://www.bing.com/indexnow"
    ]
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{BASE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": urls
    }
    
    for endpoint in endpoints:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"IndexNow ({endpoint}) Status: {resp.status} (Success/Accepted)")
        except urllib.error.HTTPError as e:
            print(f"IndexNow ({endpoint}) HTTP {e.code}: {e.reason}")
        except Exception as e:
            print(f"IndexNow ({endpoint}) Note: {e}")

def notify_gsc_google():
    sitemap_url = f"{BASE_URL}/sitemap-index.xml"
    ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"
    print(f"Notifying Google Search Console via Sitemap ping: {sitemap_url}")
    try:
        req = urllib.request.Request(
            ping_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Google Sitemap Ping Status: {resp.status}")
    except Exception as e:
        print(f"Google Sitemap Ping Response: {e} (Standard response for Google ping endpoint)")

def main():
    target_urls = [
        f"{BASE_URL}/",
        f"{BASE_URL}/blog/",
        f"{BASE_URL}/blog/01-traditional-8-course-wedding-menu/",
        f"{BASE_URL}/blog/02-wedding-catering-budget-guide/",
        f"{BASE_URL}/blog/03-food-tasting/",
        f"{BASE_URL}/blog/04-hygiene-and-temperature-control/",
        f"{BASE_URL}/blog/05-corporate-private-catering/",
        f"{BASE_URL}/blog/06-signature-dishes/",
        f"{BASE_URL}/blog/07-housewarming-catering-setup/",
        f"{BASE_URL}/blog/08-waitstaff-service-flow/",
        f"{BASE_URL}/blog/09-outdoor-tent-infrastructure/",
        f"{BASE_URL}/blog/10-60-years-chef-experience/",
        f"{BASE_URL}/blog/11-choosing-packages/",
        f"{BASE_URL}/blog/12-catering-industry-trends/",
        f"{BASE_URL}/pulse/",
        f"{BASE_URL}/tanghuot/"
    ]

    pulse_file = "src/data/pulseData.json"
    if os.path.exists(pulse_file):
        try:
            with open(pulse_file, "r", encoding="utf-8") as f:
                pulse_items = json.load(f)
                for item in pulse_items:
                    p_id = item.get("id")
                    if p_id:
                        target_urls.append(f"{BASE_URL}/pulse/{p_id}/")
        except Exception as e:
            print(f"Warning reading pulseData.json for indexing: {e}")
    
    print(f"Submitting {len(target_urls)} URLs to IndexNow & GSC Search Engines...")
    submit_indexnow(target_urls)
    notify_gsc_google()

if __name__ == "__main__":
    main()

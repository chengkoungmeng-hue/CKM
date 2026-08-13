import urllib.request
import json
import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

HOST = "ckmkh.com"
BASE_URL = f"https://{HOST}"
INDEXNOW_KEY = "e521f0df7f9c42348c416f1b878d9114"
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

def notify_gsc_api():
    """Notify Google Search Console via Service Account REST API."""
    creds_file = 'google_service_account.json'
    if not os.path.exists(creds_file):
        print("⚠️ GSC credentials not found. Skipping GSC API call.")
        return

    try:
        import requests
        from google.oauth2 import service_account
        import google.auth.transport.requests

        SCOPES = ['https://www.googleapis.com/auth/webmasters']
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=SCOPES
        )
        req = google.auth.transport.requests.Request()
        credentials.refresh(req)
        access_token = credentials.token

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        site_url = 'sc-domain:ckmkh.com'
        sitemap_target = f"{BASE_URL}/sitemap-index.xml"
        sitemap_api_url = f"https://www.googleapis.com/webmasters/v3/sites/{requests.utils.quote(site_url, safe='')}/sitemaps/{requests.utils.quote(sitemap_target, safe='')}"

        res = requests.put(sitemap_api_url, headers=headers, timeout=15)
        print(f"📡 GSC API Sitemap Resubmission: Status {res.status_code}")
        if res.status_code in [200, 204]:
            print("   ✅ Google Search Console API successfully triggered sitemap refresh!")
        else:
            print(f"   ℹ️ GSC API Response: {res.status_code} ({res.text[:100]})")
    except Exception as e:
        print(f"   ⚠️ GSC API Error: {e}")


def main():
    target_urls = [
        f"{BASE_URL}/",
        f"{BASE_URL}/blog/",
        f"{BASE_URL}/pulse/",
        f"{BASE_URL}/tanghuot/"
    ]

    # Dynamically scan all blog post markdown files in src/content/blog/
    blog_files = glob.glob("src/content/blog/*.md") + glob.glob("src/content/blog/*.mdx")
    for b_path in sorted(blog_files):
        b_name = os.path.basename(b_path)
        slug = os.path.splitext(b_name)[0]
        target_urls.append(f"{BASE_URL}/blog/{slug}/")

    # Dynamically scan pulse data items
    pulse_file = "src/data/pulseData.json"
    if os.path.exists(pulse_file):
        try:
            with open(pulse_file, "r", encoding="utf-8") as f:
                pulse_items = json.load(f)
                for item in pulse_items:
                    slug = item.get("slug")
                    p_id = item.get("id")
                    if slug:
                        target_urls.append(f"{BASE_URL}/pulse/{slug}/")
                    if p_id and p_id != slug:
                        target_urls.append(f"{BASE_URL}/pulse/{p_id}/")
                
                # Check pagination pages for pulse
                page_size = 12
                total_pages = (len(pulse_items) + page_size - 1) // page_size
                for p in range(2, total_pages + 1):
                    target_urls.append(f"{BASE_URL}/pulse/{p}/")
        except Exception as e:
            print(f"Warning reading pulseData.json for indexing: {e}")
    
    # Deduplicate while preserving order
    unique_urls = list(dict.fromkeys(target_urls))

    print(f"Submitting {len(unique_urls)} URLs to IndexNow & GSC Search Engines...")
    for u in unique_urls:
        print(f" - {u}")

    submit_indexnow(unique_urls)
    notify_gsc_api()

if __name__ == "__main__":

    main()

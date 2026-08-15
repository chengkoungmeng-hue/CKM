import urllib.request
import json
import os
import re
import subprocess
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

HOST = "ckmkh.com"
BASE_URL = f"https://{HOST}"
INDEXNOW_KEY = "e521f0df7f9c42348c416f1b878d9114"
KEY_FILE_PATH = f"public/{INDEXNOW_KEY}.txt"

def purge_cloudflare_cache():
    """Purge Cloudflare Edge Cache programmatically."""
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not token:
        print("::error::CLOUDFLARE_API_TOKEN is not set - the edge would keep serving "
              "the previous build.")
        return False

    # A GitHub secret pasted with a trailing newline produces the header value
    # "Bearer <token>\n", which is illegal in HTTP and raises
    # "Invalid header value b'***'" before the request is ever sent. This purge
    # had been failing silently on every run for exactly that reason.
    # Strip whitespace first, then stray quotes, then whitespace again.
    token = token.strip().strip("\"'").strip()
    if not token:
        print("::error::CLOUDFLARE_API_TOKEN is empty after trimming.")
        return False

    zone_id = "d459c80e06d000c6e1927783fc6b3a7a"
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    payload = {"purge_everything": True}
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("success"):
                print("🧹 Cloudflare Edge Cache successfully purged!")
                return True
            print(f"::error::Cloudflare Cache Purge failed: {res_data}")
            return False
    except Exception as e:
        print(f"::error::Cloudflare Cache Purge Error: {e}")
        return False

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
    
    accepted = 0
    for endpoint in endpoints:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"IndexNow ({endpoint}) Status: {resp.status} (Success/Accepted)")
                if 200 <= resp.status < 300:
                    accepted += 1
        except urllib.error.HTTPError as e:
            print(f"IndexNow ({endpoint}) HTTP {e.code}: {e.reason}")
        except Exception as e:
            print(f"IndexNow ({endpoint}) Note: {e}")

    # One endpoint refusing is ordinary and the other still carries the submission.
    # Both refusing means the key, the key file or the payload is wrong, and that is
    # a real failure that used to pass as success.
    if accepted == 0:
        print("::error::No IndexNow endpoint accepted the submission.")
        return False
    return True

def notify_gsc_api():
    """Notify Google Search Console via Service Account REST API."""
    creds_file = 'google_service_account.json'
    if not os.path.exists(creds_file):
        print("::error::GSC credentials not found - the sitemap was not submitted.")
        return False

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
            return True
        print(f"::error::GSC API rejected the sitemap: {res.status_code} ({res.text[:120]})")
        return False
    except Exception as e:
        print(f"::error::GSC API Error: {e}")
        return False


def urls_from_git_diff():
    """URLs touched by the most recent commit, for a hand-written edit.

    A content edit changes specific pages; submitting the whole inventory because one
    article was reworded is the same waste as doing it for a pulse post.
    """
    try:
        out = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception as e:
        print(f"Could not read the diff ({e}); falling back to the full inventory.")
        return None
    urls = []
    for path in out.splitlines():
        path = path.strip()
        m = re.match(r"src/content/blog/(.+)\.mdx?$", path)
        if m:
            urls.append(f"{BASE_URL}/blog/{m.group(1)}/")
        elif path == "src/pages/index.astro":
            urls.append(f"{BASE_URL}/")
        elif path.startswith("src/data/pulseData.json"):
            urls.append(f"{BASE_URL}/pulse/")
    return urls or None


def full_inventory():
    """Every canonical URL on the site.

    Deliberately EXCLUDES the /pulse/pulse-NN/ id aliases. They exist so an indexed URL
    never breaks (AGENTS.md 15) and every one of them carries a canonical pointing at the
    slug URL, which is why @astrojs/sitemap leaves them out: the sitemap holds 53 URLs and
    none of them is an alias. Submitting them to IndexNow asked the search engines to
    crawl 24 pages we had already told them point somewhere else.
    """
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
                    if slug:
                        target_urls.append(f"{BASE_URL}/pulse/{slug}/")
                    # the id alias is intentionally omitted -- see the docstring
                
                # Check pagination pages for pulse
                page_size = 12
                total_pages = (len(pulse_items) + page_size - 1) // page_size
                for p in range(2, total_pages + 1):
                    target_urls.append(f"{BASE_URL}/pulse/{p}/")
        except Exception as e:
            print(f"Warning reading pulseData.json for indexing: {e}")
    
    return list(dict.fromkeys(target_urls))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if "--urls" in argv:
        unique_urls = [u for u in argv[argv.index("--urls") + 1:] if u.startswith("http")]
        source = "explicit"
    elif "--changed" in argv:
        unique_urls = urls_from_git_diff() or full_inventory()
        source = "git diff" if urls_from_git_diff() else "full inventory (diff empty)"
    else:
        unique_urls = full_inventory()
        source = "full inventory"

    if not unique_urls:
        print("::error::No URLs to submit.")
        return 1

    print(f"Submitting {len(unique_urls)} URLs to IndexNow & GSC Search Engines "
          f"[{source}]...")
    for u in unique_urls:
        print(f" - {u}")

    # [REGRESSION] Every one of these three used to catch its own exceptions, print a
    # warning and return None, so main() always succeeded. The repo's own history
    # records the consequence: the Cloudflare purge "had been failing silently on every
    # run" behind a green workflow because a trailing newline in the secret made the
    # Authorization header illegal (see purge_cloudflare_cache above). A publish step
    # that cannot fail is a publish step that cannot be trusted.
    results = {
        "cloudflare purge": purge_cloudflare_cache(),
        "indexnow": submit_indexnow(unique_urls),
        "search console": notify_gsc_api(),
    }
    failed = [name for name, ok in results.items() if not ok]
    if failed:
        print(f"::error::Publishing steps failed: {', '.join(failed)}")
        return 1
    print("All publishing steps succeeded.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

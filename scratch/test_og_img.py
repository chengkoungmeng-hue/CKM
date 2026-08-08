import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://wedluxe.com/2026/08/05/hycroft-manor-wedding-vancouver/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html)
    if m:
        print("Scraped og:image URL:", m.group(1))
    else:
        print("og:image not found")
except Exception as e:
    print("Error:", e)

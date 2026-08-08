import urllib.request
import re
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://wedluxe.com/feed/',
    'https://www.cfe-news.com/feed',
    'https://www.foodsafetynews.com/feed/'
]

for url in urls:
    print(f"=== Inspecting {url} ===")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        for item in items[:3]:
            title = item.find('title').text if item.find('title') is not None else ''
            print('Title:', title[:50])
            found_img = None
            
            # Check all tags in item
            for elem in item:
                # Check media:content / enclosure
                if 'content' in elem.tag or 'thumbnail' in elem.tag or 'enclosure' in elem.tag:
                    u = elem.attrib.get('url', '')
                    if u:
                        print('  -> Found in media/enclosure tag:', u)
                        found_img = u
                        break
                # Check content:encoded
                if 'encoded' in elem.tag:
                    html_text = elem.text or ''
                    m = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif))["\']', html_text, re.IGNORECASE)
                    if m:
                        print('  -> Found in content:encoded:', m[0])
                        if not found_img:
                            found_img = m[0]
            
            if not found_img:
                desc = item.find('description').text if item.find('description') is not None else ''
                m = re.findall(r'src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp|gif))["\']', desc, re.IGNORECASE)
                if m:
                    print('  -> Found in description:', m[0])
                    found_img = m[0]
            
            if not found_img:
                print('  -> NO image found in RSS XML')

    except Exception as e:
        print('Error:', e)

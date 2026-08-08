import urllib.request
import re
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = ['https://wedluxe.com/feed/', 'https://www.cfe-news.com/feed', 'https://www.foodsafetynews.com/feed/']

for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        print(f"Checking {url}:")
        for item in items[:3]:
            title = item.find('title').text if item.find('title') is not None else ''
            img_url = ''
            
            # Check enclosure/media tags
            for elem in item:
                if 'content' in elem.tag or 'thumbnail' in elem.tag or 'enclosure' in elem.tag:
                    img_url = elem.attrib.get('url', '')
                    if img_url:
                        break
            
            # Check regex in description
            if not img_url:
                desc = item.find('description').text if item.find('description') is not None else ''
                m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
                if m:
                    img_url = m.group(1)
            
            print('  Title:', title[:40])
            print('  Image:', img_url if img_url else 'Fallback image')
    except Exception as e:
        print('Error:', e)

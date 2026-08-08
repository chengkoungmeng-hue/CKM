import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for idx, item in enumerate(items, 1):
    print(f"Item {idx:02d}: {item.get('title_km')}")

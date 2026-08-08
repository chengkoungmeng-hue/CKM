import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, item in enumerate(data):
    print(f"Item {i+1}: image_url = '{item.get('image_url')}'")

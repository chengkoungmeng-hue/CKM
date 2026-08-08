import json
import re

def generate_seo_slug(title_en, item_id):
    if not title_en:
        return item_id
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', title_en).strip().lower()
    slug = re.sub(r'[\s-]+', '-', cleaned)
    words = slug.split('-')[:7]
    short_slug = '-'.join(w for w in words if w)
    if not short_slug:
        return item_id
    return f"{short_slug}-{item_id}"

with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print("Generated SEO Slugs for Pulse items:")
for item in items:
    slug = generate_seo_slug(item.get('source_title_en', ''), item.get('id', ''))
    item['slug'] = slug
    print(f" - {item['id']} -> /pulse/{slug}/")

with open('src/data/pulseData.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("\nSuccessfully updated pulseData.json with SEO slugs!")

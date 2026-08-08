import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Real external links mapped to pulse IDs
external_links_map = {
    "pulse-01": "https://wedluxe.com/2026/08/06/pippin-hill-wedding-skywritten-love-notes/",
    "pulse-02": "https://wedluxe.com/2026/08/05/hycroft-manor-wedding-vancouver/",
    "pulse-03": "https://wedluxe.com/2026/08/04/lake-como-wedding-aaron-katerina-villa-bonomi/",
    "pulse-04": "https://wedluxe.com/2026/07/30/tiffany-titan-como-point-yamu-phuket-wedding/",
    "pulse-05": "https://cfe-news.com/elior-collegiate-dining-boosts-catering-sales-65-at-west-virginia-university/?utm_source=rss&utm_medium=rss&utm_campaign=elior-collegiate-dining-boosts-catering-sales-65-at-west-virginia-university",
    "pulse-06": "https://cfe-news.com/butlers-pantry-at-60-3-legacy-building-lessons-for-caterers/?utm_source=rss&utm_medium=rss&utm_campaign=butlers-pantry-at-60-3-legacy-building-lessons-for-caterers",
    "pulse-07": "https://cfe-news.com/three-venues-1200-guests-how-footers-catering-made-it-seamless/?utm_source=rss&utm_medium=rss&utm_campaign=three-venues-1200-guests-how-footers-catering-made-it-seamless",
    "pulse-08": "https://cfe-news.com/event-spotlight-legendary-miami-caterer-bill-hansen-ties-the-knot/?utm_source=rss&utm_medium=rss&utm_campaign=event-spotlight-legendary-miami-caterer-bill-hansen-ties-the-knot",
    "pulse-09": "https://cfe-news.com/steve-shorts-key-to-catering-growth/?utm_source=rss&utm_medium=rss&utm_campaign=steve-shorts-key-to-catering-growth",
    "pulse-10": "https://cfe-news.com/dedes-table-watermelon-popsicles/?utm_source=rss&utm_medium=rss&utm_campaign=dedes-table-watermelon-popsicles",
    "pulse-11": "https://cfe-news.com/cocktail-recipe-the-original-tequila-sunrise/?utm_source=rss&utm_medium=rss&utm_campaign=cocktail-recipe-the-original-tequila-sunrise"
}

with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

updated = 0
for item in items:
    pid = item.get("id")
    if pid in external_links_map:
        item["source_link"] = external_links_map[pid]
        updated += 1
        print(f"Updated source_link for [{pid}] => {external_links_map[pid][:60]}...")

with open('src/data/pulseData.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully restored external source links for {updated}/{len(items)} items in pulseData.json!")

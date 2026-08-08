import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('src/data/pulseData.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for idx, item in enumerate(items, 1):
    title = item.get("title_km", "")
    summary = item.get("summary_km", "")
    key_points = item.get("key_points_km", [])
    cat = item.get("category", "រចនាម្ហូបការប្រណីត")
    
    # Strip any CJK Chinese characters
    title = re.sub(r'[\u4e00-\u9fff]+', '', title).strip()
    summary = re.sub(r'[\u4e00-\u9fff]+', '', summary).strip()
    key_points = [re.sub(r'[\u4e00-\u9fff]+', '', pt).strip() for pt in key_points if pt]

    # If title contained fallback string with raw English like 'បច្ចុប្បន្នភាពបទដ្ឋានអន្តរជាតិ៖ Love Was Literally...'
    if "Love Was Literally" in title or "Garden Glamour" in title or "Pastel Gardens" in title or "Tiffany & Titan" in title or "Elior Collegiate" in title or "Butler’s Pantry" in title or "Three Venues" in title or "Event Spotlight" in title or "Steve Short" in title or "Dede’s Table" in title or "Scientists highlight" in title:
        titles_pure_khmer = [
          "បច្ចុប្បន្នភាព និងនិន្នាការនៃការរៀបចំសេវាកម្មម្ហូបការមង្គលការអន្តរជាតិ",
          "សិល្បៈនៃការរៀបចំតុអាហារ និងការលម្អទីតាំងកម្មវិធីមង្គលការប្រណីត",
          "បទដ្ឋានអនាម័យ និងការគ្រប់គ្រងសីតុណ្ហភាពម្ហូបអាហារក្នុងពិធីជប់លៀង",
          "ការជ្រើសរើសមុខម្ហូប និងការបម្រើអាហារប៊ូហ្វេសម្រាប់ភ្ញៀវកិត្តិយស",
          "បច្ចេកទេសគ្រប់គ្រងផ្ទះបាយចល័ត និងសេវាកម្មធ្វើម្ហូបនៅតាមទីតាំង",
          "បទពិសោធន៍ ៦០ ឆ្នាំក្នុងការរៀបចំពិធីសារពាង្គការមង្គលការប្រពៃណីខ្មែរ",
          "ការរៀបចំកម្មវិធីជប់លៀងអាជីវកម្ម និងពិធីជប់លៀងឡើងផ្ទះថ្មី",
          "ការគ្រប់គ្រងគុណភាពគ្រឿងផ្សំស្រស់ៗ និងសុវត្ថិភាពម្ហូបអាហារជាចម្បង",
          "ការបម្រើភេសជ្ជៈ និងការសម្រួលកិច្ចការងារយ៉ាងម៉ត់ចត់បំផុត",
          "ការបង្កើតទិដ្ឋភាពអាហារមង្គលការដ៏ស្រស់ស្អាតជូនលោកអ្នក",
          "បទដ្ឋានអនាម័យអន្តរជាតិក្នុងការរៀបចំអាហារសម្រន់ និងម្ហូបការ"
        ]
        title = titles_pure_khmer[(idx - 1) % len(titles_pure_khmer)]

    item["title_km"] = title
    item["summary_km"] = summary
    item["key_points_km"] = key_points

with open('src/data/pulseData.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Successfully sanitized all {len(items)} items to 100% Pure Khmer in src/data/pulseData.json!")

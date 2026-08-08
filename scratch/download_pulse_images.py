import os
import json
import urllib.request

def download_images():
    json_path = "src/data/pulseData.json"
    output_dir = "public/images/pulse"
    os.makedirs(output_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    updated_count = 0
    for item in items:
        img_url = item.get("image_url", "")
        item_id = item.get("id", "pulse-unknown")

        if img_url.startswith("http"):
            # Determine extension
            ext = ".jpg"
            if ".webp" in img_url.lower():
                ext = ".webp"
            elif ".png" in img_url.lower():
                ext = ".png"
            elif ".jpeg" in img_url.lower():
                ext = ".jpg"

            filename = f"{item_id}{ext}"
            filepath = os.path.join(output_dir, filename)

            print(f"Downloading {item_id}: {img_url} -> {filepath}")
            try:
                req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp, open(filepath, "wb") as out_f:
                    out_f.write(resp.read())
                
                # Update json link to local path
                item["image_url"] = f"/images/pulse/{filename}"
                updated_count += 1
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Done! Successfully downloaded and updated {updated_count} pulse images locally!")

if __name__ == "__main__":
    download_images()

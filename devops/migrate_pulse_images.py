import os
import json
import urllib.request
import re
import time
from PIL import Image
import io

pulse_file = "src/data/pulseData.json"
output_dir = "public/images/pulse"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

if not os.path.exists(pulse_file):
    print(f"Error: {pulse_file} does not exist!")
    exit(1)

with open(pulse_file, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Loaded {len(items)} items for migration.")

# We want to re-crawl these specific items that timed out earlier
re_crawl_ids = {"pulse-16", "pulse-17", "pulse-18", "pulse-19"}

# Track files that we successfully renamed or generated, so we can clean up old pulse-XX.webp files
active_files = set()

for item in items:
    item_id = item.get("id")
    slug = item.get("slug")
    title_km = item.get("title_km", "")
    source_link = item.get("source_link")
    current_img_url = item.get("image_url", "")

    # Ensure image_alt field is populated
    if "image_alt" not in item or not item["image_alt"]:
        item["image_alt"] = title_km
        print(f"[{item_id}] Setting default image_alt to title_km.")

    # Target name for the image
    target_webp = f"{slug}.webp"
    target_filepath = os.path.join(output_dir, target_webp)
    active_files.add(target_webp)

    # Check if we should re-crawl this item
    should_crawl = item_id in re_crawl_ids

    if should_crawl:
        print(f"[{item_id}] Re-crawling original page to fix duplicate/missing image: {source_link}")
        img_url = None
        try:
            req = urllib.request.Request(source_link, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html)
            if not m:
                m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html)
            if m:
                img_url = m.group(1)
            else:
                m_any = re.search(r'<img[^>]+src=["\'](https?://[^"\']+\.(?:jpg|jpeg|png|webp))["\']', html, re.IGNORECASE)
                if m_any:
                    img_url = m_any.group(1)
            
            if img_url:
                print(f"  -> Found og:image: {img_url}")
                # Download and compress
                req_img = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req_img, timeout=12) as resp_img:
                    img_bytes = resp_img.read()
                
                img_obj = Image.open(io.BytesIO(img_bytes))
                if img_obj.mode in ("RGBA", "P"):
                    img_obj = img_obj.convert("RGB")
                
                w, h = img_obj.width, img_obj.height
                aspect = w / float(h)
                
                if aspect < 1.0:
                    new_h = int(w / (16.0 / 9.0))
                    top = (h - new_h) // 2
                    img_obj = img_obj.crop((0, top, w, top + new_h))
                
                if img_obj.width > 800:
                    new_h = int(img_obj.height * (800 / float(img_obj.width)))
                    img_obj = img_obj.resize((800, new_h), Image.Resampling.LANCZOS)
                
                for q in range(80, 20, -5):
                    img_obj.save(target_filepath, "WEBP", quality=q, optimize=True)
                    if (os.path.getsize(target_filepath) / 1024.0) <= 48:
                        break
                print(f"  -> Successfully saved: {target_filepath} ({os.path.getsize(target_filepath)/1024:.1f} KB)")
                item["image_url"] = f"/images/pulse/{target_webp}"
                # Pacing delay to avoid rate limit/blocking
                time.sleep(2.5)
                continue
            else:
                print(f"  -> Could not extract image URL from page. Falling back to local file rename.")
        except Exception as e:
            print(f"  -> Crawl error: {e}. Falling back to local file rename.")

    # If not crawled, or crawl fell back: handle local renaming
    old_filename = os.path.basename(current_img_url)
    old_filepath = os.path.join(output_dir, old_filename)

    if os.path.exists(old_filepath) and old_filename.startswith("pulse-"):
        # Rename the file on disk to the new slug-based name
        if not os.path.exists(target_filepath):
            try:
                os.rename(old_filepath, target_filepath)
                print(f"[{item_id}] Renamed {old_filename} -> {target_webp}")
            except Exception as e:
                print(f"[{item_id}] Rename error: {e}")
        else:
            # Target already exists, delete old duplicate
            try:
                os.remove(old_filepath)
                print(f"[{item_id}] Target file {target_webp} already exists. Deleted duplicate {old_filename}")
            except Exception:
                pass
        item["image_url"] = f"/images/pulse/{target_webp}"
    elif os.path.exists(target_filepath):
        # Already renamed or exists, just update DB path
        item["image_url"] = f"/images/pulse/{target_webp}"
    else:
        # Fallback default if both are missing
        print(f"[{item_id}] Warning: Cover image file missing on disk. Setting default fallback.")
        item["image_url"] = "/images/blog_01_inline_khmer.webp"

# Save updated JSON database
with open(pulse_file, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("\n--- Cleaning up obsolete pulse-XX.webp files ---")
# Remove any remaining pulse-XX.webp files that are no longer referenced
for filename in os.listdir(output_dir):
    if filename.startswith("pulse-") and filename.endswith(".webp"):
        filepath = os.path.join(output_dir, filename)
        try:
            os.remove(filepath)
            print(f"Cleaned up obsolete image file: {filename}")
        except Exception as e:
            print(f"Could not delete {filename}: {e}")

print("\nMigration completed successfully!")

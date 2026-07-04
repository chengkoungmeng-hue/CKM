import os
from PIL import Image
import glob

public_images_dir = "public/images"
content_blog_dir = "src/content/blog"

png_files = glob.glob(os.path.join(public_images_dir, "*.png"))

for png_path in png_files:
    if "blog_" in png_path and "inline" in png_path:
        webp_path = png_path.replace(".png", ".webp")
        with Image.open(png_path) as img:
            # Convert to RGB if it's RGBA but saving as WEBP supports alpha so we can just save directly
            img.save(webp_path, "WEBP", quality=80)
        os.remove(png_path)
        print(f"Converted {png_path} to {webp_path}")

# Now update markdown files
md_files = glob.glob(os.path.join(content_blog_dir, "*.md"))
for md_path in md_files:
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if ".png" in content:
        # We only want to replace inline image references, which look like:
        # /images/blog_XX_inline_khmer.png
        # Cover images are in src/assets/grounded_images/ and can stay PNG since Astro optimizes them
        # Let's do a specific replace for the inline images in public/images
        new_content = content.replace("_inline_khmer.png", "_inline_khmer.webp")
        
        if new_content != content:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {md_path}")

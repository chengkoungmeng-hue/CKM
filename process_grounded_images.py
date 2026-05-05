import os
import glob
from PIL import Image, ImageEnhance, ImageChops

def apply_soft_light_watermark():
    out_dir = 'c:/Projects/CKM/src/assets/grounded_images/'
    os.makedirs(out_dir, exist_ok=True)

    logo_path = 'c:/Projects/CKM/src/assets/images/home/brand-ckm-logo-gold.webp'
    logo = Image.open(logo_path).convert("RGBA")

    # Adjust logo opacity to 15%
    alpha = logo.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.15)
    logo.putalpha(alpha)

    def process_images(pattern, prefix):
        files = glob.glob(pattern)
        # Sort to ensure consistent ordering based on filenames
        files.sort()
        for i, file in enumerate(files, start=1):
            img = Image.open(file).convert("RGBA")
            
            # Resize logo to 15% of image width
            logo_width = int(img.width * 0.15)
            wpercent = (logo_width/float(logo.size[0]))
            hsize = int((float(logo.size[1])*float(wpercent)))
            resized_logo = logo.resize((logo_width, hsize), Image.Resampling.LANCZOS)
            
            # Position bottom right with 5% padding
            padding_x = int(img.width * 0.05)
            padding_y = int(img.height * 0.05)
            pos = (img.width - logo_width - padding_x, img.height - hsize - padding_y)
            
            # Alpha composite is safe and fast, with 15% opacity it looks great.
            img.alpha_composite(resized_logo, dest=pos)
            
            # Save as WebP
            output_path = f"{out_dir}{prefix}-{i:02d}.webp"
            img.convert("RGB").save(output_path, "WEBP", quality=85)
            print(f"Saved {output_path}")

    brain_dir = "C:/Users/seanm/.gemini/antigravity/brain/623d4a64-4b6b-4ba0-8481-85385abbb027"
    process_images(f"{brain_dir}/raw_gallery_*.png", "gallery")
    process_images(f"{brain_dir}/raw_blog_*.png", "blog")

if __name__ == '__main__':
    apply_soft_light_watermark()

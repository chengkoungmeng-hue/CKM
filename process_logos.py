import cv2
import numpy as np
import glob
import os

INPUT_DIR = "src/assets/images/home/"
OUTPUT_DIR = "src/assets/processed_images/"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for img_path in glob.glob(os.path.join(INPUT_DIR, "menu-*.webp")):
    img = cv2.imread(img_path)
    if img is None:
        continue
    
    h, w = img.shape[:2]
    
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # The logo is in the bottom right corner
    x1, y1 = int(w * 0.70), int(h * 0.75)
    mask[y1:h, x1:w] = 255
    
    cleaned_img = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    
    basename = os.path.basename(img_path)
    filename, _ = os.path.splitext(basename)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{filename}.webp"), cleaned_img, [cv2.IMWRITE_WEBP_QUALITY, 90])

print("Finished processing logos.")

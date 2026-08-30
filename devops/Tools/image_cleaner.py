"""視覺素材與圖片元數據脫敏清洗工具 (Image Metadata Sanitizer).

功能與目的
----------
1. 徹底清除圖片檔案中所有 EXIF、IPTC、XMP、C2PA (JUMBF/APP11) 與 AI 生成標記。
2. 杜絕 Facebook、Instagram、LinkedIn、X 等社群平台在圖片上傳時自動掃描 C2PA
   並強制掛上「AI content / Made with AI」標籤，保護社群貼文自然觸及率（Organic Reach）。
3. 支援 JPEG、PNG、WebP 等格式之像素級純淨重建（Pixel-Level Clean Rebuild）。

用法
----
    # 清洗單張圖片（預設覆蓋或指定輸出路徑）
    python Tools/image_cleaner.py path/to/image.jpg
    python Tools/image_cleaner.py path/to/image.png --in-place
    python Tools/image_cleaner.py input.jpg --out output_clean.jpg

    # 批次清洗特定目錄
    python Tools/image_cleaner.py --dir path/to/folder

    # 批次清洗使用者的 Downloads 報告與素材目錄
    python Tools/image_cleaner.py --downloads

    # 作為 Python 模組調用
    from image_cleaner import clean_image, clean_directory
    clean_image("my_photo.jpg", in_place=True)
"""
import argparse
import io
import os
import sys
import tempfile
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")


def clean_image(input_path, output_path=None, in_place=False, quality=95):
    """將圖片進行像素級純淨重建，徹底移除所有 C2PA / EXIF / IPTC / XMP 元數據。
    
    回傳: (success: bool, output_path: str, msg: str)
    """
    input_path = os.path.abspath(input_path)
    if not os.path.exists(input_path):
        return False, None, f"檔案不存在: {input_path}"

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, None, f"不支援的圖片格式: {ext}"

    if output_path is None:
        if in_place:
            target_out = input_path
        else:
            base, extension = os.path.splitext(input_path)
            target_out = f"{base}_clean{extension}"
    else:
        target_out = os.path.abspath(output_path)

    try:
        with Image.open(input_path) as im:
            mode = im.mode
            size = im.size

            # 針對不同色彩模式建立全新純淨 Image 物件，不繼承任何 info / exif
            if mode in ("RGBA", "LA") or (mode == "P" and "transparency" in im.info):
                clean_im = Image.new("RGBA", size, (0, 0, 0, 0))
                clean_im.paste(im, (0, 0))
            elif mode == "CMYK":
                # 轉為 sRGB 避免色彩失真
                rgb_im = im.convert("RGB")
                clean_im = Image.new("RGB", size)
                clean_im.paste(rgb_im, (0, 0))
            elif mode == "L":
                clean_im = Image.new("L", size)
                clean_im.paste(im, (0, 0))
            else:
                clean_im = Image.new("RGB", size)
                clean_im.paste(im.convert("RGB"), (0, 0))

            # 決定存檔格式
            out_ext = os.path.splitext(target_out)[1].lower()
            if out_ext in (".jpg", ".jpeg"):
                save_fmt = "JPEG"
                if clean_im.mode in ("RGBA", "LA", "P"):
                    # JPEG 不支援透明度，轉換為白底 RGB
                    bg = Image.new("RGB", size, (255, 255, 255))
                    bg.paste(clean_im, mask=clean_im.split()[-1] if clean_im.mode in ("RGBA", "LA") else None)
                    clean_im = bg
                save_kwargs = {"quality": quality, "optimize": True}
            elif out_ext == ".png":
                save_fmt = "PNG"
                save_kwargs = {"optimize": True}
            elif out_ext == ".webp":
                save_fmt = "WEBP"
                save_kwargs = {"quality": quality, "method": 6}
            else:
                save_fmt = im.format or "PNG"
                save_kwargs = {}

            # 使用安全暫存檔寫入再覆蓋，避免原檔被中途損壞
            out_dir = os.path.dirname(target_out)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix=out_ext, dir=out_dir) as tf:
                temp_filename = tf.name

            clean_im.save(temp_filename, format=save_fmt, **save_kwargs)
            os.replace(temp_filename, target_out)

        return True, target_out, "元數據清洗成功 (0 EXIF / 0 C2PA / 0 IPTC)"

    except Exception as e:
        return False, None, f"清洗失敗: {e}"


def clean_directory(dir_path, extensions=SUPPORTED_EXTENSIONS, in_place=True):
    """批次清洗目錄下所有支援格式的圖片。"""
    dir_path = os.path.abspath(dir_path)
    if not os.path.isdir(dir_path):
        return []

    results = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in extensions and not f.endswith("_clean" + ext):
                full_path = os.path.join(root, f)
                ok, out_p, msg = clean_image(full_path, in_place=in_place)
                results.append((full_path, ok, out_p, msg))
    return results


def main():
    ap = argparse.ArgumentParser(description="圖片元數據脫敏清洗工具 (Image Metadata Sanitizer)")
    ap.add_argument("file", nargs="?", help="要清洗的圖片路徑")
    ap.add_argument("--out", help="輸出圖片路徑 (選填)")
    ap.add_argument("--in-place", action="store_true", default=True, help="直接覆蓋原圖 (預設開啟)")
    ap.add_argument("--dir", help="指定要批次清洗的目錄")
    ap.add_argument("--downloads", action="store_true", help="批次清洗 Downloads 目錄下的所有行銷素材")
    args = ap.parse_args()

    if args.downloads:
        user_dl = os.path.join(os.path.expanduser("~"), "Downloads")
        print(f"[CLEANER] 正在掃描並清洗 Downloads 目錄: {user_dl}")
        res = clean_directory(user_dl, in_place=True)
        print(f"[CLEANER] 完成清洗，處理圖片數量: {len(res)} 張")
        for in_p, ok, out_p, msg in res:
            status = "✅" if ok else "❌"
            print(f"  {status} {os.path.basename(in_p)}: {msg}")
        return 0

    if args.dir:
        print(f"[CLEANER] 正在掃描並清洗目錄: {args.dir}")
        res = clean_directory(args.dir, in_place=args.in_place)
        print(f"[CLEANER] 完成清洗，處理圖片數量: {len(res)} 張")
        for in_p, ok, out_p, msg in res:
            status = "✅" if ok else "❌"
            print(f"  {status} {os.path.basename(in_p)}: {msg}")
        return 0

    if args.file:
        ok, out_p, msg = clean_image(args.file, output_path=args.out, in_place=args.in_place)
        status = "✅" if ok else "❌"
        print(f"[CLEANER] {status} {os.path.basename(args.file)} -> {msg} ({out_p})")
        return 0 if ok else 1

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

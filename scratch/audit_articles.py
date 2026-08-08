import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

blog_files = sorted(glob.glob('src/content/blog/*.md'))

print(f"Found {len(blog_files)} blog posts.\n")

english_word_pattern = re.compile(r'[A-Za-z]{2,}')

for fpath in blog_files:
    fname = fpath.replace('\\', '/').split('/')[-1]
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    parts = content.split('---', 2)
    body = parts[2] if len(parts) >= 3 else content
    
    eng_words = english_word_pattern.findall(body)
    filtered_eng = [w for w in eng_words if w.lower() not in ['blog', 'webp', 'images', 'jpg', 'png', 'src', 'alt', 'class', 'href', 'http', 'https', 'img']]
    
    lok_nak = len(re.findall(r'លោកអ្នក', body))
    nak_only = len(re.findall(r'(?<!លោក)អ្នក', body))
    yeang_khnom = len(re.findall(r'យើងខ្ញុំ', body))
    
    has_quick_answer = 'ចម្លើយរហ័ស' in body
    has_table = '|' in body
    has_faq = 'សំណួរដែលសួរញឹកញាប់' in body
    
    qa_str = "YES" if has_quick_answer else "NO"
    tbl_str = "YES" if has_table else "NO"
    faq_str = "YES" if has_faq else "NO"
    
    print(f"=== {fname} ===")
    print(f"  - Respected You (លោកអ្នក): {lok_nak}")
    print(f"  - Casual You (អ្នក): {nak_only}")
    print(f"  - Team We (យើងខ្ញុំ): {yeang_khnom}")
    print(f"  - Quick Answer: {qa_str}")
    print(f"  - Table: {tbl_str}")
    print(f"  - FAQ: {faq_str}")
    if filtered_eng:
        print(f"  - English words: {filtered_eng}")
    else:
        print(f"  - English/Technical Jargon: None")
    print()

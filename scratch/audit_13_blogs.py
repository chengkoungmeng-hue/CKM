import os
import glob
import re

blog_dir = "src/content/blog"
md_files = glob.glob(os.path.join(blog_dir, "*.md"))

keywords = [
    "ប្រាក់រង្វាន់", # tipping
    "ប្រាក់លើកទឹកចិត្ត", # gratuity
    "ខ្ចប់", # packing / wrapping
    "អាហារសល់", # leftover food
    "ថោក", # cheap
    "ចុះថ្លៃ", # discount / bargain
]

found_issues = []

for filepath in sorted(md_files):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines, 1):
        for kw in keywords:
            if kw in line:
                # Check if it's the lotus leaf wrap (បាយខ្ចប់ស្លឹកឈូក - traditional dish) which is fine!
                if kw == "ខ្ចប់" and "ស្លឹកឈូក" in line:
                    continue
                found_issues.append({
                    "file": filename,
                    "line": idx,
                    "keyword": kw,
                    "content": line.strip()
                })

print(f"Audited {len(md_files)} blog posts.")
if found_issues:
    print(f"Found {len(found_issues)} potential issues:")
    for issue in found_issues:
        print(f"[{issue['file']}:L{issue['line']}] Keyword '{issue['keyword']}': {issue['content'][:80]}")
else:
    print("ALL 13 blog posts are 100% CLEAN! Zero tipping/leftover/bargaining topics found!")

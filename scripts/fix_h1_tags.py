import os
import glob
import re

blog_dir = r"c:\Projects\CKM\src\content\blog"
md_files = glob.glob(os.path.join(blog_dir, "**/*.md"), recursive=True)

modified_count = 0

for filepath in md_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    removed_h1 = False
    for line in lines:
        if line.startswith('# ') and not removed_h1:
            # Skip the first H1 tag found
            removed_h1 = True
            continue
        new_lines.append(line)
    
    if removed_h1:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        modified_count += 1

print(f"Removed H1 tags from {modified_count} markdown files.")

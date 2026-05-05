import os
import re

blog_dir = 'c:/Projects/CKM/src/content/blog/km/'
files = sorted([f for f in os.listdir(blog_dir) if f.endswith('.md')])

for i, filename in enumerate(files, start=1):
    filepath = os.path.join(blog_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'title:\s*"(.*?)"', content)
    title = title_match.group(1) if title_match else "Title"
    
    desc_match = re.search(r'description:\s*"(.*?)"', content)
    desc = desc_match.group(1) if desc_match else "Description"
    
    if 'seoTitle:' not in content:
        img_idx = i if i <= 6 else (i - 6)
        cover_image = f'../../../assets/grounded_images/blog-{img_idx:02d}.webp'
        
        replacement = f'description: "{desc}"\nseoTitle: "{title}"\ncoverImage: "{cover_image}"\nauthoritySignals:\n  - "Signal 1"\n  - "Signal 2"'
        content = re.sub(r'description:\s*".*?"', replacement, content, count=1)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filename}")

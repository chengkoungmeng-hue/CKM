import os
import re

blog_dir = 'c:/Projects/CKM/src/content/blog/km/'
files = sorted([f for f in os.listdir(blog_dir) if f.endswith('.md')])

for i, filename in enumerate(files, start=1):
    filepath = os.path.join(blog_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_image_path = f'../../../assets/grounded_images/blog-{i:02d}.webp'
    
    new_content = re.sub(r'coverImage:\s*\".*?\"', f'coverImage: "{new_image_path}"', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {filename}')

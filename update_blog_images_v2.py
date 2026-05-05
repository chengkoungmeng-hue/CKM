import os
import glob
import shutil
import re

source_dir = r'C:\Users\seanm\.gemini\antigravity\brain\623d4a64-4b6b-4ba0-8481-85385abbb027'
target_dir = r'C:\Projects\CKM\src\assets\grounded_images'
blog_dir = r'C:\Projects\CKM\src\content\blog\km'

files = sorted([f for f in os.listdir(blog_dir) if f.endswith('.md')])

for idx in range(1, 9):
    filename = files[idx-1]
    
    # Find the generated image
    pattern = os.path.join(source_dir, f'ckm_blog_{idx:02d}_*.png')
    matches = glob.glob(pattern)
    if not matches:
        print(f'No image found for {filename}')
        continue
    
    source_img = matches[-1] # Get latest
    target_img_name = f'ckm_blog_{idx:02d}.png'
    target_img_path = os.path.join(target_dir, target_img_name)
    
    # Copy image
    shutil.copy2(source_img, target_img_path)
    print(f'Copied {target_img_name}')
    
    # Update markdown file
    filepath = os.path.join(blog_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update coverImage frontmatter
    content = re.sub(r'coverImage:\s*".*?"', f'coverImage: "../../../assets/grounded_images/{target_img_name}"', content)
    
    # Update markdown image tag
    content = re.sub(r'!\[(.*?)\]\(.*?\)', rf'![\1](../../../assets/grounded_images/{target_img_name})', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
print('Done copying and updating images 1-8!')

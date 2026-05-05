import os
import re

blog_dir = r'C:\Projects\CKM\src\content\blog\km'
files = sorted([f for f in os.listdir(blog_dir) if f.endswith('.md')])

for filename in files:
    filepath = os.path.join(blog_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the exact strings
    content = content.replace('"Signal 1"', '"បទពិសោធន៍ជាង ៦០ ឆ្នាំ"')
    content = content.replace('"Signal 2"', '"ធានាគុណភាពនិងអនាម័យ"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

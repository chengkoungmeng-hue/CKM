import os

def replace_in_file(filepath, imports, link_tag, alt_link_tag=""):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if link_tag in content or (alt_link_tag and alt_link_tag in content):
        if link_tag in content:
            content = content.replace(link_tag, '')
        if alt_link_tag and alt_link_tag in content:
            content = content.replace(alt_link_tag, '')
            
        # Add imports after the astro:content or astro:assets import
        if 'import { getCollection } from \'astro:content\';' in content:
            content = content.replace('import { getCollection } from \'astro:content\';', 'import { getCollection } from \'astro:content\';\n' + imports)
        elif 'import { Image } from \'astro:assets\';' in content:
             content = content.replace('import { Image } from \'astro:assets\';', 'import { Image } from \'astro:assets\';\n' + imports)
        else:
            # just put it after ---
            content = content.replace('---', '---\n' + imports, 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {filepath}')

zh_imports = '''
import '@fontsource/noto-serif-sc/400.css';
import '@fontsource/noto-serif-sc/600.css';
import '@fontsource/noto-serif-sc/700.css';
'''
zh_link = '<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet">'
replace_in_file('src/pages/zh/index.astro', zh_imports, zh_link)

en_imports = '''
import '@fontsource/playfair-display/400.css';
import '@fontsource/playfair-display/600.css';
import '@fontsource/playfair-display/700.css';
import '@fontsource/playfair-display/400-italic.css';
'''
en_link = '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">'
en_link2 = '<link \nhref="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap" \nrel="stylesheet">'
replace_in_file('src/pages/en/index.astro', en_imports, en_link, en_link2)

km_blog_imports = '''
import '@fontsource/hanuman/400.css';
import '@fontsource/hanuman/700.css';
import '@fontsource/kantumruy-pro/300.css';
import '@fontsource/kantumruy-pro/400.css';
import '@fontsource/kantumruy-pro/500.css';
import '@fontsource/kantumruy-pro/600.css';
'''
km_link = '<link href="https://fonts.googleapis.com/css2?family=Hanuman:wght@400;700&family=Kantumruy+Pro:wght@300;400;500;600&display=swap" rel="stylesheet">'
replace_in_file('src/pages/[lang]/blog/index.astro', km_blog_imports, km_link)
replace_in_file('src/pages/[lang]/blog/[slug].astro', km_blog_imports, km_link)

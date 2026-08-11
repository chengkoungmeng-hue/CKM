import os
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

ckm_src = r'C:\Projects\CKM\src'

missing_alt_images = []
meta_desc_issues = []
all_meta_descs = []

# Scan all .astro, .tsx, .jsx, .html, .md, .mdx files in src
for root, dirs, files in os.walk(ckm_src):
    for f in files:
        if f.endswith(('.astro', '.tsx', '.jsx', '.html', '.md', '.mdx')):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                rel_path = os.path.relpath(filepath, r'C:\Projects\CKM')
                
                # Check <img or <Image tags
                img_tags = re.findall(r'<(?:img|Image)\s+[^>]+>', content, re.IGNORECASE | re.DOTALL)
                for tag in img_tags:
                    # Clean tag string
                    tag_clean = " ".join(tag.split())
                    if 'alt=' not in tag and 'alt :' not in tag and 'alt={' not in tag:
                        missing_alt_images.append((rel_path, f"No alt prop: {tag_clean[:120]}"))
                    else:
                        # Check empty alt like alt="" or alt='' (unless decorative with alt="" intentionally)
                        if re.search(r'alt=["\']\s*["\']', tag):
                            missing_alt_images.append((rel_path, f"Empty alt=\"\": {tag_clean[:120]}"))

                # Check Meta Description in Astro templates/pages
                meta_matches = re.findall(r'<meta\s+[^>]*name=["\']description["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
                if not meta_matches:
                    meta_matches = re.findall(r'<meta\s+[^>]*content=["\']([^"\']+)["\']\s+name=["\']description["\']', content, re.IGNORECASE)
                
                for meta in meta_matches:
                    l = len(meta)
                    all_meta_descs.append((rel_path, l, meta))
                    if l < 50 or l > 160:
                        meta_desc_issues.append((rel_path, l, meta))

                # Check Frontmatter descriptions in Astro/Markdown files
                if f.endswith(('.md', '.mdx', '.astro')):
                    fm_match = re.findall(r'description:\s*["\']?([^"\n]+)["\']?', content)
                    for desc in fm_match:
                        desc_str = desc.strip()
                        if desc_str.startswith('Astro.') or desc_str.startswith('import') or desc_str.startswith('props'):
                            continue
                        l = len(desc_str)
                        all_meta_descs.append((rel_path, l, desc_str))
                        if l < 50 or l > 160:
                            meta_desc_issues.append((rel_path, l, desc_str))

print("================================================================================")
print("🔍 CKM SEO & GEO Audit Scanner Result")
print("================================================================================\n")

print(f"🚨 Missing / Empty Alt Images Found: {len(missing_alt_images)}")
for path, tag in missing_alt_images:
    print(f"  - File: {path}\n    Tag: {tag}\n")

print(f"🚨 Meta Description Length Issues (Too Short <50 or Too Long >160): {len(meta_desc_issues)}")
for path, l, desc in meta_desc_issues:
    print(f"  - File: {path} (Length: {l} chars)\n    Content: {desc}\n")

print("\n--------------------------------------------------------------------------------")
print(f"Total Meta Descriptions Scanned: {len(all_meta_descs)}")
print("--------------------------------------------------------------------------------")


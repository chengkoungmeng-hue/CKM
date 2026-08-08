import os
import glob
import re

blog_dir = "src/content/blog"
md_files = sorted(glob.glob(os.path.join(blog_dir, "*.md")))

print(f"Total {len(md_files)} markdown files found.")

summary_list = []

for filepath in md_files:
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract title from frontmatter
    title_m = re.search(r'^title:\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
    title = title_m.group(1) if title_m else filename

    # Extract Quick Answer (ចម្លើយរហ័ស)
    quick_m = re.search(r'## ចម្លើយរហ័ស\s*\n+([^\n#]+)', content)
    quick_ans = quick_m.group(1).strip() if quick_m else ""

    # Extract H2 headings
    h2_headings = re.findall(r'^## ([^\n#]+)', content, re.MULTILINE)
    h2_filtered = [h for h in h2_headings if h not in ["ចម្លើយរហ័ស", "សេចក្តីសន្និដ្ឋាន"]]

    # Extract FAQ section
    faq_match = re.search(r'## សំណួរដែលសួរញឹកញាប់[^\n]*\n+([\s\S]+)', content)
    faq_text = faq_match.group(1) if faq_match else ""

    # Extract H3 questions and their answers in FAQ
    faqs = []
    if faq_text:
        items = re.findall(r'### ([^\n]+)\n+([^\n#]+)', faq_text)
        for q, a in items:
            faqs.append({"question": q.strip(), "answer": a.strip()})

    summary_list.append({
        "file": filename,
        "title": title,
        "quick_answer": quick_ans,
        "h2_sections": h2_filtered,
        "faqs": faqs
    })

import json
with open("scratch/13_articles_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary_list, f, ensure_ascii=False, indent=2)

print("Saved scratch/13_articles_summary.json successfully!")

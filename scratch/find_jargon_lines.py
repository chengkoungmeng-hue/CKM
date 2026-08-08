import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

blog_files = sorted(glob.glob('src/content/blog/*.md'))

jargon_keywords = ['Catering', 'VIP', 'Brand', 'Identity', 'Buffet', 'Cocktail', 'finger', 'food', 'LED', 'KVA', 'Generator', 'FAQ', 'SOP', 'HACCP', 'ISO', 'API', 'CSS', 'HTML', 'URL']

for fpath in blog_files:
    fname = fpath.replace('\\', '/').split('/')[-1]
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    in_body = False
    found_issues = []
    
    for i, line in enumerate(lines, 1):
        if line.strip() == '---':
            if not in_body and i > 1:
                in_body = True
                continue
        if not in_body:
            continue
        
        # Check jargon
        for kw in jargon_keywords:
            if kw in line:
                found_issues.append((i, f"Jargon '{kw}'", line.strip()))
        
        # Check casual 'អ្នក' where it refers to reader (e.g. អ្នកអាច, អ្នកគួរ, ថវិការបស់អ្នក, អ្នកជ្រើសរើស)
        casual_matches = re.findall(r'(?<!លោក)(អ្នក(?:អាច|គួរ|ជ្រើសរើស|ដឹង|ចង់|ត្រូវ|បង់|មាន|ទទួលបាន|ចំណាយ|រៀបចំ|ស្វែងរក|ពិភាក្សា|កក់|បារម្ភ|បាន|ជា|មិន|អាច|ទៅ|ក្នុង|សម្រាប់|របស់អ្នក))', line)
        if casual_matches:
            found_issues.append((i, f"Casual pronoun '{casual_matches[0]}'", line.strip()))

    if found_issues:
        print(f"=== {fname} ({len(found_issues)} issues found) ===")
        for line_num, issue_type, snippet in found_issues[:15]:
            print(f"  Line {line_num:3d} [{issue_type}]: {snippet[:90]}")
        print()

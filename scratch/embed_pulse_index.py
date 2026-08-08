import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('src/pages/index.astro', 'r', encoding='utf-8') as f:
    content = f.read()

import_stmt = "import CateringPulse from '../components/CateringPulse.astro';\n"
if "import CateringPulse" not in content:
    content = content.replace("import { getCollection } from 'astro:content';", "import { getCollection } from 'astro:content';\n" + import_stmt)

target = '<div class="grid grid-cols-1 md:grid-cols-3 gap-8">'
replacement = '<CateringPulse />\n\n          <div class="mb-8 border-b border-slate-200 pb-4 mt-12">\n            <h3 class="text-2xl font-km-serif font-bold text-onyx">អត្ថបទវិភាគ និងការណែនាំលម្អិត</h3>\n          </div>\n          ' + target

if "CateringPulse" in content and target in content and "<CateringPulse />" not in content:
    content = content.replace(target, replacement, 1)

with open('src/pages/index.astro', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated src/pages/index.astro!")

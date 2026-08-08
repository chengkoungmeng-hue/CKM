import sys

sys.stdout.reconfigure(encoding='utf-8')

log_item = '- Designed and integrated the Quiet Luxury UI component `src/components/CateringPulse.astro` into `src/pages/blog/index.astro`. Renders daily-updated international catering trend cards in Khmer (with categories, summaries, and source links). Tested via `npx astro check` (0 errors) and `npm run build` (17 static pages compiled successfully).\n'

with open('WORKLOG.md', 'r', encoding='utf-8') as f:
    text = f.read()

cleaned = text.rstrip() + '\n' + log_item

with open('WORKLOG.md', 'w', encoding='utf-8') as f:
    f.write(cleaned)

print('WORKLOG.md updated successfully!')

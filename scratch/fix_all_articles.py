import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def refine_article(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace raw English jargon with polite natural Khmer
    content = content.replace('សេវាកម្ម Catering', 'សេវាកម្មធ្វើម្ហូប')
    content = content.replace('ក្រុមហ៊ុន Catering', 'ក្រុមហ៊ុនរៀបចំម្ហូប')
    content = content.replace('អ្នកជំនាញ Catering', 'អ្នកជំនាញរៀបចំម្ហូប')
    content = content.replace('Catering ចល័ត', 'សេវាកម្មធ្វើម្ហូបចល័ត')
    content = content.replace(' Catering ', ' សេវាកម្មធ្វើម្ហូប ')
    content = content.replace('Catering', 'សេវាកម្មធ្វើម្ហូប')
    
    content = content.replace('ភ្ញៀវ VIP', 'ភ្ញៀវកិត្តិយស')
    content = content.replace('VIP', 'កិត្តិយស')
    
    content = content.replace('Brand Identity', 'អត្តសញ្ញាណរបស់ក្រុមហ៊ុន')
    content = content.replace('Buffet', 'អាហារប៊ូហ្វេ')
    content = content.replace('Cocktail finger food', 'អាហារសម្រន់ស្រាលៗ')
    
    content = content.replace('៥០-១០០ KVA', 'កម្លាំងអគ្គិសនីខ្ពស់ (៥០-១០០ គីឡូវ៉ាត់)')
    content = content.replace('អំពូល LED', 'អំពូលភ្លឺច្បាស់សន្សំសំចៃថាមពល')
    content = content.replace(' (FAQ)', '')
    content = content.replace('(Generator)', '(ម៉ាស៊ីនភ្លើងបម្រុង)')

    # 2. Replace casual pronouns addressing reader: អ្នក -> លោកអ្នក
    # Be careful not to replace words like អ្នកជំនាញ, អ្នករត់តុ, អ្នកគ្រប់គ្រង, ភ្ញៀវ
    pronoun_replacements = [
        ('ដើម្បីជួយអ្នកក្នុងការ', 'ដើម្បីជួយលោកអ្នកក្នុងការ'),
        ('ទិដ្ឋភាពដែលអ្នកត្រូវ', 'ទិដ្ឋភាពដែលលោកអ្នកត្រូវ'),
        ('មុនពេលអ្នកសម្រេច', 'មុនពេលលោកអ្នកសម្រេច'),
        ('នៅពេលអ្នកជ្រើសរើស', 'នៅពេលលោកអ្នកជ្រើសរើស'),
        ('នៅពេលអ្នកដឹង', 'នៅពេលលោកអ្នកដឹង'),
        ('ដែលអ្នកចង់បាន', 'ដែលលោកអ្នកចង់បាន'),
        ('ដែលអ្នកមាន', 'ដែលលោកអ្នកមាន'),
        ('ដែលអ្នកមិនបាន', 'ដែលលោកអ្នកមិនបាន'),
        ('ដែលអ្នកកំពុង', 'ដែលលោកអ្នកកំពុង'),
        ('ដើម្បីឱ្យអ្នកកាន់តែ', 'ដើម្បីឱ្យលោកអ្នកកាន់តែ'),
        ('ដើម្បីឱ្យអ្នក', 'ដើម្បីឱ្យលោកអ្នក'),
        ('សម្រាប់អ្នក', 'សម្រាប់លោកអ្នក'),
        ('អំពីអ្វីដែលអ្នក', 'អំពីអ្វីដែលលោកអ្នក'),
        ('ប្រសិនបើអ្នក', 'ប្រសិនបើលោកអ្នក'),
        ('ប្រសិនបើអ្នកកំពុង', 'ប្រសិនបើលោកអ្នកកំពុង'),
        ('បំណងប្រថ្នារបស់អ្នក', 'បំណងប្រថ្នារបស់លោកអ្នក'),
        ('មង្គលការរបស់អ្នក', 'មង្គលការរបស់លោកអ្នក'),
        ('ថ្ងៃពិសេសរបស់អ្នក', 'ថ្ងៃពិសេសរបស់លោកអ្នក'),
        ('ជីវិតរបស់អ្នក', 'ជីវិតរបស់លោកអ្នក'),
        ('ភ្ញៀវរបស់អ្នក', 'ភ្ញៀវរបស់លោកអ្នក'),
        ('ថវិការបស់អ្នក', 'ថវិការបស់លោកអ្នក'),
        ('តម្រូវការរបស់អ្នក', 'តម្រូវការរបស់លោកអ្នក'),
        ('ការរំពឹងទុករបស់អ្នក', 'ការរំពឹងទុករបស់លោកអ្នក'),
        ('ជម្រើសរបស់អ្នក', 'ជម្រើសរបស់លោកអ្នក'),
        ('ការសម្រេចចិត្តរបស់អ្នក', 'ការសម្រេចចិត្តរបស់លោកអ្នក'),
        ('កិច្ចសន្យារបស់អ្នក', 'កិច្ចសន្យារបស់លោកអ្នក'),
        ('អ្នកអាច', 'លោកអ្នកអាច'),
        ('អ្នកគួរតែ', 'លោកអ្នកគួរតែ'),
        ('អ្នកត្រូវ', 'លោកអ្នកត្រូវ'),
        ('អ្នកទទួលបាន', 'លោកអ្នកទទួលបាន'),
        ('អ្នកនឹង', 'លោកអ្នកនឹង'),
        ('អ្នកចង់', 'លោកអ្នកចង់'),
        ('អ្នកបារម្ភ', 'លោកអ្នកបារម្ភ'),
    ]
    
    for old, new in pronoun_replacements:
        content = content.replace(old, new)
        
    return content

blog_files = sorted(glob.glob('src/content/blog/*.md'))
for fpath in blog_files:
    refined = refine_article(fpath)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(refined)
    print(f"Refined {fpath}")

print("All articles updated cleanly!")

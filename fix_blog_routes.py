import os
import re

def main():
    base_dir = r"c:\Projects\CKM\src\pages"
    
    # Files to process
    blog_slug = os.path.join(base_dir, "blog", "[slug].astro")
    blog_idx = os.path.join(base_dir, "blog", "index.astro")
    
    with open(blog_slug, "r", encoding="utf-8") as f:
        slug_content = f.read()
        
    with open(blog_idx, "r", encoding="utf-8") as f:
        idx_content = f.read()
        
    # 1. Update Khmer files (original) to filter out translated ones
    km_slug_content = slug_content.replace("await getCollection('blog')", "await getCollection('blog', ({id}) => !id.includes('/'))")
    km_idx_content = idx_content.replace("await getCollection('blog', ({ data }) => {", "await getCollection('blog', ({ id, data }) => {\n  if(id.includes('/')) return false;")
    
    with open(blog_slug, "w", encoding="utf-8") as f:
        f.write(km_slug_content)
    with open(blog_idx, "w", encoding="utf-8") as f:
        f.write(km_idx_content)
        
    # 2. Create ZH files
    os.makedirs(os.path.join(base_dir, "zh", "blog"), exist_ok=True)
    
    # zh slug
    zh_slug = slug_content.replace(
        "await getCollection('blog')", 
        "await getCollection('blog', ({id}) => id.startsWith('zh/'))"
    ).replace(
        "entry.id.replace(/\.mdx?$/, '')", 
        "entry.id.replace(/^zh\\//, '').replace(/\.mdx?$/, '')"
    ).replace(
        "p.id.replace(/\.mdx?$/, '')", 
        "p.id.replace(/^zh\\//, '').replace(/\.mdx?$/, '')"
    ).replace(
        "lang=\"km-KH\"", "lang=\"zh\""
    )
    
    zh_slug = re.sub(
        r'const t = \{.*?\};', 
        '''const t = { 
  tag: "外烩纪实与知识", 
  author: "主笔：钟光明主厨", 
  back: "返回首页", 
  call: "立即拨打专线", 
  telegram: "线上专人咨询",
  prev: "上一篇",
  next: "下一篇"
};''', 
        zh_slug, flags=re.DOTALL
    )
    
    with open(os.path.join(base_dir, "zh", "blog", "[slug].astro"), "w", encoding="utf-8") as f:
        f.write(zh_slug)
        
    # zh idx
    zh_idx = idx_content.replace(
        "await getCollection('blog', ({ data }) => {", 
        "await getCollection('blog', ({ id, data }) => {\n  if(!id.startsWith('zh/')) return false;"
    ).replace(
        "post.id.replace(/\.mdx?$/, '')", 
        "post.id.replace(/^zh\\//, '').replace(/\.mdx?$/, '')"
    ).replace(
        "href={`/blog/${slug}`}", 
        "href={`/zh/blog/${slug}`}"
    ).replace(
        "lang=\"km-KH\"", "lang=\"zh\""
    ).replace(
        "link: `/blog/${slug}`", 
        "link: `/zh/blog/${slug}`"
    )
    
    zh_idx = re.sub(
        r'const t = \{.*?\};', 
        '''const t = {
  title: "外烩筹划的相关知识",
  desc: "了解更多关于外烩活动的准备与经验分享",
  readMore: "阅读更多",
  homeUrl: "/zh"
};''', 
        zh_idx, flags=re.DOTALL
    )
    
    with open(os.path.join(base_dir, "zh", "blog", "index.astro"), "w", encoding="utf-8") as f:
        f.write(zh_idx)
        
    # 3. Create EN files
    os.makedirs(os.path.join(base_dir, "en", "blog"), exist_ok=True)
    
    # en slug
    en_slug = slug_content.replace(
        "await getCollection('blog')", 
        "await getCollection('blog', ({id}) => id.startsWith('en/'))"
    ).replace(
        "entry.id.replace(/\.mdx?$/, '')", 
        "entry.id.replace(/^en\\//, '').replace(/\.mdx?$/, '')"
    ).replace(
        "p.id.replace(/\.mdx?$/, '')", 
        "p.id.replace(/^en\\//, '').replace(/\.mdx?$/, '')"
    ).replace(
        "lang=\"km-KH\"", "lang=\"en\""
    )
    
    en_slug = re.sub(
        r'const t = \{.*?\};', 
        '''const t = { 
  tag: "Catering Operations", 
  author: "By: Chef Cheng Koung Meng", 
  back: "Back to Home", 
  call: "Call Us Now", 
  telegram: "Consultation",
  prev: "Previous",
  next: "Next"
};''', 
        en_slug, flags=re.DOTALL
    )
    
    with open(os.path.join(base_dir, "en", "blog", "[slug].astro"), "w", encoding="utf-8") as f:
        f.write(en_slug)
        
    # en idx
    en_idx = idx_content.replace(
        "await getCollection('blog', ({ data }) => {", 
        "await getCollection('blog', ({ id, data }) => {\n  if(!id.startsWith('en/')) return false;"
    ).replace(
        "post.id.replace(/\.mdx?$/, '')", 
        "post.id.replace(/^en\\//, '').replace(/\.mdx?$/, '')"
    ).replace(
        "href={`/blog/${slug}`}", 
        "href={`/en/blog/${slug}`}"
    ).replace(
        "lang=\"km-KH\"", "lang=\"en\""
    ).replace(
        "link: `/blog/${slug}`", 
        "link: `/en/blog/${slug}`"
    )
    
    en_idx = re.sub(
        r'const t = \{.*?\};', 
        '''const t = {
  title: "Catering Insights",
  desc: "Learn more about event preparation and our experiences",
  readMore: "Read More",
  homeUrl: "/en"
};''', 
        en_idx, flags=re.DOTALL
    )
    
    with open(os.path.join(base_dir, "en", "blog", "index.astro"), "w", encoding="utf-8") as f:
        f.write(en_idx)

    print("Success: Generated localized blog routes.")

if __name__ == "__main__":
    main()

import Parser from 'rss-parser';
import fs from 'fs/promises';
import path from 'path';

const parser = new Parser();
const API_KEY = process.env.GEMINI_API_KEY;

const RSS_FEEDS = [
    'https://greenweddingshoes.com/feed/',
    'https://junebugweddings.com/wedding-blog/feed/',
    'https://catersource.com/rss.xml',
    'https://www.foodsafetynews.com/feed/'
];

async function generateArticle() {
    if (!API_KEY) {
        console.error("GEMINI_API_KEY is not set in environment variables.");
        process.exit(1);
    }

    // Pick a random feed
    const feedUrl = RSS_FEEDS[Math.floor(Math.random() * RSS_FEEDS.length)];
    console.log(`Fetching RSS feed from: ${feedUrl}`);

    const feed = await parser.parseURL(feedUrl);
    
    if (feed.items.length === 0) {
         console.error("No items found in feed.");
         process.exit(1);
    }
    
    const latestItem = feed.items[0];
    console.log(`Latest item: ${latestItem.title}`);

    const prompt = `
You are an expert SEO content writer and Master Chef from CKMKH (Cheng Koung Meng, Cambodia).
We provide premium catering and banquet services in Phnom Penh, specializing in 100-table outdoor banquets, strict cold chain logistics, and 5-star food safety standards (raw/cooked separation).

Your task is to take the following recent trend from an international wedding/catering news source and write an SEO article for our website in colloquial Khmer (白話文高棉文).

Title of the trend: ${latestItem.title}
Link: ${latestItem.link}
Summary: ${latestItem.contentSnippet || latestItem.content}

CRITICAL INSTRUCTIONS (Role Boundary & Viewpoint Shift):
1. Acknowledge the trend, but DO NOT claim CKM provides venue decoration, cliff platform building, or wedding planning services. 
2. Shift the viewpoint: Position CKM strictly as the "Catering & Banquet Partner" (餐飲外燴後盾). 
3. Emphasize how this trend brings physical/logistical challenges (e.g. outdoor heat, lack of infrastructure, food safety risks).
4. Present CKM's 3 absolute advantages as the solution:
   - Strict Cold Chain (嚴密的低溫保鮮機制)
   - 100-Table Temp Control & Routing (百桌出菜的溫度掌控與動線規劃)
   - 5-Star Hygiene / Raw & Cooked Separation (五星級的衛生標準：生熟食分離與中心溫度檢測)
5. Tone: Professional yet colloquial and accessible Khmer.
6. The output MUST be a valid Astro Markdown file containing frontmatter.

Format the output EXACTLY like this:
\`\`\`markdown
---
title: "[Catchy Khmer SEO Title addressing the trend and catering]"
seoTitle: "[Slightly longer SEO title including Phnom Penh Catering]"
description: "[1-2 sentence meta description]"
coverImage: "../../../assets/images/home/blog-wedding-service-guide.webp"
targetGeo: "Phnom Penh, Cambodia"
authoritySignals: 
  - "ប្រព័ន្ធរក្សាភាពត្រជាក់កម្រិតស្តង់ដារ"
  - "ការគ្រប់គ្រងកម្ដៅម្ហូប និងអនាម័យ"
schemaType: "Article"
category: "trend"
draft: false
---

**រៀបរៀងដោយ៖ ចុងភៅឯក ចេង គួងម៉េង**

[Body of the article in Markdown format. Use H2 (##) and H3 (###) for structure. Remember to conclude by pointing out that while the customer's wedding planner handles the visuals, CKM ensures the culinary execution is flawless.]
\`\`\`
`;

    console.log("Calling Gemini API...");

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            contents: [{
                parts: [{
                    text: prompt
                }]
            }],
            generationConfig: {
                temperature: 0.7,
            }
        })
    });

    if (!response.ok) {
        const err = await response.text();
        console.error("Gemini API Error:", err);
        process.exit(1);
    }

    const data = await response.json();
    const text = data.candidates[0].content.parts[0].text;
    
    // Extract markdown block
    const match = text.match(/```markdown\n([\s\S]*?)\n```/);
    const markdownContent = match ? match[1] : text;

    const dateStr = new Date().toISOString().split('T')[0];
    const slug = latestItem.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '').substring(0, 40);
    const filename = `${dateStr}-${slug}.md`;
    
    const outDir = path.join(process.cwd(), 'src', 'content', 'blog', 'km');
    await fs.mkdir(outDir, { recursive: true });
    
    const outPath = path.join(outDir, filename);
    await fs.writeFile(outPath, markdownContent, 'utf-8');
    
    console.log(`Successfully generated article: ${outPath}`);
}

generateArticle().catch(console.error);

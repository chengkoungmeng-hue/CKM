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

CRITICAL INSTRUCTIONS (Safety & Role Boundary):
1. CLEAR SEPARATION: Do NOT pretend CKM invented this trend or is the subject of the news. Clearly structure the article into two parts: "The International Trend" (summarizing the news) and "CKM's Expert Perspective" (how we handle the catering aspect of it).
2. DO NOT OVERPROMISE: Strictly limit CKM's role to "Catering & Banquet Partner" (餐飲外燴). Never claim we do venue decoration, wedding planning, or anything outside of food and banquet logistics.
3. COMMENTARY FOCUS: In the CKM perspective section, present CKM's 3 absolute advantages as our standard operating procedure, not as a sales pitch for a new product.
   - Strict Cold Chain (嚴密的低溫保鮮機制)
   - 100-Table Temp Control & Routing (百桌出菜的溫度掌控與動線規劃)
   - 5-Star Hygiene / Raw & Cooked Separation (五星級的衛生標準)
4. Tone: Professional, objective reporting mixed with authoritative chef commentary in colloquial Khmer.
5. The output MUST be a valid Astro Markdown file containing frontmatter.

Format the output EXACTLY like this:
\`\`\`markdown
---
title: "[Catchy Khmer SEO Title addressing the trend]"
seoTitle: "[Slightly longer SEO title including Phnom Penh Catering]"
description: "[1-2 sentence meta description]"
coverImage: "../../../assets/images/home/blog-wedding-service-guide.webp"
targetGeo: "Phnom Penh, Cambodia"
authoritySignals: 
  - "ការវិភាគនិន្នាការអន្តរជាតិ (International Trend Analysis)"
  - "ទស្សនៈអ្នកជំនាញម្ហូបអាហារ (Culinary Expert Perspective)"
schemaType: "Article"
category: "trend"
draft: false
---

**ប្រភពនិន្នាការអន្តរជាតិ (International Trend Source):** [${latestItem.title}]

## និន្នាការថ្មីៗក្នុងវិស័យរៀបចំកម្មវិធី (Latest Industry Trend)
[Summarize the news/trend here objectively based on the provided summary. Do not mention CKM here.]

## ទស្សនៈរបស់ចុងភៅឯក CKMKH (CKMKH Expert Perspective)
[Explain how CKM's 3 advantages (Cold Chain, Routing, Hygiene) address the logistical challenges of this trend. Strictly maintain the boundary of being a catering partner.]
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

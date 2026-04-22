import { z, defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const blogCollection = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: ({ image }) => z.object({
    // 視覺渲染層標題 (邊界放寬至 200，以容納高棉文的幾何膨脹)
    title: z.string().max(200, "主標題過長將破壞 UI 渲染結構"),
    
    // 搜尋引擎防禦層 (解除嚴格字元封鎖，改為寬鬆警戒線)
    seoTitle: z.string().max(120, "SEO 標題長度超載"),
    description: z.string().min(10).max(400, "Meta 描述長度超載，請精簡"),
    
    // 出版時間戳記 (導入 optional 解除強制綁定，容許「長青化」無日期資產存在)
    date: z.coerce.date().optional(),
    
    // 視覺證據 (強制綁定 VISION_ENGINE 產出的高畫質影像路徑)
    coverImage: image(),
    
    // 地理座標錨定：強制鎖定市場邊界
    targetGeo: z.string().default("Phnom Penh, Cambodia"),
    
    // 權威訊號矩陣：拒絕空泛，強制寫入實體數據
    authoritySignals: z.array(z.string()).min(1, "必須至少包含一項信任指標"),
    
    // 結構化資料微格式定義
    schemaType: z.enum(['Article', 'FAQPage', 'HowTo']).default('Article'),
    
    // 開發狀態切換
    draft: z.boolean().default(false),
  }),
});

export const collections = {
  'blog': blogCollection,
};
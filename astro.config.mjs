import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  // 網站身分證 (SEO 還是需要這行)
  site: 'https://ckmkh.com',
  
  // 只啟用 Tailwind，移除 sitemap()
  integrations: [
    tailwind()
  ],
});

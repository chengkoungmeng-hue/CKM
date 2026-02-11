import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  // ✅ 新增這行：這是網站的身分證，SEO 必備！
  site: 'https://ckmkh.com',
  
  integrations: [tailwind()],
});

import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
// import sitemap from "@astrojs/sitemap"; // ❌ 先暫時關掉這行

export default defineConfig({
  site: 'https://ckmkh.com',
  
  integrations: [
    tailwind(), 
    // sitemap() // ❌ 先暫時關掉這行
  ],
});

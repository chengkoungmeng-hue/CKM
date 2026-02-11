import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  // 網站身分證
  site: 'https://ckmkh.com',
  
  // 啟用 Tailwind 和 Sitemap
  integrations: [
    tailwind(), 
    sitemap()
  ],
});

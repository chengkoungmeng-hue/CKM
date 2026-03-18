import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  // 絕對網域錨點：強制綁定 www，從源頭消滅編譯期的重定向鏈
  site: 'https://www.ckmkh.com',
  
  // 整合矩陣：維持最高純淨度，僅保留 Tailwind 渲染引擎
  integrations: [
    tailwind()
  ],
});
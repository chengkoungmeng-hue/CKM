// 實體路徑: astro.config.mjs
// 狀態: 終極編譯封裝 4.2。消滅編譯期重定向，強制 CSS 內嵌以阻斷渲染延遲。
import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  // 絕對網域錨點：強制綁定 www，從源頭消滅編譯期的重定向鏈
  site: 'https://www.ckmkh.com',
  
  // 整合矩陣：維持最高純淨度，僅保留 Tailwind 渲染引擎
  integrations: [
    tailwind()
  ],

  // [極限參數] 強制將輕量 CSS 內嵌至 HTML，物理性消滅 300ms 網路握手與渲染阻塞
  build: {
    inlineStylesheets: 'always',
  },
});
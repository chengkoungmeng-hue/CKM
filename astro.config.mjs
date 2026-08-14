// @ts-nocheck
// 實體路徑: astro.config.mjs
// 狀態: 終極編譯封裝 4.3。消滅編譯期重定向，強制 CSS 內嵌以阻斷渲染延遲，突破 Vite 閾值。(Vite Reload with 13-item Safe East Asian Dataset)
import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // 這裡必須填寫沒有 www 的版本，以確保 Sitemap 和 Canonical 標籤正確無誤 (已修正為 ckmkh.com 以對齊 Canonical)
  site: 'https://ckmkh.com',
  
  // 整合矩陣：維持最高純淨度，僅保留 Tailwind 渲染引擎
  integrations: [
    tailwind(), 
    sitemap({
      // /pulse/pulse-NN/ is the legacy id route for an article that also lives at
      // /pulse/{slug}/. Both resolve, both canonicalise to the slug, and only the
      // slug belongs in the sitemap — otherwise 24 of 72 submitted URLs are
      // duplicates of the other 24.
      filter: (page) => !/\/pulse\/pulse-\d+\/$/.test(page),
    })
  ],

  // 強制統一目錄斜線結尾，避免 Cloudflare 301 重定向迴圈 (GSC Redirect error)
  trailingSlash: 'always',

  // No `redirects` block here. public/_redirects already 301s /zh and /en at the
  // Cloudflare edge — verified live: `curl -I https://ckmkh.com/zh` returns 301.
  // Declaring them here as well only emitted dist/zh/ and dist/en/ meta-refresh
  // stub pages that nothing ever serves.

  // 開啟 Prefetch 以達成零延遲換頁
  prefetch: true,

  // [極限參數] 強制將輕量 CSS 內嵌至 HTML，物理性消滅 300ms 網路握手與渲染阻塞
  build: {
    format: 'directory',
    inlineStylesheets: 'always',
  },

  // [系統注入] 突破 Vite 預設 4KB 限制，強制內嵌 10KB 以下的所有樣式與資源
  vite: {
    build: {
      assetsInlineLimit: 10240, 
    }
  }
});
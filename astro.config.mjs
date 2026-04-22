// @ts-nocheck
// 實體路徑: astro.config.mjs
// 狀態: 終極編譯封裝 4.3。消滅編譯期重定向，強制 CSS 內嵌以阻斷渲染延遲，突破 Vite 閾值。
import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

import sitemap from '@astrojs/sitemap';
import astroPwa from '@vite-pwa/astro';

export default defineConfig({
  // 絕對網域錨點：強制綁定 www，從源頭消滅編譯期的重定向鏈
  site: 'https://www.ckmkh.com',
  
  // 整合矩陣：維持最高純淨度，僅保留 Tailwind 渲染引擎
  integrations: [
    tailwind(), 
    sitemap(),
    astroPwa({
      registerType: 'autoUpdate',
      injectRegister: 'script',
      manifest: {
        name: 'CKM Catering',
        short_name: 'CKM',
        description: 'CKM Catering Premium Service',
        theme_color: '#0f172a',
        background_color: '#0f172a',
        display: 'standalone',
        icons: [
          {
            src: '/favicon.svg',
            sizes: '192x192 512x512',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,json,webp,jpg,jpeg}']
      }
    })
  ],

  // 開啟 Prefetch 以達成零延遲換頁
  prefetch: true,

  // [極限參數] 強制將輕量 CSS 內嵌至 HTML，物理性消滅 300ms 網路握手與渲染阻塞
  build: {
    inlineStylesheets: 'always',
  },

  // [系統注入] 突破 Vite 預設 4KB 限制，強制內嵌 10KB 以下的所有樣式與資源
  vite: {
    build: {
      assetsInlineLimit: 10240, 
    }
  }
});
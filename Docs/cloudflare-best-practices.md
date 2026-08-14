# Sunder: Cloudflare 最佳化防禦與效能配置指南 (Astro 專屬)

這份文件記錄了 Sunder 專案在 Cloudflare 上的「極致靜態最佳化 (Endgame Optimization)」設定。未來若有新的 Astro 專案（如 CKM 等），可直接參考此設定。

> **核心架構**：Sunder 為 Astro 靜態生成的網站，已由 Cloudflare Pages 直接託管。以下規則是為了將邊緣快取 (Edge Cache) 推向極致，使伺服器負載與載入延遲趨近於零。

## 1. 現代化快取規則 (Cache Rules)
Astro 編譯後的靜態資源（CSS、JS、圖片）皆附帶 Hash 雜湊值（例如 `index.a1b2c3d4.js`），因此**永遠不會發生快取衝突**，非常適合設定為永久快取。

在 Cloudflare 控制台 `Rules > Cache Rules` 中建立一條新規則：
- **名稱**: `Astro Static Assets Cache`
- **When incoming requests match...**: 
  - `URI Path` 包含 `/_astro/`
  - 或 `URI Path` 包含 `/assets/`
- **Cache status**: `Eligible for cache`
- **Edge TTL**: `Override origin` -> `1 year`
- **Browser TTL**: `Override origin` -> `1 year`

## 2. 全域基礎設定 (Zone Settings)
在 `Speed > Optimization > Content Optimization` 或透過 API 設定：
- **Auto Minify**: HTML `[ON]`, CSS `[ON]`, JS `[ON]` 
  *(作為 Astro 壓縮的第二道防線)*
- **Brotli**: `[ON]` 
  *(比傳統 Gzip 更好的壓縮比)*
- **Early Hints**: `[ON]` 
  *(提早暗示瀏覽器抓取核心 LCP 圖片)*

在 `Caching > Configuration`：
- **Browser Cache TTL**: `4 hours` 
  *(首頁等 HTML 網頁快取 4 小時，既兼顧效能又能保證發布新內容時能相對即時更新)*

## 3. 安全性設定 (Security)
- **Security Level**: `Medium` (中等)
- **Bot Fight Mode (機器人戰鬥模式)**: `[OFF]`
  *(因為是靜態網站，沒有後端資料庫負擔。關閉 BFM 可以避免拖慢真實訪客的 TTFB 速度，也能確保 SEO 爬蟲暢通無阻)*
- **WAF Custom Rules**: `維持淨空`
  *(沒有特定惡意攻擊或防盜連需求時，不需增加無謂的檢查點)*

## 4. API 執行腳本 (備忘)
若未來需要透過 API 自動套用，可使用 Python 或 PowerShell 呼叫 Cloudflare API。
⚠️ **注意**：絕不可將帶有 `Token` 的腳本提交到 Git。請將 Token 存放於 `.env` 中，並確保 `.gitignore` 內包含 `.env`。

*(本文件已於 2026-06-12 建立，確立了 Sunder 頂級效能架構)*

# devops/ — 本專案的維運工具

本目錄是 ckmkh.com **唯一**的工具存放處。2026-08-20 由 `scripts/` 更名而來,
所有 workflow、`package.json`、`.agents/AGENTS.md` 與 `Docs/` 的引用已在同一次
變更內一併更新。

CI 一律從 repo 根目錄(`$GITHUB_WORKSPACE`)呼叫這些工具,沒有任何 step 設定
`working-directory`。因此腳本內以 CWD 為基準的相對路徑(`src/data/pulseData.json`、
`public/images/pulse` 等)在更名後行為不變;以 `__file__` / `__dirname` 為基準的
路徑同樣不受影響。

## 工具清單

### CI 排程執行

| 檔案 | 用途 | 呼叫方式 |
| :--- | :--- | :--- |
| `check_content.py` | 內容閘門:高棉文字元完整性、`seoTitle` / `description` 渲染寬度預算、內鏈下限、開頭語重複上限、密鑰樣式掃描。無外部相依,全樹掃描一秒內完成 | workflow `Content gate`(push / PR 觸及 `src/content/**`、`src/data/**`、`public/llms*.txt`、`devops/check_content.py` 時)與 `Daily Catering Pulse & Auto-Indexing Pipeline`,兩者皆執行 `python devops/check_content.py --strict` |
| `fetch_catering_pulse.py` | 每日 RSS 擷取、Gemini 高棉文改寫、封面圖下載與壓縮,寫入 `src/data/pulseData.json` | workflow `Daily Catering Pulse & Auto-Indexing Pipeline`,cron `47 20 * * *` 與 `47 8 * * *`:`python devops/fetch_catering_pulse.py` |
| `generate_llms_txt.py` | 由站內既有內容產生 `public/llms.txt` 與 `public/llms-full.txt`;`--check` 於檔案過期時非零退出 | 同上 workflow:`python devops/generate_llms_txt.py` |
| `check_pulse_health.py` | 停擺偵測器。不逐一檢查各種失敗成因,而是量測「資料集最新一筆有多舊」,涵蓋所有已知與未知的靜默失敗路徑 | 同上 workflow(`if: always()`,在 commit 步驟之後):`python devops/check_pulse_health.py --max-age-days 2` |
| `notify_indexing.py` | Cloudflare 邊緣快取清除、IndexNow 提交、Search Console sitemap 重送;可由 git diff 推導受影響 URL | workflow `Publish`(push / `workflow_run` / 手動):`python devops/notify_indexing.py --urls …` 或 `--changed` |
| `gsc_query_report.py` | 拉取 Search Console 即時搜尋數據。無任何 fallback 值,API 失敗即非零退出;原始輸出寫入 `devops/reports/gsc_search_queries.json` | workflow `Search Report`,cron `0 6 * * 1`:`python devops/gsc_query_report.py --days "$days"` |

`Verify Credentials`(cron `0 19 * * 0`)以 inline 指令驗證三組憑證,不呼叫本目錄任何檔案;
其註解引用了 `devops/fetch_catering_pulse.py` 的 `MODEL_LADDER`。

### npm 執行

| 檔案 | 用途 | 呼叫方式 |
| :--- | :--- | :--- |
| `run_content_check.mjs` | `check_content.py --strict` 的 npm 端執行器。依序試 `python3` / `python` / `py`,找不到直譯器時明確失敗而非跳過檢查 | `npm run check`;`npm run build` 串接為 `npm run check && astro check && astro build` |

### 手動執行

| 檔案 | 用途 | 呼叫方式 |
| :--- | :--- | :--- |
| `apply_internal_links.py` | 依 `src/data/internalLinks.json` 的宣告表,把文章內既有的精確錨點字串包成內鏈。冪等,錨點非唯一或位於標題 / 表格 / 既有連結內時拒絕寫入 | `python devops/apply_internal_links.py` 套用,`--check` 僅驗證 |
| `fix_section_order.py` | 把 `## សេចក្តីសន្និដ្ឋាន`(結論)搬到 `## សំណួរដែលសួរញឹកញាប់`(FAQ)之後。純區塊搬移,寫入前驗證檔案行的多重集合不變 | `python devops/fix_section_order.py --check` 僅報告,不加參數則改寫 |
| `build_width_table.cjs` | 在真實瀏覽器量測每個 codepoint 的 advance width,產生 `devops/reports/khmer_width_table.json`,供更新 `check_content.py` 內嵌的寬度表 | `node devops/build_width_table.cjs`(需 playwright) |
| `verify_a11y.cjs` | 以行程內 http server 服務 `dist/`,在真實瀏覽器驗證無障礙修正,截圖存 `devops/reports/skip_link.png` | 先 build,再 `node devops/verify_a11y.cjs` |
| `playwright_audit.js` | 20 條路由 × 3 種視窗的 SEO / UX / UI 稽核,輸出 `devops/reports/audit_summary.json` | 先啟動本機站台(`http://localhost:4321`),再 `node devops/playwright_audit.js` |
| `astro_full_browser_audit.js` | 10 條代表性路由 × 3 種視窗的瀏覽器全面稽核(含 JSON-LD 檢查),輸出 `devops/reports/astro_full_browser_audit_results.json` | 同上,`node devops/astro_full_browser_audit.js` |
| `cloudflare_audit.js` | 讀取 Cloudflare zone 的 WAF / Cache / Speed 即時設定,輸出 `devops/reports/cloudflare_audit_summary.json`。唯讀 | `node devops/cloudflare_audit.js`(需 `CLOUDFLARE_API_TOKEN`,或 `.env`) |
| `apply_cf_settings.py` | 以 Cloudflare API 套用 zone 設定與三個 ruleset phase | 視為意圖紀錄,**不建議執行**:每個 `put_ruleset_phase()` 都是 `PUT` 整組取代,會清掉自上次編輯後在 dashboard 新增的規則(見 `.agents/AGENTS.md` §16 [REGRESSION]) |
| `scan_seo_issues.py` | 掃描 `src/` 找缺 `alt` 的圖片與 meta description 問題 | `python devops/scan_seo_issues.py`。內含硬編碼絕對路徑 `C:\Projects\CKM\src`,換機器需先改 |
| `compress_images.py` | 把 `public/images` 內的 blog inline PNG 轉為 WebP 並同步更新 markdown 引用 | `python devops/compress_images.py`(需 Pillow) |
| `migrate_pulse_images.py` | 一次性遷移:把舊 `pulse-XX` 圖檔改名為 slug 命名、補 `image_alt`、重抓缺圖 | `python devops/migrate_pulse_images.py`(需 Pillow) |
| `fix_h1_tags.py` | 移除 blog markdown 內文的第一個 H1 | 一次性腳本。內含硬編碼絕對路徑 `c:\Projects\CKM\src\content\blog`,換機器需先改 |

## 版控規則:哪些追蹤、哪些忽略

- **`devops/` 底下的工具一律由 git 追蹤,絕不整包加進 `.gitignore`。** CI 是從
  checkout 出來的樹直接呼叫它們的;工具一旦沒進版控,排程流程會在無人察覺的情況下停止。
- `.gitignore` 只忽略兩個子目錄:

  ```gitignore
  devops/local/
  devops/reports/
  ```

- `devops/local/` — 一次性、不可重複執行的本機腳本。目前放三個已退役的 pulse
  資料 seeder(`populate_rich_khmer_pulse_content.py`、`reseed_100pct_real_urls.py`、
  `seed_12_gourmet_pulse.py`),更名前即已被 `.gitignore` 逐檔忽略。
- `devops/reports/` — 工具產生的輸出(稽核 JSON、GSC 原始資料、寬度表、截圖)。
  這些檔案由工具重新產生,不需要人工維護。
  註:`astro_full_browser_audit_results.json`、`audit_summary.json`、
  `cloudflare_audit_summary.json` 三個檔案在更名前已被追蹤,以 `git mv` 搬入本目錄後
  仍在 index 中(`.gitignore` 不影響已追蹤檔案)。若要讓它們比照其他報告不再進版控,
  需另外執行 `git rm --cached`。
- 更廣泛的一次性探索工具留在 repo 根目錄的 `scratch/`,該目錄整包被忽略,不在本次搬移範圍內。

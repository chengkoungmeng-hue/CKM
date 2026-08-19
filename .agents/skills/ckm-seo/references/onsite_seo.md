# CKM SEO(ckmkh.com,高棉文婚宴/宴席)

Astro 靜態站 + Cloudflare Pages。SEO 規則的唯一真本在 `.agents/AGENTS.md`;本 skill 依
§0 Skills policy(2026-08-20 修訂)只放執行層,不復述規則,衝突時以 AGENTS.md 為準。
本檔只做工具索引與規則路由。

## 工具鏈(位於 `devops/`,CI 會跑,必須保持追蹤)

| 工具 | 作用 |
| :--- | :--- |
| `check_content.py --strict` | **阻斷式內容閘門**:標題/描述寬度預算、連結、語言純度等。`npm run build` 與 `content_gate.yml` 都跑它 |
| `generate_llms_txt.py` | 依實際站內容重建 `public/llms.txt` 與 `llms-full.txt`(曾漂移到零覆蓋) |
| `notify_indexing.py` | Cloudflare 清快取 + IndexNow + GSC 提交 |
| `gsc_query_report.py` | 拉 GSC 搜尋分析。**API 失敗即非零退出,不產生合成資料** |
| `apply_internal_links.py` | 依 `src/data/internalLinks.json` **宣告表**注入內鏈 |
| `scan_seo_issues.py` | 掃 `src/` 的 alt text 缺失與 meta description 問題 |
| `check_pulse_health.py` | pulse 資料集停滯偵測(每日 cron 內建) |

## 動工前先讀的規則(本體皆在 AGENTS.md,此處僅路由)

- 語言範圍(高棉文 only、`/zh/` 與 `/en/` 301):規則本體見 AGENTS.md §2。
- canonical、trailingSlash 與 [REGRESSION] pulse slug 路由:規則本體見 AGENTS.md §3。
- 內鏈宣告表與 [REGRESSION] 內鏈規則(嚴禁關鍵字 regex):規則本體見 AGENTS.md §14。
- 外鏈計畫已停,不要重啟:規則本體見 AGENTS.md §19。

## 站外(社群)

Facebook 粉絲團 + 社團,高棉文圖文三件套,零連結。見 AGENTS.md §21 與本 skill 的
[facebook_playbook.md](facebook_playbook.md)。本地服務型商家若尚未建立
**Google Business Profile**,那是本專案 CP 值最高的一次性 SEO 投資(婚宴是強在地意圖)。

## 量測

每週 `search_report.yml`(cron)自動拉 GSC;高曝光低 CTR 的高棉文查詢是改標題與寫新文的題材來源。

# CKM SEO(ckmkh.com,高棉文婚宴/宴席)

Astro 靜態站 + Cloudflare Pages。**站上只有高棉文**——`baseLang` 硬編碼為 `km`,
`/zh/` 與 `/en/` 一律 301。嚴禁產生或連結到中英文路由。

**本專案禁止建立專案級 skills**(AGENTS.md §0),SEO 規則的真本在 `.agents/AGENTS.md`
(§2 語言範圍、§3 canonical、§18 搜尋需求、§19 外鏈已停)。本檔只做工具索引與提醒。

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

## 不可退讓

1. **canonical 嚴格 `https://ckmkh.com`**,永不 `www.`、永不 `http://`;`trailingSlash: 'always'`,
   內部連結不以 `/` 結尾就會吃 301,權重花在轉址上。
2. **[REGRESSION] pulse 頁只能有描述性 slug 路由**。同時輸出 `/pulse/[slug]/` 與 `/pulse/[id]/`
   會讓 GSC 報「重複內容,Google 選了不同的正規網址」。
3. **內鏈用宣告表,永遠不要改回關鍵字 regex**——那正是本專案記錄下 Sunder 弄壞 130 處的做法。
4. 外鏈計畫已於 §19 停止,不要重啟。

## 站外(社群)

Facebook 粉絲團 + 社團,高棉文圖文三件套,零連結。見 AGENTS.md §21 與
`community-content-engine` 的 `ckm_facebook.md`。本地服務型商家若尚未建立
**Google Business Profile**,那是本專案 CP 值最高的一次性 SEO 投資(婚宴是強在地意圖)。

## 量測

每週 `search_report.yml`(cron)自動拉 GSC;高曝光低 CTR 的高棉文查詢是改標題與寫新文的題材來源。

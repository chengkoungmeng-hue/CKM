# CKM 優化 Brief

寫於 2026-08-15。給接手這個專案的 AI session 或人。

先讀 `.agents/AGENTS.md`——那是這個專案的最高指導原則，600 行，所有 skill 已整併進去。
本文件只補充該檔案沒有涵蓋的、待處理的項目。

---

## 專案現況

Astro 靜態站，`ckmkh.com`，高棉語。Cheng Koung Meng（хаang 承光明）——柬埔寨金邊的
高棉─中式宴席外燴。

```
src/content/blog/*.md        15 篇  常青文章
src/data/pulseData.json      27 筆  每日自動產出的美食動態
```

自動化每天 20:47 UTC 執行：

```
Daily Catering Pulse  抓 RSS → Gemini 譯寫高棉語 → check_content.py --strict → commit
        ↓ workflow_run
Publish               輪詢新頁面直到 200 → 清 Cloudflare 快取 → IndexNow + GSC
```

手動寫的文章 push 上去會走同一條 `publish.yml`，行為一致。

---

## 已完成（2026-08-15，勿重複處理）

- **Secret 改名**：`SEARCH_CONSOLE_SA_JSON` / `ANALYTICS_SA_JSON` / `GEMINI_API_KEY` /
  `CLOUDFLARE_API_TOKEN`，與 Sunder 完全同名，workflow 可互相複製
- **`publish.yml` 拆出**：先前索引只在 pulse job 內執行，手寫文章不會被提交
- **過濾器誤判修正**：`EXCLUDE_REGEX` 的 `pancakes` / `sandwich` 誤傷蔥油餅與港式三文治，
  新增窄範圍的 `ALLOW_REGEX`
- **排序修正**：先前依 `pub_date`（來源部落格發布日）排序，今天的文章因為來源是二月的食譜
  而排在第 26/27 筆、第 3 頁。新增 `added_at` 並依它排序，schema 的 `datePublished` 同步改用
- **型別錯誤**：`astro check` 從 6 errors 降到 0
- **GA4 權限收斂**：帳戶層移除，只保留資源層檢視者

---

## 待處理

### 1. 內容產量偏薄（優先）

程式碼自己量測的有效產量是 **42.2 篇/月**，而每日一篇需要 30 篇/月——餘裕只有 40%。
2026-08-14 那天所有候選都被過濾掉，整天沒有產出。

解法是**增加中文來源**，不是放寬 `EXCLUDE_REGEX`。那些排除規則存在的原因寫在
`devops/fetch_catering_pulse.py` 的註解裡：先前的來源組合在高棉─中式宴席品牌底下
產出了 Palm Springs 椰棗奶昔和波蘭奶油蛋糕。

現有 5 個來源與各自產量記錄在同一個檔案的註解中。

### 2. 缺少內部連結注入

Sunder 有 `scratch/apply_internal_links.cjs`，會在文章中自動插入指向支柱文章的連結。
CKM 沒有對應機制，15 篇 blog 與 27 篇 pulse 之間的連結全靠 `[id].astro` 的相關文章區塊。

移植前注意：Sunder 那支腳本原本有 bug——它把 `（TCO）` 整個換成 ` [TCO](…)`，
吃掉括號又補上一個中文不需要的空格，造成 53 個檔案 130 處語法損壞。修正版保留括號、
只把關鍵字變成連結。**移植的是修正後的版本。**

高棉語沒有詞間空格，直接套用中文的規則會出問題，需要重新設計匹配方式。

### 3. 缺少 llms.txt 自動生成

`public/llms.txt` 與 `llms-full.txt` 存在但沒有生成腳本，內容會逐漸與實際文章脫節。
Sunder 有 `scratch/generate_llms_txt.cjs` 可參考。

### 4. On-page SEO

15 篇 blog 的 frontmatter 已經有 `title` / `seoTitle` / `description` /
`target_keyword` / `authoritySignals` / `targetGeo`——結構比 Sunder 完整。
尚未檢查的是這些欄位的**實際內容品質**：

- `seoTitle` 是否在 SERP 顯示長度內
- `description` 是否寫給人看，而不是關鍵字堆疊
- 是否有多篇共用同一個開頭句式（Sunder 有 12/42 篇以「深度解析五星…」開頭的問題）

pulse 的 27 筆是機器譯寫，語氣一致性值得抽查。

### 5. UI / UX

沒有系統性檢視過。`astro check` 目前 0 errors，但 Lighthouse、Core Web Vitals、
行動裝置實測、鍵盤導航、對比度都沒量過。

---

## 操作限制

remote 走 SSH：`git@github.com-chengkoungmeng:chengkoungmeng-hue/CKM.git`
`gh` 已登入 `chengkoungmeng-hue`，可直接讀 Actions log。

**push 到 `main` 會觸發 `publish.yml`**——等頁面上線、清快取、提交 IndexNow 與 GSC。
每次 push 都是真的發布。

`verify_credentials.yml` 有四個 job（Search Console / Gemini / Cloudflare / Analytics），
手動觸發，全部唯讀或冪等。**注意 Cloudflare 那個 job 會實際清一次整個 zone 的快取**，
不要在流量高峰隨手跑。

### 驗證

```bash
npx astro check      # 必須 0 errors
npx astro build      # 必須成功，約 80 頁
python devops/check_content.py --strict
```

---

## 建議順序

產量問題最急——它決定每天有沒有東西可發。內部連結與 llms.txt 是既有能力的補齊。
On-page SEO 與 UI/UX 可以並行，但都建議先做 3-5 個樣本給使用者確認方向。

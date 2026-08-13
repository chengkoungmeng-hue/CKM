---
name: ckm_backlink_writer
description: 適用於 ckmkh.com 的 Medium、Substack 與 Blogger 外鏈推廣文章撰寫規格，包含主題標籤 (Topics), 描述、標準網址設定、HTML 輸出格式、圖片 Alt text 與 Downloads 複製自動化，以及外鏈帳本 (Ledger) 紀錄規範。
---

# CKM 外鏈推廣文章撰寫與發佈指引 (Medium, Substack & Blogger)

本指引旨在規範如何為 ckmkh.com 撰寫與發佈發送至外部平台（如 Medium、Substack、Blogger）的推廣外鏈（Backlink）文章。所有產出的文章必須一次性完整輸出對應平台所需的所有規格項目，以利極速發佈、避免重複內容，並最大化搜尋引擎收錄權益。

---

## 1. 輸出格式與操作規範 (Output Format & Operating Rules)

- **雙重格式輸出 (HTML & Markdown)**：對於 Blogger 等外部發佈平台，為了防止讀者直接從 Markdown 複製貼上造成樣式殘留或產生黑色背景塊（CSS Artifacts），**必須同時提供 HTML 乾淨原始碼版本與 Markdown 版本**。
- **圖片自動下載與複製 (Downloads Automation)**：生成推廣文章所需的封面或插圖時，必須將生成的 JPG/PNG 圖片使用 PowerShell 腳本**自動複製到使用者的 `Downloads` 資料夾**，並在回覆中附上圖片的下載連結與對應的高棉語 Alt Text。

---

## 2. 完整發佈規格

### 2.1 Medium 發佈規格

每篇產出的 Medium 外鏈文章，必須包含以下 6 項標準規格：

- **文章標題 (Title)**：100% 柬埔寨高棉語 (`km-KH`)，包含品牌關鍵字與地理區域。
- **文章描述 (Description / Subtitle)**：100% 柬埔寨高棉語，**嚴格限制在 100 至 140 字元之間**（Medium 上限為 150 字元）。
- **文章內容 (Body Content)**：至少 600 - 1000 字（以高棉語計），嵌入 1 到 2 個指向官網 `https://ckmkh.com` 的錨文字（例如 `[សេវាកម្មធ្វើម្ហូប CKM](https://ckmkh.com)`）。
- **圖片替代文字 (Alt Text)**：100% 柬埔寨高棉語，描述圖片內容並融入關鍵字。
- **主題標籤 (Topics / Tags)**：**僅限英文**。固定推薦 5 個標籤（例如 `Catering`, `Cambodia`, `Event Planning`, `Weddings`, `Phnom Penh`）。
- **標準網址 (Canonical URL)**：指向 **`https://ckmkh.com`**（嚴禁 `www.`）。設定路徑：`Settings` -> `Advanced Settings` -> 勾選 `This story was originally published elsewhere` 並填入網址。

### 2.2 Substack 發佈規格

每篇產出的 Substack 外鏈文章，必須包含以下 6 項標準規格：

- **文章標題 (Title)**：100% 柬埔寨高棉語 (`km-KH`)，建議在 60 字元以內以利 SEO 顯示。
- **副標題 (Subtitle)**：100% 柬埔寨高棉語，**限制在 100 至 140 字元之間**，用於電子報發送摘要。
- **文章內容 (Body Content)**：與 Medium 相同，嵌入 1 到 2 個指向 `https://ckmkh.com` 的高棉語錨文字連結。
- **圖片替代文字 (Alt Text)**：100% 柬埔寨高棉語。Substack 編輯器中上傳圖片後點選圖片設定可輸入 Alt text。
- **SEO 設定 (SEO Settings)**：
  - **SEO Title**：不超過 60 字元的高棉語標題。
  - **SEO Description**：限制在 140 字元內的高棉語摘要。
- **標準網址 (Canonical URL)**：指向 **`https://ckmkh.com`**。設定路徑：在 Post Settings 面板 -> 點擊 `SEO Options` -> 填入 `Custom Canonical URL`。

### 2.3 Blogger 發佈規格

每篇產出的 Blogger 外鏈文章，必須包含以下 6 項標準規格：

- **文章標題 (Title)**：100% 柬埔寨高棉語 (`km-KH`)，融入核心關鍵字。
- **搜尋說明 (Search Description)**：100% 柬埔寨高棉語，**限制在 100 至 140 字元之間**（Blogger 字數上限為 150 字元，需於右側面板 `Search Description` 欄位填入）。
- **文章內容 (Body Content)**：與 Medium/Substack 相同，嵌入 1 到 2 個指向 `https://ckmkh.com` 的高棉語錨文字連結。
- **自訂永久連結 (Custom Permalink)**：**僅限英文/拼音**，以底線或連字號分隔（例如 `wedding-menu-planning-phnom-penh`）。在發佈面板 -> `Permalink` -> 選擇 `Custom Permalink` 填入，避免 Blogger 自動生成亂碼或過長的網址。
- **標籤 (Labels / Tags)**：支援高棉語與英文。固定推薦 3-5 個標籤（例如 `Catering`, `សេវាកម្មធ្វើម្ហូប`, `ភ្នំពេញ`），直接在發佈面板 `Labels` 填入。
- **圖片 Alt 屬性**：上傳圖片後，在 HTML 檢視或點選圖片設定，輸入 `alt` 屬性與 `title` 屬性，確保搜尋引擎能索引圖片。

---

## 3. 外鏈帳本 (Backlinks Ledger) 紀錄流程

為了避免重複發佈相同主題的文章或造成重複內容（Duplicate Content），所有 AI Agent 在撰寫或計畫產出外鏈文章時，必須遵循以下流程：

1. **檢查帳本**：在撰寫新文章前，必須優先讀取位於 `Docs/backlink_ledger.md` 的外鏈發佈紀錄。
2. **避免重複**：確認新文章的目標關鍵字、標題或切入角度，未與已存在的紀錄重複。
3. **登記新文章**：一旦生成新的外鏈文章，必須立即在 `Docs/backlink_ledger.md` 中新增一筆紀錄，填入編號、發佈日期、平台、標題、目標關鍵字、標準網址和發佈狀態。

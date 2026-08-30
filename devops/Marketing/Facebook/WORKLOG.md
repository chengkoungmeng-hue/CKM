# CKM Facebook Marketing Worklog

記錄 CKM 在 Facebook 平台的發布歷史、排程進度、各階段里程碑與操作日誌。

---

## 📅 工作排程與進度一覽

| 日期 | 行動項目 | 狀態 | 核心成果 / 備註 |
| :--- | :--- | :--- | :--- |
| **2026-08-22** | 平台標準化四件套建立 (SKILL / ledger / WORKLOG / ASSET_SPEC) | ✅ 已完成 | 納入 Central DevOps 獨立中樞 |
| **2026-08-24** | **戰略轉型與獨立專頁正式建立 ＆ 首篇美食洞察發布** | ✅ **已完成** | 1. 定名 `រសជាតិ និងសិល្បៈធ្វើម្ហូប - Taste & Culinary Arts`<br>2. 確立「純淨美食媒體智庫 ➔ 官網 ckmkh.com 轉化」架構<br>3. 成功上傳黑金名廚大頭貼與奢華長桌封面<br>4. 實裝高棉文 Unicode 白名單、錯字與防過度承諾檢驗閘門<br>5. **成功首發第 1 篇金黃蒜香油高湯洞察圖文 (`post-001`)**，100% 零貼文外鏈 |
| **2026-08-25+** | 進入常態 Pulse 每日圖文營運 | ⏳ 進行中 | 維持每天 1 篇高質感美食洞察圖文，以大眾智庫模式高速累積金邊在地 Follower |

---

## 📝 執行工作日誌 (SOP)

1. **動工前 (Pre-flight Check)**：
   - 讀取本目錄 [`SKILL.md`](SKILL.md) 檢查高棉文四大憲政紅線與尊榮稱謂。
   - 讀取 [`ledger.json`](ledger.json) 確保主題與菜色不與過往重複。
2. **產出素材與文案（極速一分鐘發布）**：
   - Agent 直接調用工具生成 1:1 奢華美食實拍圖，自動輸出至 `Downloads/`（無文字、無水印）。
   - 撰寫 200~350 字元 100% 純高棉文案（食材秘訣 + 火候 + 0 外鏈 + 0 促銷廢話）。
   - 執行 `python Tools/content_gate.py --project CKM --platform Facebook --file draft.txt` 通過機械檢查。
3. **發布後回寫 (Post-publish Log)**：
   - 發布後將貼文 ID、URL 與數據回寫至 `ledger.json`。

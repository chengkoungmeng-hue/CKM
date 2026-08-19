# CKM — Agent Entry Point

**開始工作前,先完整讀取 [`.agents/AGENTS.md`](.agents/AGENTS.md)。** 那是本專案規則的唯一真本
(涵蓋高棉文完整性、機密處理、Pulse 管線、實測搜尋需求與品牌語調)。

## 規則層級

1. `~/.codex/AGENTS.md` — 跨專案母法(真本在 `~/.agents/GLOBAL.md`)。
2. `.agents/AGENTS.md` — 本專案規則,**覆蓋母法**。
3. 對話中的明確指示覆蓋以上全部。

## 進場提醒

- 規則描述的是程式碼**現在實際的行為**,不是理想狀態。改動行為時,在同一個 commit 內更新規則。
- 標記 `[REGRESSION]` 的規則對應真實上線過的缺陷,不要簡化掉。
- 提交內容前執行 `python devops/check_content.py`。`npm run build` 會以 `--strict` 再跑一次,
  CI 的 `.github/workflows/content_gate.yml` 才是真正的閘門(Cloudflare Pages 在 merge 之後才建置)。
- 專案 skill 只有一個:`.agents/skills/ckm-seo/`(僅放執行層,不復述規則;衝突時以
  `.agents/AGENTS.md` 為準)。邊界政策見 `.agents/AGENTS.md` §0,未依該政策記錄前勿另建 skills。

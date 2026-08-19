# CKM — Agent Entry Point

專案規則的唯一真本是 [`.agents/AGENTS.md`](.agents/AGENTS.md)。下一行會自動 import 它;
若未生效,開始工作前先自行讀取該檔。

@.agents/AGENTS.md

## 規則層級

1. `~/.agents/GLOBAL.md` — 跨專案母法,由各工具的全域設定自動載入。
2. `.agents/AGENTS.md` — 本專案規則,**覆蓋母法**。
3. 對話中的明確指示覆蓋以上全部。

## 進場提醒

- 規則描述的是程式碼**現在實際的行為**,不是理想狀態。改動行為時,在同一個 commit 內更新規則。
- 標記 `[REGRESSION]` 的規則對應真實上線過的缺陷,不要簡化掉。
- 提交內容前執行 `python devops/check_content.py`。`npm run build` 會以 `--strict` 再跑一次,
  CI 的 `.github/workflows/content_gate.yml` 才是真正的閘門(Cloudflare Pages 在 merge 之後才建置)。
- 專案 skill 只有一個:`.agents/skills/ckm-seo/`(僅放執行層,不復述規則;衝突時以
  `.agents/AGENTS.md` 為準)。邊界政策見 `.agents/AGENTS.md` §0,未依該政策記錄前勿另建 skills。

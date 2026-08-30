# CKM

ckmkh.com 的網站原始碼。Astro 靜態站,部署於 Cloudflare Pages;維運與資料管道工具在 `devops/`。

## Prerequisites

- **Node.js** — 專案未宣告版本:`package.json` 沒有 `engines` 欄位,repo 沒有 `.nvmrc`,
  workflow 也沒有任何 `actions/setup-node` 步驟(CI 用 runner 預設)。開發機實測 v24.13.1 可用。
- **npm** — `.npmrc` 只有一行 `legacy-peer-deps=true`;安裝相依時會沿用,不要覆寫。
- **Python 3** — `devops/` 的腳本與內容閘門 `devops/check_content.py` 需要。CI 一律指定 3.11
  (`.github/workflows/*.yml` 的 `python-version`),開發機實測 3.12.10 可用。專案沒有
  `requirements.txt`:各 workflow 自行 `pip install`(`requests`、`google-auth`、`Pillow`),
  而 `check_content.py` 本身刻意零外部相依。

## Setup

```bash
npm install
npm run dev
```

憑證放在 `devops/.env` —— **不是根目錄**,本專案沒有根目錄 `.env`。該檔已被 `.gitignore` 排除,
永不進 git。目前存放的鍵:`CLOUDFLARE_ACCOUNT_ID`、`CLOUDFLARE_ZONE_ID`、
`CLOUDFLARE_API_TOKEN`、`GOOGLE_SERVICE_ACCOUNT_KEY`。

CI 使用的憑證另存於 GitHub Actions secrets,寫入後無法讀回。憑證的讀取、遮蔽與存放規則見
`.agents/AGENTS.md` 第 16 節。

## Everyday commands

| 指令 | 作用 |
| :--- | :--- |
| `npm run dev`(= `npm start`) | 啟動 Astro 開發伺服器 |
| `npm run check` | 執行 `devops/run_content_check.mjs`,即內容閘門 `check_content.py --strict` |
| `npm run build` | `npm run check && astro check && astro build` —— 本機與任何有 Python 3 的環境用這個 |
| `npm run build:deploy` | `astro check && astro build`,不含內容閘門(見下) |
| `npm run preview` | 預覽 `dist/` 建置產物 |
| `npm run astro` | 直接呼叫 astro CLI |

### `build:deploy` 為什麼存在 —— 不要當成多餘的後門刪掉

`npm run build` 的第一步 `npm run check` 需要 Python 3。`devops/run_content_check.mjs` 依序
嘗試 `python3` / `python` / `py`,一個都找不到時**明確失敗**而不是跳過檢查。因此在沒有 Python 3
的建置環境(例如缺 Python 的 Cloudflare Pages 映像)裡,`npm run build` 必定紅燈。
`build:deploy` 就是給這種環境的替代入口。

它不是繞過閘門的手段:內容在進 main 之前已由 `.github/workflows/content_gate.yml` 跑過同一支
`check_content.py --strict`,所以 `build:deploy` 略過的是一個已經跑完的檢查。同樣的理由也記在
`package.json` 的 `//build:deploy` 註解欄位裡。本機開發一律用 `npm run build`。

## Layout

| 目錄 | 職責 |
| :--- | :--- |
| `src/` | 網站本體:`pages/`(路由,含 `blog/` 與 `pulse/`)、`layouts/`、`components/`、`content/blog/`(15 篇 Markdown 文章)、`data/`(`pulseData.json`、`internalLinks.json` 等資料檔)、`assets/`(建置期處理的圖片) |
| `public/` | 原樣輸出的靜態檔:`robots.txt`、`llms.txt` / `llms-full.txt`、favicon 與 icon、`images/`、`fonts/`,以及 Cloudflare Pages 讀取的 `_headers` 與 `_redirects` |
| `devops/` | 維運與資料管道工具(以 Python 為主):內容閘門、每日 pulse 抓取、Search Console 報表、Cloudflare 設定、圖片壓縮。逐支說明見 `devops/README.md` |
| `Docs/` | 專案文件:Cloudflare 最佳實務、安全基準、最佳化簡報、`Architecture/Worklogs/` |
| `.agents/` | AI agent 的專案規則(`AGENTS.md`);根目錄 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` 指向它 |
| `.github/workflows/` | CI:內容閘門、每日 pulse 管道、發布與索引通知、GSC 報表、憑證驗證 |

## Documentation

- [Cloudflare Optimization Best Practices](./Docs/cloudflare-best-practices.md)

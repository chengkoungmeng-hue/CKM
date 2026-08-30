# Pulse Module — CKM

本專案（CKM）的市場脈動、情報收集與痛點採礦。

## 管線組成

| 檔案 | 角色 | 排程 |
| :--- | :--- | :--- |
| `collect.py` | 撈原始資料 | CKM 有 `daily_catering_pulse.yml` |
| `ckm_material.py` | 整理成當日素材 JSON | 同上 |
| `ckm_pdf_generator.py` | 把素材排版成給人讀的 PDF | **刻意不排程** |
| `report_paths.py` | 共用輸出路徑 → `Downloads/CKM-report/` | — |

## PDF 產生器為什麼留著卻不排程(2026-08-30 決定)

它產出的是**給擁有者自己讀的內部簡報**,不是網站內容——`public/` 與 `src/`
底下沒有任何 PDF,它不會出現在 CKM 的網站上。

保留但不排程的理由:

- **它與查重完全無關。** 發布查重的唯一真本是
  `devops/Marketing/<平台>/ledger.json`,來源查重在各專案的 `*_sent.txt`。
  `Marketing/` 底下零個檔案提到 pdf。**刪掉或停用 PDF 不會影響任何去重機制**
  ——`report_paths.py` 的檔頭本來就寫著「即使 Downloads 內的報告被刪除,
  查重防重依然 100% 準確運作」。
- **實務上沒有在用。** 2026-08-30 檢查時,四個 `Downloads/*-report/` 資料夾
  全部是空的,這條管線先前並未產出任何 PDF。
- **成本是零。** 它現在能跑、不佔 CI、不進網站。留著等於保留一個隨時可用的選項。

要發社群貼文時,直接讀 `ckm_material.py` 產出的素材 JSON 即可,
不必經過 PDF 這一層。

**TWProbe 的日報是另一條路徑**(`devops/Scrape/daily_market_and_painpoints_collector.py`,
`npm run brief`),與本目錄無關,且刻意保留——它是撰寫 Threads、部落格與
發想新功能的素材來源。

## 已知的失敗模式(2026-08-30 修復)

`ckm_pdf_generator.py` 的圖檔目錄原本指向已刪除的 `C:\Projects\DevOps` hub。
`os.path.exists()` 一律回 False,於是**每張卡片都靜默少掉圖片,產出一份看起來正常、
只是沒有圖的 PDF**。一份無圖簡報和一份有圖的,在結束碼上完全一樣。

現在目錄不存在時直接非零離開,不產出半成品。改動任何路徑之後,
**要實跑一次並數 PDF 裡的內嵌影像數**,不要只跑 `py_compile`
——語法檢查不會發現名稱解析錯誤,也不會發現圖片沒進去。

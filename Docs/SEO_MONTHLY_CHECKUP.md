# CKM 每季 SEO 體檢與維護

建立於 2026-10-08。規則真本仍是 `.agents/AGENTS.md`;本文件只放**程序**與**台帳**,
不復述規則。衝突時以 AGENTS.md 為準。

**節奏自 2026-11-14 起由每月改為每季(owner 決定)**,檔名保留以免改動既有引用。
兩次體檢之間唯一的警報是每週的 `Search Report` 與 `Verify Credentials` 兩個 workflow,
所以它們必須維持「綠燈 = 正常、紅燈 = 有事」:2026-11 發現後者已連續紅了三週而沒人處理(§4b)。
每季另加一步依賴更新(§2.8)。

## 0. 這份體檢在量什麼

AGENTS.md §18 已經量出這個市場的天花板:柬埔寨境內的高棉文商業搜尋量大約每月 100 次曝光,
排名已在 3 至 6 名。所以體檢**不是為了成長**,而是為了三件事:

1. **偵測退化**:索引被污染、路由 404、標題被截斷、憑證失效、workflow 停擺。
2. **確認既有判斷仍成立**:`ចុងភៅ` 仍是零點擊、`ម៉ឺនុយ` 仍是意圖錯配、品牌搜尋仍是零。
3. **抓住極少數真的可做的事**:某個既有頁面對某個真實查詢排在第 8 至 12 名,而且標題裡沒有那個詞。

每季產出一行台帳(§5),讓趨勢能跨期比較。

## 1. 角色分工

| 角色 | Session | 做什麼 |
| :--- | :--- | :--- |
| 規劃與稽核 | 主 session(Fable) | 跑量測、判讀、決定本月批次、驗收 worker 交付 |
| 執行 | CKM Worker(Opus) | 程式碼與內容改動,依交辦單逐項做、逐項驗證、回報 |
| 量測 | Sonnet 子代理 | 單純跑指令與整理數字:Lighthouse、curl 矩陣等 |

Worker **不 push**。commit 與 push 由 owner 看過 diff 後決定。

## 2. 程序(每季第一週執行,約 60 分鐘)

每一步都寫「指令」與「什麼算發現」。沒有發現就只記一行數字,不要寫分析。

### 2.1 Search Console 數據

```bash
python devops/gsc_query_report.py --days 90
python devops/gsc_query_report.py --days 28
```

- 本機 `devops/.env` 的 `GOOGLE_SERVICE_ACCOUNT_KEY` 可用(2026-10-08 驗證,`npm run check:env` 12 項通過)。
- 總量與查詢表只看 `country = khm`。台灣與美國是團隊與爬蟲。
- **逐頁判斷不要用柬埔寨頁面表。** 2026-11-14 實測(窗口 08-15 至 11-12):khm 總量是
  38 點擊 / 2,473 曝光,但「頁面 × khm」只回傳 17 列共 8 / 820,三種查法結果相同
  (篩選、`["country","page"]` 雙維度、`aggregationType: byPage`),原因未查明。全國家頁面表
  83 列共 47 / 2,973 是完整的。逐頁數字看全國家表,並註明當期 khm 佔比(該期為曝光的 88%)。
- 第二次執行會覆寫 `devops/reports/gsc_search_queries.json`;兩個窗口都要留就先複製一份。
- 記錄到台帳:khm 點擊、khm 曝光、`ម្ហូបការ` 位置、`មុខម្ហូបការ` 位置、ឡើងផ្ទះ 叢集曝光與位置。
- **什麼算發現**:`ម្ហូបការ` 掉出前 5;某頁某查詢 ≥ 15 次曝光且位置 7 到 12 且標題不含該詞;
  `pages_all` 出現不該存在的 URL(見 2.2)。
- **什麼不算發現**:`ចុងភៅ` 叢集的曝光再高也不追(§18);`ម៉ឺនុយ` 零點擊不追;英文查詢落在
  `www.` 不追(Google 已認 apex 為 canonical,見 2.2)。

### 2.2 索引衛生

三個獨立機制,缺一不可(§0:驗證要用不同機制):

**(a) 即時路由矩陣** —— 對下列 URL 做 `curl -sI`,預期值寫在後面:

| URL | 預期 |
| :--- | :--- |
| `https://www.ckmkh.com/` | 301 → apex |
| `http://ckmkh.com/` | 301 → https |
| `/en/`、`/zh/`、`/en/tanghuot/` | 301 → `/` |
| `/pulse/pulse-NN/`(抽 3 個) | 301 → 描述性 slug |
| `/blog/page/1/`、`/pulse/1/` | 301 → `/blog/`、`/pulse/`(2026-10 批次修復後) |
| `/blog/02-khmer-chinese-fusion/`、`/blog/04-temperature-flavor-consistency/` | 301(2026-10 批次修復後) |
| `/sitemap-index.xml`、`/robots.txt`、`/llms.txt` | 200 |

**(b) GSC 回報的每個頁面都還活著** —— 把 `devops/reports/gsc_search_queries.json` 的
`pages_all` 逐一 `curl`,任何 404 都是發現(Google 仍在爬的死頁)。

**(c) Search Console URL Inspection API** —— 對 canonical 集合(首頁、/blog/、/pulse/、
/tanghuot/、blog 01、07、15,加上 (a) 裡每個 301 的來源)查 `coverageState` 與
`googleCanonical`。預期:canonical 頁 `Submitted and indexed`,301 來源
`Page with redirect` 且 `googleCanonical` 指向 apex 目標。唯讀 scope
`webmasters.readonly` 就夠,本機金鑰可用。

**sitemap API 的 `indexed: 0` 不是訊號**:Google 自 2020 年起不再填這個欄位,永遠是 0。
看 `errors` / `warnings` 與 `lastDownloaded` 就好。另外 `lastSubmitted` 每週日都會被
`verify_credentials.yml` 的寫入能力探測重送(2026-10-04 那次就是它),所以它也不代表
「有東西改了」。

### 2.3 內容閘門與衍生檔

```bash
python devops/check_content.py
python devops/generate_llms_txt.py --check
python devops/apply_internal_links.py --check
python devops/fix_section_order.py --check
```

全部要 0 errors。`llms.txt` 以前由每日 pulse workflow 重生,pulse 凍結後沒有人重生它,
所以它會漂移——2026-10 已漂移(一個高棉字錯字修正沒跟上)。

### 2.4 渲染後的標題與描述預算

`check_content.py` 只讀 frontmatter 與 `pulseData.json`,**不讀 `.astro` 頁面模板**。
所以每月要從 live HTML 量一次列表頁與首頁:用 `check_content.display_width` 量
`<title>` 與 `meta description`,預算 60 / 155 單位。2026-10 量測 14 頁全部在預算內
(首頁 52.7u,/tanghuot/ 59.0u 最接近上限)。

### 2.5 Core Web Vitals

PageSpeed Insights 匿名配額是全球共用的,經常耗盡(2026-10-08 即是)。改用本機 Lighthouse:

```bash
npx --no-install lighthouse https://ckmkh.com/ --form-factor=mobile --screenEmulation.mobile --output=json --output-path=devops/reports/lighthouse_home_mobile.json --chrome-flags="--headless=new"
```

量首頁、blog 07、/tanghuot/ 三頁的行動版,類別加上 accessibility。記錄 LCP、CLS、總位元組,
以及 `color-contrast` 與 `label-content-name-mismatch` 是否為 1(§4 說過 Lighthouse 給後者的
權重是 0,類別 100 分不代表它通過,要看單項)。Chrome 清暫存目錄時在 Windows 會印 EPERM
stack trace,JSON 已完整寫出,忽略。這是量測,交給 Sonnet。

- `--no-install` 只在 npx 快取還留著 Lighthouse 時有效。2026-11-14 快取已清,指令直接失敗
  (`npx canceled due to missing packages`);改用 `npx --yes lighthouse@<版本>`,只進 npm 快取,
  不寫入 `package.json`。
- **Performance 與 TBT 只在機器閒置時才能跨期比較。** 讀報告裡的 `environment.benchmarkIndex`:
  2026-11-14 同時有多個 session 在跑,該值只有 687 至 925,首頁 TBT 量到 4,680 ms(10 月是
  430 ms),而程式碼自 10-08 起一行未改。LCP、CLS、總位元組不受影響,可以比。

### 2.6 Workflow 健康

```bash
gh auth switch --hostname github.com --user chengkoungmeng-hue
gh run list --limit 12
```

預期:`Search Report`(週一)與 `Verify Credentials`(週日)每週各一次綠燈。紅燈即發現。

### 2.7 Cloudflare Web Analytics(owner 手動)

本機 `CLOUDFLARE_API_TOKEN` 只有 zone 層權限,GraphQL 的 `rumPageloadEventsAdaptiveGroups`
回 `not authorized for that account`(2026-10-08 驗證)。要用 API 讀,owner 得在 dashboard
另發一把只帶 `Account Analytics: Read` 的唯讀 token。在那之前,這一項由 owner 在 dashboard
看:30 天 visits、來源網域、國家。重點是看 Facebook / Telegram 的 UTM 有沒有出現。

### 2.8 依賴更新(每季)

```bash
npm outdated
npm audit
```

- 只做 semver 範圍內的更新:`npm update` 加 `npm audit fix`,**不加 `--force`**,不升 major。
- 判準是「更新前後 `dist/` 內容相同」:先在 HEAD 建置留一份基準,更新後再建置,比對頁數、
  sitemap URL 清單,以及首頁、blog 07、`/tanghuot/`、一個 pulse 頁的 HTML(先把 `/_astro/`
  雜湊檔名正規化)。
- 本站是純靜態輸出、沒有不受信任的輸入,建置工具鏈的弱點實際曝險低;這是衛生,不是緊急修補。
  剩餘弱點若只能靠 major 解,列出來交 owner 決定,不要順手升。

## 3. 本月批次怎麼決定

- 索引污染、404、漂移、紅燈:**一律修**,交給 worker。
- 標題改寫:只在 2.1 的「發現」條件成立時做,一次最多一頁,改 metadata 不蓋 `revision:`(§14)。
- 新文章、外鏈、pulse 解凍:**不做**。理由在 §15、§18、§19,不要重新推導。

## 4. 2026-10 稽核結果(2026-10-08,窗口 2026-07-09 → 2026-10-06)

### 數字

| 指標 | 90 天 | 28 天 | 上次(09-11 拉,窗口至 09-09) |
| :--- | ---: | ---: | ---: |
| khm 點擊 | 30 | 8 | 27 |
| khm 曝光 | 1,864 | 869 | 1,351 |
| khm CTR | 1.61% | 0.92% | 2.0% |
| `ម្ហូបការ` 位置(khm) | 3.21 | 4.05 | 3.50 |
| `មុខម្ហូបការ` 位置(khm) | 5.73 | 6.12 | 5.27 |
| ឡើងផ្ទះ 叢集曝光 / 位置 | 51 / ~8.5 | 27 / 7.9 | 未分拆 |
| pulse khm 曝光 / 點擊(上線以來) | 16 / 0 | — | 2 / 0 |

曝光漲了,點擊沒漲;漲的曝光多半是 `ចុងភៅ`(162,零點擊)與 `ម៉ឺនុយ`(81,零點擊)。結論不變。

### 發現(交 worker 修)

1. **`/blog/page/1/` 與 `/pulse/1/` 是 `/blog/` 與 `/pulse/` 的完整複本**:相同 12 筆內容、
   各自 self-canonical、都在 sitemap 裡、Google 都已 `Submitted and indexed`。站內連結其實
   已經繞開它們(第 2 頁的「上一頁」指向 `/blog/`),它們只是被 `paginate()` 產出並塞進 sitemap。
2. **兩個舊 blog slug 404 仍被 Google 爬**:`02-khmer-chinese-fusion`、
   `04-temperature-flavor-consistency` 在 `90b9a98`(2026-07-04)被改名刪除,沒留 301。
   Google 8 月仍爬到 404,來源是舊的 `/zh/blog/…` 連結。
3. **`/pulse/pickled-daikon-pulse-19/` 404**,Google 9 月 19 日還在爬,GSC 有 2 次曝光。
   同題材的 `pickled-daikon-pulse-20` 仍在線。
4. **`llms.txt` / `llms-full.txt` 漂移**:`milk-pudding` 標題的 `បច្គេក` → `បច្ចេក` 錯字修正
   沒重生。凍結 pulse 後沒有任何 workflow 會重生它們。
5. **blog 07 是本站唯一的真實機會**:ឡើងផ្ទះ 叢集 4 個查詢共 51 次曝光、位置 8 到 11,
   而文章 `seoTitle` 只含 `ពិធីឡើងផ្ទះថ្មី`,不含曝光最高的 `កម្មវិធីឡើងផ្ទះ`(26)與
   `គេហដ្ឋានថ្មី`(18);內文 `កម្មវិធីឡើងផ្ទះ` 出現 0 次、`ម្ហូបការ` 出現 0 次。

6. **Logo 連結的 `aria-label` 蓋掉可見文字(WCAG 2.5.3,§4 記錄過的同型缺陷)**:
   `Layout.astro` 約第 404 行,`aria-label={isMooncakePage ? "ហាងនំ តាំង ហួត" : "Home"}`,
   而連結內可見文字是 `activeTitle` + `activeSubtitle`。Lighthouse 在 `/tanghuot/` 以
   `label-content-name-mismatch` 失敗;首頁的 `"Home"` 同樣與高棉文可見文字不符,只是沒被抓到。
   拿掉 `aria-label` 即可,`<img alt>` 與可見文字已構成無障礙名稱。
7. **對比度不足(Lighthouse `color-contrast`)**,全是小字標籤,不是主文:
   - 首頁 `span.eyebrow text-slate-400` 在白底(2.56:1),`p.eyebrow text-slate-500` 與
     `span.text-[11px] text-slate-500` 在 onyx 底(3.76:1)。淺底用 `slate-500` 以上,
     深底用 `slate-400` 以上,剛好反過來。
   - `blog/[slug].astro` 第 130、132 行 breadcrumb `text-slate-400`(2.45:1),第 146 行
     `text-amber-600` 作者標籤(3.04:1)——§9 本就禁止 `amber-*`,改 `champagne-dark`。
   - `/tanghuot/` 主 CTA `bg-kh-red`(其實是 `#C5A059` 金色)配白字 2.45:1,是整頁最重要的
     按鈕;改 `champagne-dark`(`#8C6D31`,白字 4.83:1)。

### Lighthouse 行動版(本機 13.5.0,單次,lab 數據)

| 頁 | Perf | SEO | A11y | LCP | CLS | TBT | 總位元組 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `/` | 72 | 100 | 96 | 3.6 s | 0 | 430 ms | 1,010 KiB |
| blog 07 | 74 | 100 | 96 | 3.9 s | 0 | 260 ms | 683 KiB |
| `/tanghuot/` | 81 | 100 | 96 | 3.2 s | 0 | 260 ms | 490 KiB |

LCP 是 lab 模擬 4G 的數字,CrUX 沒有欄位資料(流量太低),所以**這組數字只能跟自己比**,
不能當真實使用者體驗。單次執行在 Windows 上會飄 3 到 5 分。唯一的 opportunity 是
server-response-time 34 至 64 ms,沒有可動的東西。

### 不是發現(記錄以免下個月重查)

- `https://www.ckmkh.com/` 在 GSC 以 1 到 3 名承接英文查詢:URL Inspection 顯示
  `Page with redirect`,`googleCanonical = https://ckmkh.com/`。這是 Google 回報 301 來源,不用修。
- sitemap 65 筆、0 errors、`lastDownloaded 2026-10-04`。
- 14 個 live 頁面的 title / description 全在預算內。
- `check_content.py` 0 errors 0 warnings;workflow 近 8 週全綠;本機憑證 12 項通過。
- 外部指向本站的連結來自兩個垃圾部落格(blogspot、nature-health),忽略。

### 驗收(2026-10-08,主 session 以不同機制複驗)

| 項 | Worker 做法 | 複驗機制 | 結果 |
| :--- | :--- | :--- | :--- |
| 1 分頁複本 | 兩個 `[page].astro` 過濾 `currentPage !== 1`;`_redirects` 加 4 條 | 自行 `npm run build`,檢查 `dist/` | page 1 目錄不存在,sitemap 65 → 63,dist 內零 href 指向它們 |
| 2 舊 slug | 3 組 6 條 301 | 目標頁在 `dist/` 存在 | 通過 |
| 3 llms | 重生 + `content_gate.yml` 加 `--check` 步驟與觸發路徑 | `generate_llms_txt.py --check` | exit 0 |
| 4 blog 07 | 只改 seoTitle、description、快答兩處 | 從 `dist/` HTML 量 | title 55.4u、desc 140.3u、`datePublished` 不變、無 `dateModified`;`check_content.py` 0/0 |
| 6a aria-label | 整行刪除 | grep `dist/` 三頁 | 零 aria-label |
| 6b 對比度 | 見 diff;MooncakePage 只改 CTA class(`--kh-red` 是死碼,改它無效) | Worker 的 Lighthouse JSON | `/` 與 blog 07 兩項皆 1;`/tanghuot/` Facebook 按鈕 `#1877F2` 4.23:1 → `#166FE5` 4.73:1,複跑後三頁兩項皆 1 |

Worker 另外觀察到:`90b9a98` 還刪了 10 個舊 slug 都沒有 301,但 GSC 沒看到被爬,依 §2.1 不算
發現;`MooncakePage.astro` 的 `--kh-red` 與 `.border-kh-red` 是死碼。兩者都記錄,不處理。

### 需要 owner 審的高棉文(commit 前)

- blog 07 新 seoTitle:`កម្មវិធីឡើងផ្ទះថ្មី៖ គន្លឹះវាយតម្លៃទីតាំង និងសេវាកម្មម្ហូបការ`
- description 只換一個詞:`ពិធីឡើងផ្ទះថ្មី` → `ពិធីឡើងគេហដ្ឋានថ្មី`
- 快答段:`ការរៀបចំកម្មវិធី` → `ការរៀបចំកម្មវិធីឡើងផ្ទះ`;`សេវាកម្មម្ហូបអាហារ (សេវាកម្មធ្វើម្ហូប)` →
  `សេវាកម្មម្ហូបការ`(拿掉同義括號)
- 既有狀態、沒改:快答首句的 `សហភាវរតន៍` 兩個 session 都不認得,疑似生成錯字;快答段約 600 字,
  §14 寫 40 到 80 字。這兩點屬內容品質,留給 owner 決定。

## 4b. 2026-11 稽核結果(2026-11-14,窗口 2026-08-15 → 2026-11-12)

### 數字

| 指標 | 90 天 | 28 天(10-16 → 11-12) | 上次(10-08 拉,90 天) |
| :--- | ---: | ---: | ---: |
| khm 點擊 | 38 | 19 | 30 |
| khm 曝光 | 2,473 | 879 | 1,864 |
| khm CTR | 1.54% | 2.16% | 1.61% |
| `ម្ហូបការ` 位置(khm) | 3.85 | 4.25 | 3.21 |
| `មុខម្ហូបការ` 位置(khm) | 6.39 | 7.17 | 5.73 |
| ឡើងផ្ទះ 叢集曝光(khm,可見查詢) | 64 | 9 | 51 |

全國家頁面表(完整,khm 佔曝光 88%),90 天:

| 區塊 | URL 數 | 曝光 | 點擊 |
| :--- | ---: | ---: | ---: |
| `/` | 1 | 950 | 19 |
| blog 07 | 1 | 534 | 8 |
| blog 01 | 1 | 236 | 5 |
| 其餘 13 篇加 `/blog/` 列表 | 15 | 455 | 8 |
| `/pulse/` | 59 | 602 | 5 |
| `/tanghuot/` | 1 | 133 | 2 |

- 文章合計 21 次點擊,多於首頁的 19 次。9 月 worklog 的「15 篇合計約 120 曝光、1 點擊」
  出自柬埔寨頁面表,那張表只涵蓋三分之一(§2.1),結論的數字要更正,凍結的決定不變。
- 可見查詢只涵蓋 khm 曝光的 31%(778 / 2,473)與 8 / 38 次點擊;其餘是 Google 不揭露的長尾。
- 10 月改過標題的 blog 07:`កម្មវិធីឡើងផ្ទះ` 近 28 天排名 5.33(改前 28 天叢集約 7.9),
  但只有 6 次曝光,樣本太小,不下結論。全國家近 28 天 181 曝光 / 3 點擊,與前期 190 / 4 持平。

### 發現(交 worker 修)

1. **`/pulse/korean-style-stuffed-peppers-pulse-12/` 404,GSC 仍回報。** 現行 slug 是 `-pulse-13`,
   舊 slug 最後出現在 `8f0dba9`,與 10 月修過的 `pickled-daikon-pulse-19` 同一個重新編號事件。
   同型缺陷第二次出現,所以本次要 worker 掃完整個 git 歷史裡出現過的 slug,一次補齊。
2. **`Verify Credentials` 連續三週紅燈(10-25、11-01、11-08)。** 只有 `gemini` job 失敗:
   金鑰認證通過,但兩個階梯模型都回 `403 The Gemini API free tier is not available for this
   project`。pulse 已凍結、沒有排程消費者,而紅燈會掩蓋另外兩把真正在用的憑證出問題。
   處置:該 job 只在手動觸發時執行;是否刪除 `GEMINI_API_KEY` 由 owner 決定。
3. **`npm audit` 21 項(1 critical、13 high、6 moderate、1 low)。** critical 是 `astro` 本身。
   純靜態站,實際曝險低。處置見 §2.8。
4. **`gsc_query_report.py` 的柬埔寨頁面表只涵蓋 33% 的曝光,而且沒有任何提示。** 處置:
   腳本印出覆蓋率並在偏低時警告;AGENTS.md §18 引用該表的數字一併更正。
5. **`មុខម្ហូបការ` 持續下滑(5.27 → 5.73 → 6.39,近 28 天 7.17;落在首頁的部分 7.96、25 次曝光),
   而這個詞在首頁原始碼出現 0 次。** 符合 §2.1 的發現條件。處置:菜單區 H2 與 `Menu` schema
   的 `name` 放進該詞,本季只做這一處內容改動。

### 發現(owner 在 dashboard 決定,不交 worker)

1. **Cloudflare 在每頁注入 `/cdn-cgi/challenge-platform/scripts/jsd/main.js`**(JavaScript
   Detections)。Lighthouse 的 `deprecations` 因它失敗(Fenced Frame API、`StorageType.persistent`),
   Best Practices 三頁皆 81;在模擬的行動 CPU 上它佔 520 至 660 ms 主執行緒。10 月沒量 Best
   Practices,所以不知道它是何時開始注入的。本站沒有表單與登入,它擋得到的東西有限;
   關不關是安全與效能的取捨,影響小。AGENTS.md §18 寫的「第三方腳本只有 beacon」仍然成立,
   因為這支走的是同源路徑。

### Lighthouse 行動版(13.6.0,單次,lab;本次機器負載高,Perf 與 TBT 不可比)

| 頁 | Perf | SEO | A11y | BP | LCP | CLS | TBT | 總位元組 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `/` | 56 | 100 | 100 | 81 | 3.6 s | 0 | 4,680 ms | 1,024 KiB |
| blog 07 | 62 | 100 | 100 | 81 | 3.6 s | 0 | 1,570 ms | 686 KiB |
| `/tanghuot/` | 59 | 100 | 100 | 81 | 3.8 s | 0 | 2,190 ms | 491 KiB |

`color-contrast` 與 `label-content-name-mismatch` 三頁皆為 1,10 月的無障礙修正仍然有效
(A11y 96 → 100)。LCP 與總位元組與 10 月相同。

### 不是發現

- 路由矩陣全部符合預期;GSC 回報的 83 個 URL 中 61 個 200、21 個 301 到正確目標,
  唯一的 404 是上面第 1 項。
- URL Inspection:首頁、`/blog/`、`/pulse/`、`/tanghuot/`、blog 01、07、13、15 皆
  `Submitted and indexed`,最近爬取 11-03 至 11-13。`/blog/page/1/` 與 `/pulse/1/` 已變成
  `Page with redirect`,10 月的修正被 Google 接受。舊 404(`pickled-daikon-pulse-19`、
  `04-temperature-flavor-consistency`)的最後爬取日都早於 10-08,Google 還沒回來看 301。
- 四個內容閘門全部 exit 0;`check_content.py` 0 errors 0 warnings。
- 渲染後的標題預算本次未重量:HEAD 仍是 10-08 的 `eb69fec`,模板與 frontmatter 沒變。
- `ម្ហូបការ` 3.85,仍在前 5。`ម៉ឺនុយ`(104 曝光 0 點擊)與 `ចុងភៅ`(174 曝光 0 點擊)照舊不追。

### 驗收(2026-11-14,主 session 以不同機制複驗)

| 項 | Worker 做法 | 複驗機制 | 結果 |
| :--- | :--- | :--- | :--- |
| 1 pulse 舊 slug | 掃 `pulseData.json` 全部 32 個 commit:歷來 99 個 slug、已消失 62 個、其中 2 個已有規則;補 60 組 120 條 301(47 組對到後繼者,13 組到 `/pulse/`) | 自寫解析器讀 `_redirects` 對 `dist/`;另以 slug 詞幹比對對應關係(與 worker 用的 `source_link` 不同機制) | 210 條規則、0 重複來源、0 目標缺失、0 來源被已建置頁面遮蔽、0 串鏈;39 組詞幹相同,8 組詞幹不同者逐一看過合理 |
| 2 Verify Credentials | `gemini` job 加 `if: github.event_name == 'workflow_dispatch'` 與說明註解;AGENTS.md §15、§16 更新 | 讀 diff | 通過。排程時的實際行為要等 push 後第一個週日才能確認,**尚未驗證** |
| 3 依賴更新 | `npm update` 加 `npm audit fix`;`package.json` 不變;astro 6.1.8 → 6.4.8、@lucide/astro 1.23.0 → 1.73.0 等 | 自行 `npm run build`;`git diff --quiet package.json`;自行 `npm audit` | 建置 exit 0、64 頁、sitemap 63。Worker 比對 64 頁:只有 generator meta 與 286 處 Lucide SVG 不同。剩餘弱點見下 |
| 4 GSC 覆蓋率 | 腳本新增 `coverage()` 與警告,`meta` 寫入兩個覆蓋率欄位;AGENTS.md §18 更正 | 讀 diff;對照我先前獨立量到的 820 / 2,473 與 778 / 2,473 | 一致(33.2%、31.5%) |
| 5 首頁菜單標題 | `index.astro` 第 68、255 行 | 讀 `dist/index.html` | 新字串 2 次、舊字串 0 次;`មុខម្ហូបការ` 在首頁由 0 次變為有 |

依賴更新的剩餘事項:

- `@astrojs/check` 0.9.12 連帶的 language-server 2.17 換了 parser,遇到 `pulse/[id].astro` 第 259 行
  註解(運算式內的 HTML 註解,同時含奇數個撇號與 `<tag>` 字樣)會報錯。Worker 有最小重現。
  第一輪 worker 把 check 鎖回 0.9.8,但那只鎖在 lockfile,下次 `npm update` 會再壞,而且舊版
  language-server 帶著 yaml 鏈的 4 個 moderate(worker 回報剩 5 項,主 session 實測 9 項,
  差的就是這 4 項)。第二輪改修根因:該註解改寫一行(`CKM's own generated` →
  `the CKM-generated`),check 升到 0.9.12。主 session 複驗:建置 exit 0、`astro check`
  0 errors 0 warnings 36 hints、64 頁、sitemap 63;`npm audit` 21 → **5**
  (1 critical、1 high、2 moderate、1 low)。
- Astro 會把 `.astro` 模板裡的 `<!-- -->` 註解原樣輸出到 HTML(上述那段註解出現在全部 37 個
  pulse 內頁)。不影響功能,體積極小,只記錄,不處理。
- 只能靠 major 解的弱點,**本季不做,交 owner 決定**:`astro`(要 7.4.7 以上;公告已不只 XSS,
  含 AVIF 影像最佳化的 RCE 一則,本站只在建置時處理自己的圖,沒有執行期影像端點)、`sharp`、
  `esbuild`(皆隨 astro 7)、`@tailwindcss/typography` 與 `postcss-selector-parser`(0.5.x 內無修正版)。
- 既有狀態:`@astrojs/tailwind 5.1.5` 的 peer 範圍只到 astro 5,升 astro 6 時就已不符。
  升 astro 7 會連帶牽動 Tailwind 的整合方式,是獨立的一件工作,不是順手能做的。

### 需要 owner 審的高棉文(commit 前)

- 首頁菜單區 H2 與 `Menu` schema 的 `name`:`មុខម្ហូបប្រចាំតុរបស់យើងខ្ញុំ` →
  `មុខម្ហូបការប្រចាំតុរបស់យើងខ្ញុំ`(插入 `ការ`)。
- 該 H2 上方的小標已是 `ម៉ឺនុយម្ហូបការ`,兩行都含 `ម្ហូបការ`,請一併看是否顯得重複。
  兩個 session 都不是母語者。

## 5. 台帳

| 月份 | khm 點擊 / 曝光(90d) | `ម្ហូបការ` 位置 | ឡើងផ្ទះ 叢集 | 發現數 | 批次 |
| :--- | :--- | ---: | :--- | ---: | :--- |
| 2026-09 | 27 / 1,351 | 3.50 | 未分拆 | 3 | hreflang、字型快取、hero 體積 |
| 2026-10 | 30 / 1,864 | 3.21 | 51 imp / pos 8.5 | 7 | 分頁複本、舊 slug 301、llms 重生、blog 07 標題、aria-label、對比度 |
| 2026-11 | 38 / 2,473 | 3.85 | 64 imp / pos 7.7 至 14 | 6 | pulse 舊 slug 301、Verify Credentials 紅燈、依賴更新、GSC 覆蓋率警告、首頁菜單標題 |

# 憑證與權限基準線(跨專案通用)

這份文件不是 CKM 專屬的。任何有 API 憑證的專案都可以直接照著跑一遍。
建立於 2026-08-14,來源是 CKM 的一次實際稽核 —— 每一條規則背後都有一個真的踩過的坑。

---

## 0. 核心判準

> **憑證只存在於真的需要它的地方,而且只帶著在那裡需要的權限。**

兩個推論,**照順序做**:

1. **先刪掉沒人需要的副本。** 沒有任何程式讀取的憑證,是純風險、零效益。
2. **再降低刪不掉的那些的權限。** 把一把鑰匙拆成兩把,除非第二把**嚴格更弱**,否則毫無意義 —— 重點是最小權限,不是「拆開」。

### 依「損害」分級,不是依「有沒有在用」

「沒人在用」單獨拿出來是很弱的理由。要問的是:**這把鑰匙外洩時,對方能造成什麼損害?**

| 等級 | 例子 | 外洩後 | 動作 |
| :--- | :--- | :--- | :--- |
| **可計費 / 可存資料** | BigQuery、Cloud SQL、Cloud Storage、任何運算服務 | 用你的帳單跑運算、託管惡意檔案 | **關掉** |
| **可寫入設定** | GA4 Admin API、DNS 編輯、WAF 規則寫入 | 弄壞東西、刪掉救不回的歷史資料 | **降權或關掉** |
| **唯讀且不計費** | GA4 Data API、分析報表讀取 | 對方知道你的流量數字 | 開關都行,**不是資安決策** |
| **基礎設施** | Service Usage、Service Management、Telemetry、Logging | 無 | **留著。** 關掉沒好處,可能造成難查的怪問題 |

**不要把「關掉無害的東西」跟「關掉危險的東西」用同樣的語氣講。** 那會稀釋真正重要的建議,
讓人分不出哪幾條該認真對待。

---

## 1. 盤點:誰在讀什麼

**不要用猜的。** 每個專案先跑這幾行:

```bash
# Python
grep -rhoE "os\.(getenv|environ(\.get)?)\(\s*[\"'][A-Z_0-9]+[\"']" . --include=*.py

# JS / TS / Astro
grep -rhoE "(process\.env|import\.meta\.env)\.[A-Z_0-9]+" . --include=*.js --include=*.ts --include=*.astro

# CI
grep -rhoE "secrets\.[A-Z_0-9]+" .github/workflows/

# 實際呼叫了哪些外部端點
grep -rhoE "https://[a-z0-9.-]+\.(googleapis|cloudflare|openai|anthropic)\.com/[a-zA-Z0-9/._-]*" . | sort -u
```

把結果跟 `.env`、CI secrets、雲端平台上的憑證清單三方對照。**任何一邊有、但沒有程式讀的,就是該刪的。**

### 已知的假陽性

- 憑證可能被**設定在原始碼之外**(見 §5)。grep 找不到不代表沒裝。
- `GITHUB_OUTPUT` 之類是 CI 內建變數,不是你的 secret。

---

## 2. 每個環境需要什麼

| 環境 | 憑證放哪 | 注意 |
| :--- | :--- | :--- |
| 本機 | `.env`(**必須 gitignored**) | 只放本機真的會跑的腳本需要的 |
| CI | GitHub Actions secrets | **寫得進去、讀不出來**。沒有任何方式可以把值取回 |
| Git 認證 | OS credential manager | **絕對不要**把 token 放進 remote URL |
| 一次性操作 | **不存** | 用時開、設到期日、用完撤銷 |

### 「現在沒在用」和「不需要」是同一種風險

一年用兩次的憑證,不該在中間那 363 天躺在 `.env` 裡。它能造成的損害不會因為你沒在用而變小。
**開 → 用 → 撤銷。**

### GitHub Actions secrets 是單向的

**沒有任何方法可以把值讀出來** —— 不管是 API、`gh` CLI、還是 AI agent。
如果想要「本機零 secret」,正確做法是**把工作搬進 CI**(包成 `workflow_dispatch`),
而不是想辦法把值搬出來。

### repo 寫入權 = secret 存取權

任何能推 workflow 的人,都能寫一支把 secret 做 base64 再印出來的 workflow
(遮蔽只認原始字串,編碼就繞掉)。集中在 GitHub 確實減少外洩點,
但代價是**帳號被攻破 = 全部被攻破**。所以:帳號開 2FA、workflow 變更要看過。

---

## 3. 權限稽核:光看「有沒有開」不夠

### API 開關只是第二道防線

**IAM 角色才是第一道。** 如果 service account 是 Owner / Editor,
它可以自己把你關掉的 API 開回來 —— 你的清理形同虛設。

- **GCP**:IAM & Admin → IAM → 找到該 service account → 檢視角色
- 很多情況下需要的 GCP 角色是**零個**。例如 Search Console 的存取權是在
  **Search Console 後台**授權的,跟 GCP IAM 無關。

### 「有 scope」不等於「權限小」

一把有作用域的 token 仍然可能很危險。**要驗證它到底能做什麼,不是只驗證它不是 global key。**

```bash
# Cloudflare:確認是 scoped token 而非 Global API Key(不會印出 token 本身)
export CF_TOKEN=$(grep '^CLOUDFLARE_API_TOKEN=' .env | cut -d= -f2- | tr -d '\r\n"')
curl -s https://api.cloudflare.com/client/v4/user/tokens/verify \
  -H "Authorization: Bearer $CF_TOKEN"
```

**實際案例:** CKM 的 Cloudflare token 通過了上面這個檢查(確實是 scoped token),
但它同時能 `PUT /rulesets/phases/…/entrypoint` —— 也就是重寫整個網站的 WAF、
速率限制和快取規則。而 CI 只用它清快取。**通過 verify 不等於安全。**

### 永遠不要使用「全域」等級的憑證

有些平台除了可設定範圍的 token 之外,還有一把**無法限制**的萬用鑰匙:

| 平台 | 那把東西 | 特性 |
| :--- | :--- | :--- |
| Cloudflare | **Global API Key** | 全帳號權限、不能設 scope、永不過期、**不能刪除只能 Roll** |
| GCP | 專案 Owner 角色的 service account | 能自己把你關掉的 API 開回來 |
| GitHub | 有 `repo` + `workflow` scope 的 classic PAT | 能推 workflow 就能偷走所有 secret |

**Cloudflare Global API Key 特別要注意:**

- 它**不是你建立的** —— 每個帳號天生就有,不管用不用
- 外洩後對方可以**改 DNS**,等於整個網域被接管
- 任何教學或工具叫你貼 Global API Key,都是過時做法 —— 一律改用 scoped API token
- 因為不能刪除,唯一的處置是 **Roll**(重新產生,舊值失效)。不確定它有沒有被複製過,就 Roll

### 到期日要跟破壞力成正比,不是一律要設

**不要機械式地給每把 token 設 TTL。** 判準是:**這把外洩後能造成什麼損害?**

| 破壞力 | 例子 | TTL |
| :--- | :--- | :--- |
| 高(可寫入設定、可計費、可刪資料) | WAF 寫入、DNS 編輯、BigQuery | **必須設** |
| 低(唯讀、或單一無害動作) | 清快取、讀分析數據 | **不要設** |

低破壞力的憑證設了 TTL,換來的是**到期那天靜默失敗**。

**實際案例:** CKM 的 `notify_indexing.py` 把清快取包在 `try/except` 裡,失敗只印一行警告、
不會讓 workflow 變紅。給那把 purge-only token 設一年到期,一年後的某個半夜它會停止工作,
而**沒有任何人會知道**。安全收益趨近零,運維風險是真的。

**設 TTL 之前先問:到期時會不會有人發現?** 如果答案是「不會」,那 TTL 只是把一個
確定會發生的故障排進行事曆。

### 檢查金鑰的數量和年齡

- GCP:IAM → Service Accounts → 該帳號 → Keys。**忘記的舊金鑰仍然有效。**
- Cloudflare / 其他:列出所有 token,找**建立很久卻從未使用**的 —— 那是最典型的孤兒。

---

## 4. 零中斷輪換順序(不可顛倒)

每一把憑證都照這個順序:

1. **開新的**(權限設成剛好夠用;到期日依破壞力決定 —— 見 §3)
2. **更新使用端**(CI secret / `.env`)—— 值直接從產生畫面貼到目的地,**中間不經過任何地方**
3. **測試**(手動觸發一次 workflow / 跑一次腳本)
4. **確認成功之後**,才撤銷舊的
5. 清掉不再需要的本機副本

**先撤舊的會造成服務中斷。** 每次只換一把,換完驗證再換下一把。

---

## 5. 設定住在 repo 外面

grep 找不到,不代表沒有。這些地方的設定完全不會出現在原始碼裡:

| 位置 | 例子 | 怎麼查 |
| :--- | :--- | :--- |
| Cloudflare Zaraz | GA4 / GTM 等第三方腳本 | 用**瀏覽器 UA** curl(Cloudflare 對非瀏覽器 UA 跳過注入) |
| Cloudflare Dashboard | WAF 規則、Cache Rules、Bot 設定 | Dashboard |
| 雲端平台 Console | IAM 角色、API 開關 | Console |
| DNS 供應商 | 記錄、驗證 TXT | DNS 面板 |

```bash
# 用瀏覽器 UA 才看得到 Zaraz 注入的內容
curl -s https://example.com/ -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" | grep -c zaraz
```

**把這類「設定在別處」的事實寫進專案的 agent rules。** 否則下一個人(或下一個 AI)
grep 不到,就會得出「沒裝」的錯誤結論,然後「修好」它 —— 造成重複載入或重複計數。

---

## 6. 洩漏防範

### 讀取 secret:一律導進環境變數,絕不進 stdout

```bash
export TOKEN=$(grep '^SOME_TOKEN=' .env | cut -d= -f2- | tr -d '\r\n"')
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/...
```

### 印出任何可能含憑證的東西之前,先遮蔽

| 不要用 | 改用 |
| :--- | :--- |
| `git remote -v` | `git remote -v \| sed 's#//[^@]*@#//<hidden>@#'` |
| `git config -l` | `git config -l \| sed 's/=.*token.*/=<hidden>/I'` |
| `cat .env` | `sed 's/=.*/=<hidden>/' .env` |
| `env` / `printenv` | 永遠不要整包倒出來,只讀指定的那一個 |

**實際案例:** 一個活的 `ghp_…` PAT 被嵌在 git remote URL 裡,
一句沒遮蔽的 `git remote -v` 就把它完整印進了對話紀錄。使用者什麼都沒貼 ——
洩漏完全來自一個診斷指令。

### 確認 repo 歷史是乾淨的

```bash
git log --all --oneline --name-only --diff-filter=A -- .env '*service_account*.json' '*.pem'
git ls-files | grep -iE "\.env$|service_account|\.pem$|credential"
```

### 公開 repo 額外要檢查

```bash
# workflow 有沒有 pull_request_target(fork PR 可以偷 secret 的典型手法)
grep -rn "pull_request_target\|pull_request" .github/workflows/
```

- **絕對不要**在公開 repo 加 `pull_request_target` 觸發。
- 檢查有沒有把不該公開的資料 commit 進去(分析報告、內部數據、客戶資訊)。

### 憑證不該存進密碼管理器

API token **可以重新產生**,跟銀行密碼不同。存進密碼管理器只是**多一份副本、多一個外洩面**,
換來一個你本來就不需要的功能。密碼管理器是給「弄丟就真的完了」的東西用的。

**正確做法:** 產生 → 直接貼到使用端 → 關掉分頁。要用時不是「找回來」,是「開一把新的」。

---

## 7. 反模式

- ❌ 把 secret 貼給 AI agent、貼進聊天、記事本、email、截圖
- ❌ 用 `PUT` 覆蓋整份設定的腳本(下面單獨說明)
- ❌ **高破壞力**憑證沒有到期日(低破壞力的反而不該設 —— 見上面)
- ❌ 同一把憑證給多個環境用 —— 撤銷代價太高,結果就是拖著不撤
- ❌ 為了「一致」而關掉零風險的基礎設施服務

### 「整份取代」型腳本特別危險

用 `PUT` 寫入設定端點的腳本(例如 Cloudflare 的 `PUT /rulesets/phases/…/entrypoint`),
是**取代整份設定,不是新增**。你之後在 dashboard 加的任何規則,
下次跑腳本都會被**無聲清掉**。

一年動幾次的設定,**用 dashboard 改**。腳本降級成「設定紀錄」,不要執行。

---

## 8. 稽核檢查表

複製到新專案時逐項打勾:

- [ ] 跑 §1 的盤點指令,列出所有被讀取的憑證
- [ ] 對照 `.env` / CI secrets / 雲端憑證清單,刪掉沒人讀的
- [ ] `.env`、金鑰檔在 `.gitignore` 裡
- [ ] git 歷史從未包含憑證(§6 指令)
- [ ] repo 是公開的話 —— 沒有 `pull_request_target`,沒有 commit 內部資料
- [ ] **每個 service account / API key 的 IAM 角色檢查過**(不只是 API 開關)
- [ ] 每把 token 都驗證過「實際能做什麼」,不只是「有沒有 scope」
- [ ] 高破壞力 token 有到期日;低破壞力 token **沒有**被硬塞到期日
- [ ] 沒有在用 Cloudflare Global API Key(或同等的全域憑證);不確定就 Roll
- [ ] 沒有忘記的舊金鑰還有效
- [ ] 可計費服務的 API 全部關閉(除非真的在用)
- [ ] 一次性用途的憑證不長駐 `.env`
- [ ] 「設定在 repo 之外」的事實已寫進 agent rules
- [ ] 輪換時照 §4 的順序,每次一把,換完驗證

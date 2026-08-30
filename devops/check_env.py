#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""一鍵驗證本機開發環境:憑證是活的、外部服務通得到、必備檔案在。

    npm run check:env          (= python devops/check_env.py)

2026-08-31 建立。此前本機沒有任何指令能證明憑證還活著:

* `npm run check` 只讀 15 篇文章的內容,一個憑證都不碰。
* 唯一會打 API 的 devops/Tools/test_gsc_matrix.py 不論成敗一律 exit 0——
  拿一把 Google 不認得的服務帳號金鑰加一個無效 token 實測,它照樣印
  「狀態: 失敗」然後 exit 0。永遠回綠的檢查器擋不住任何東西(同日一併修掉)。
* 真正會亮紅燈的只有 .github/workflows/verify_credentials.yml,而它只在 CI 跑,
  本機沒有對應物。

三條原則,與 devops/sa_credentials.py 同一套(不另立第四種寫法):

1. **環境變數優先於檔案**,路徑一律由 __file__ 推導,與工作目錄無關。
   CWD 相對的載入器是本專案反覆壞掉的那一種(見 cloudflare_audit.js 的註解)。
2. **每一項憑證都真的打一次 API**。「變數有設定」不等於「憑證有效」:
   2026-08-30 的事故是一把還好端端躺在檔案裡、但已被輪替掉的死金鑰,
   三支腳本因此靜默失效,而所有「檔案存在嗎」的檢查全都是綠的。
3. **fail-closed**:任何一項失敗就以非零碼結束並印出缺什麼。缺設定一律當失敗,
   絕不把「沒設定」讀成「通過」。

刻意不做的兩件事:

* **不寫入。** CI 版本會提交 sitemap、清空 Cloudflare 快取來證明寫入權限;
  本機版只讀,因為開發者一天可能跑它十次,而清快取是真的會清。
  寫入權限的證明留給 verify_credentials.yml,那裡一週跑一次。
* **不檢查 pulse 資料新鮮度。** devops/check_pulse_health.py 量的是內容有多舊,
  而 pulse 已於 2026-08-23 由擁有者決定凍結(daily_catering_pulse.yml 的 cron
  已註解),資料集不可能再變新,那支檢查因此永遠是紅的。把它併進來會得到一個
  永遠不會綠的閘門,而永遠紅的閘門會訓練人忽略紅燈。
  環境健康與內容新鮮度不共用一個結束碼。
"""

import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sa_credentials import get_access_token, load_env  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT = 20

SITE = "sc-domain:ckmkh.com"
GSC_SITES_URL = "https://www.googleapis.com/webmasters/v3/sites"
CF_API = "https://api.cloudflare.com/client/v4"
GEMINI_API = "https://generativelanguage.googleapis.com/v1beta"

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"

#: 缺了就無法建置或無法跑內容閘門的檔案。憑證檔不列在這裡——憑證在 CI 是環境變數、
#: 根本沒有 .env,「檔案在不在」也從來不是憑證能不能用的判準,由下面的實打檢查回答。
REQUIRED_PATHS = [
    ("package.json", "npm scripts 進入點"),
    ("astro.config.mjs", "Astro 建置設定"),
    ("node_modules", "npm install 尚未執行"),
    ("src/data/pulseData.json", "src/pages/pulse/ 直接 import,缺了建置會失敗"),
    ("devops/sa_credentials.py", "所有 Search Console 路徑的單一憑證取得點"),
]

#: import 失敗就代表對應的腳本一定跑不起來。列出用到它的地方,壞了才知道要裝什麼。
REQUIRED_MODULES = [
    ("google.auth", "google-auth", "sa_credentials.get_access_token"),
    ("googleapiclient.discovery", "google-api-python-client", "devops/Tools/ 的 GSC 查詢"),
    ("requests", "requests", "notify_indexing.py / apply_cf_settings.py"),
]


def _get(url, headers):
    """GET 一次,回傳 (status, body_dict)。連不上也是失敗,不當成「暫時沒資料」。"""
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(raw or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            return exc.code, json.loads(raw or "{}")
        except json.JSONDecodeError:
            return exc.code, {"raw": raw[:200]}
    except Exception as exc:  # 逾時、DNS、TLS:對呼叫端而言都是「這項不能用」
        return 0, {"error": f"{type(exc).__name__}: {exc}"}


def check_files():
    results = []
    for rel, why in REQUIRED_PATHS:
        target = os.path.join(ROOT, rel)
        if os.path.exists(target):
            results.append((PASS, f"檔案 {rel}", "存在"))
        else:
            results.append((FAIL, f"檔案 {rel}", f"不存在 — {why}"))
    return results


def check_modules():
    results = []
    for module, package, used_by in REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError as exc:
            results.append((FAIL, f"套件 {package}",
                            f"import {module} 失敗({exc})— {used_by} 會直接壞掉。"
                            f"修法:pip install {package}"))
        else:
            results.append((PASS, f"套件 {package}", f"可 import({used_by})"))
    return results


def check_search_console():
    """換一次 token,再讀一次資源清單。兩者都成功才算這把憑證真的能用。"""
    try:
        # get_access_token() 換不到 token 就 sys.exit,那是它單獨執行時的正確行為;
        # 在這裡要攔下來,因為本檢查要一次跑完所有項目再一起報告,不能死在第一項。
        token, source = get_access_token()
    except SystemExit as exc:
        return [(FAIL, "Search Console 憑證", str(exc).replace("\n", " "))]

    results = [(PASS, "Search Console 憑證", f"來源 {source},已實際換取 access token")]

    status, body = _get(GSC_SITES_URL, {"Authorization": f"Bearer {token}"})
    if status != 200:
        results.append((FAIL, "Search Console API",
                        f"列出資源失敗({status}):{json.dumps(body, ensure_ascii=False)[:200]}"))
        return results

    sites = [s.get("siteUrl") for s in body.get("siteEntry", [])]
    if SITE not in sites:
        results.append((FAIL, "Search Console 權限",
                        f"{SITE} 不在此服務帳號的資源清單內(目前:{sites})。"
                        "到 Search Console 把服務帳號加進去。"))
    else:
        results.append((PASS, "Search Console API", f"{SITE} 可讀取(共 {len(sites)} 個資源)"))
    return results


def check_cloudflare(env):
    token = env.get("CLOUDFLARE_API_TOKEN")
    zone_id = env.get("CLOUDFLARE_ZONE_ID")
    results = []

    if not token:
        return [(FAIL, "Cloudflare 憑證",
                 "CLOUDFLARE_API_TOKEN 未設定(環境變數與 devops/.env 都沒有)")]
    if not zone_id:
        results.append((FAIL, "Cloudflare Zone",
                        "CLOUDFLARE_ZONE_ID 未設定,無法確認 token 對應的是哪個 zone"))

    headers = {"Authorization": f"Bearer {token}"}
    status, body = _get(f"{CF_API}/user/tokens/verify", headers)
    if not body.get("success"):
        errors = json.dumps(body.get("errors") or body, ensure_ascii=False)[:200]
        results.append((FAIL, "Cloudflare 憑證",
                        f"token 驗證失敗({status}):{errors}"
                        " — Global API Key 在這個端點一定會失敗,要用 scoped API token"))
        return results

    result = body.get("result", {})
    # 印 token id 而不是 token 本身:id 是儀表板上看得到的識別碼,不是機密,
    # 而它是唯一能證明「現在生效的是哪一把」的東西。
    results.append((PASS, "Cloudflare 憑證",
                    f"token {result.get('id')} 狀態 {result.get('status')},"
                    f"到期 {result.get('expires_on') or '無'}"))

    if zone_id:
        status, body = _get(f"{CF_API}/zones/{zone_id}", headers)
        if not body.get("success"):
            errors = json.dumps(body.get("errors") or body, ensure_ascii=False)[:200]
            results.append((FAIL, "Cloudflare Zone",
                            f"讀取 zone {zone_id} 失敗({status}):{errors}"))
        else:
            zone = body.get("result", {})
            results.append((PASS, "Cloudflare Zone",
                            f"{zone.get('name')}({zone.get('status')})"))
    return results


def check_gemini(env):
    """本機沒有這把 key 是已知且刻意的狀態,但不能因此報成綠燈。

    GEMINI_API_KEY 只存在於 GitHub secret,devops/.env 裡沒有——因為唯一的用途
    devops/fetch_catering_pulse.py 已於 2026-08-23 凍結。所以:有 key 就實打驗證,
    沒有 key 就明確標成 SKIP 並說出理由,不混進 PASS 裡當作「檢查過了」。
    """
    key = env.get("GEMINI_API_KEY")
    if not key:
        return [(SKIP, "Gemini 憑證",
                 "GEMINI_API_KEY 本機未設定。它只在 GitHub secret,"
                 "唯一用途 fetch_catering_pulse.py 已於 2026-08-23 凍結,"
                 "本機不需要。要在本機跑 pulse 就把它加進 devops/.env,"
                 "這一項會自動改為實打驗證")]

    # header 帶 key,絕不用 ?key= — query string 會進 proxy log,
    # 而 urllib 的例外訊息會把整條 URL 印出來。
    status, body = _get(f"{GEMINI_API}/models",
                        {"Content-Type": "application/json", "x-goog-api-key": key})
    if status != 200:
        message = (body.get("error") or {}).get("message") or json.dumps(body, ensure_ascii=False)
        return [(FAIL, "Gemini 憑證", f"key 被拒({status}):{str(message)[:200]}")]
    models = body.get("models", [])
    return [(PASS, "Gemini 憑證", f"key 有效,可見 {len(models)} 個模型")]


def main():
    env = load_env()

    print("=" * 66)
    print("  CKM 開發環境檢查 — 憑證一律實際打 API,不看變數有沒有設")
    print("=" * 66)

    results = []
    results += check_files()
    results += check_modules()
    results += check_search_console()
    results += check_cloudflare(env)
    results += check_gemini(env)

    for status, label, detail in results:
        print(f"[{status}] {label}: {detail}")

    failed = [r for r in results if r[0] == FAIL]
    skipped = [r for r in results if r[0] == SKIP]
    passed = [r for r in results if r[0] == PASS]

    print("-" * 66)
    print(f"通過 {len(passed)} 項,跳過 {len(skipped)} 項,失敗 {len(failed)} 項")

    if failed:
        print("\n環境不健康。以下項目要先修好:")
        for _status, label, detail in failed:
            print(f"  - {label}: {detail}")
        return 1

    print("環境健康:憑證都換得到 token / 通得過 API,必備檔案齊全。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Search Console 服務帳號憑證的單一取得點。

2026-08-30 建立。此前有兩處各自載入憑證(gsc_query_report.find_key_file 與
notify_indexing.notify_gsc_api),判準都是「檔案存不存在」。而本機的
google_service_account.json 裡是一把已被輪替掉的死金鑰——取 token 時回
`Invalid JWT Signature`——於是 gsc_query_report.py、notify_indexing.py 與
check_pulse_indexation.py 三支全部靜默失效,沒有任何檢查會發現。

同一天在 TWProbe 出現同型事故:devops/Vault/config_production.json 裡的
Cloudflare token 是死的(401),60 支腳本讀它。兩次的共同點是
**判準停在「檔案在」,沒有問「憑證能用嗎」**。

因此本模組刻意做兩件事:

1. **環境變數優先於檔案。** 檔案是最容易變成過期副本的那一種載體:它不會
   隨輪替更新,也沒有人會去看它。順序為
   SEARCH_CONSOLE_SA_JSON(CI 提供) -> GOOGLE_SERVICE_ACCOUNT_KEY(本機 .env)
   -> 檔案候選清單(相容舊行為)。
2. **回傳前先真的換一次 token。** 換不到就以非零結束並說出是哪一個來源壞掉,
   而不是讓呼叫端拿著死憑證繼續跑到某個看起來像「沒有資料」的結果。
"""

import json
import os
import sys

SCOPES_READONLY = ["https://www.googleapis.com/auth/webmasters.readonly"]
SCOPES_WRITE = ["https://www.googleapis.com/auth/webmasters"]

# 相容舊行為:環境變數都沒有時仍然找這些檔名。
KEY_CANDIDATES = [
    "google_service_account.json",
    "gsc_service_account.json",
    "service_account.json",
]

_ENV_KEYS = ("SEARCH_CONSOLE_SA_JSON", "GOOGLE_SERVICE_ACCOUNT_KEY")


def _dotenv_values(path):
    """最小的 .env 讀取器。不引入 python-dotenv,本檔在 CI 也要能跑。"""
    out = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                out[key.strip()] = value.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env_path():
    """本專案憑證檔的絕對路徑。由 __file__ 推導,與呼叫端的工作目錄無關。"""
    return os.path.join(_repo_root(), "devops", ".env")


#: 本專案會用到的憑證鍵名。load_env() 只讓這些鍵吃到環境變數的覆蓋,
#: 其餘 os.environ(PATH 之類)不會混進來。
ENV_KEYS = (
    "SEARCH_CONSOLE_SA_JSON",
    "GOOGLE_SERVICE_ACCOUNT_KEY",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ZONE_ID",
    "CLOUDFLARE_ACCOUNT_ID",
    "GEMINI_API_KEY",
)


def load_env(extra_keys=(), path=None):
    """devops/.env 的內容,環境變數覆蓋之。回傳 dict。

    2026-08-31 新增。devops/Tools/ 的三支工具(site_metrics、test_gsc_matrix、
    seo_topic_injector)原本各有一份私有的 load_env(),只讀檔案、從不查
    os.environ,而且檔案不在就 raise。在 CI 裡憑證是環境變數、根本沒有 .env,
    於是那三支會把「憑證明明有」報成「未配置」——與本模組開頭記的是同一種錯:
    判準停在載體(檔案),而不是問憑證本身。

    順序與 load_service_account_info() 一致:環境變數優先於檔案。兩者都沒有時
    回傳空 dict,由呼叫端決定怎麼失敗——本函式不猜測缺哪一把才算致命。

    extra_keys 供仍在用專案後綴鍵名(CLOUDFLARE_API_TOKEN_CKM 之類)的呼叫端補充;
    path 供已有自訂 .env 位置參數的呼叫端沿用,預設就是本專案的 devops/.env。
    """
    values = _dotenv_values(path or env_path())
    for key in tuple(ENV_KEYS) + tuple(extra_keys):
        raw = os.environ.get(key)
        if raw:
            # 與 verify_credentials.yml 同樣的正規化:貼進 secret 時帶到的
            # 換行或引號會讓 header 變成非法值,在送出請求之前就爆掉。
            values[key] = raw.strip().strip('"').strip("'").strip()
    return values


def load_service_account_info():
    """回傳 (info_dict, source_label)。找不到任何來源時 sys.exit。"""
    for key in _ENV_KEYS:
        raw = os.environ.get(key)
        if raw:
            try:
                return json.loads(raw), f"環境變數 {key}"
            except json.JSONDecodeError:
                # 值可能是一個路徑而不是 JSON 本體。
                if os.path.exists(raw):
                    with open(raw, encoding="utf-8") as handle:
                        return json.load(handle), f"環境變數 {key} 指向的檔案 {raw}"
                sys.exit(f"環境變數 {key} 既不是合法 JSON 也不是存在的路徑。")

    env_file = os.path.join(_repo_root(), "devops", ".env")
    for key in _ENV_KEYS:
        raw = _dotenv_values(env_file).get(key)
        if raw:
            try:
                return json.loads(raw), f"devops/.env 的 {key}"
            except json.JSONDecodeError:
                sys.exit(f"devops/.env 的 {key} 不是合法 JSON。")

    for candidate in KEY_CANDIDATES:
        if os.path.exists(candidate):
            with open(candidate, encoding="utf-8") as handle:
                return json.load(handle), f"檔案 {candidate}"

    sys.exit(
        "找不到 Search Console 服務帳號憑證。依序找過:"
        f"環境變數 {', '.join(_ENV_KEYS)}、devops/.env、"
        f"檔案 {', '.join(KEY_CANDIDATES)}。拒絕在無憑證的情況下輸出數字。"
    )


def get_access_token(scopes=None):
    """換一個 access token 回來。憑證是死的就在這裡失敗,不要讓它流到下游。"""
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account

    info, source = load_service_account_info()
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=list(scopes or SCOPES_READONLY)
    )
    try:
        creds.refresh(Request())
    except Exception as exc:  # google.auth 會包裝底層錯誤,型別不穩定
        sys.exit(
            f"憑證來源【{source}】無法換取 token:{exc}\n"
            f"服務帳號 {info.get('client_email')} 的金鑰 "
            f"{(info.get('private_key_id') or '?')[:12]} 可能已被輪替或撤銷。"
        )
    return creds.token, source


if __name__ == "__main__":
    token, source = get_access_token()
    print(f"OK — 來源:{source},已成功換取 token(長度 {len(token)})")

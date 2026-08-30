"""四個專案的 Cloudflare 邊緣流量、RUM 真實訪客、WAF 安全威脅日誌與 Search Console 表現。

功能總覽:
--------
1. [HTTP 邊緣流量] : 總請求數、頁面瀏覽數 (PV)、獨立來源 IP (Uniques)、頻寬吞吐。
2. [RUM 真實訪客]  : 100% 零 Cookie 隱私分析 (Cloudflare Web Analytics)，真實訪客人數、手機/電腦比例、讀者熱門路徑。
3. [WAF 安全威脅]  : 每日惡意攻擊攔截量、最近 24 小時 403 阻擋路徑、Managed Challenge 機器人質詢日誌與攻擊來源國家。
4. [Search Console] : Google 搜尋關鍵字排名、點擊數、曝光量與品牌詞社群歸因分析。

用法範例:
--------
    python Tools/site_metrics.py                           # 4 專案全方位盤點 (7 天)
    python Tools/site_metrics.py --project TWProbe         # 單一專案
    python Tools/site_metrics.py --project TWProbe --waf   # 專注檢視 WAF 攻擊防禦日誌
    python Tools/site_metrics.py --days 3                  # 指定最近 3 天
    python Tools/site_metrics.py --brand-attribution       # 包含品牌搜尋詞歸因
    python Tools/site_metrics.py --json                    # 輸出 JSON 給 agent 讀
    python Tools/site_metrics.py --strict                  # 任何一個專案失敗就 exit 1
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

# 2026-08-30 自 DevOps hub 遷入。原本這裡登記四個專案,已裁到只剩本專案——
# 四個 repo 各留一份完整清單會讓別人的網域與設定散佈到不需要它的地方,
# 而且下一個人讀到會以為這支工具還在管四個專案。
PROJECTS = {
    'CKM': {'domain': 'ckmkh.com', 'suffix': 'CKM', 'brand_terms': ['ckm', '金邊外燴', '金邊頂級外燴', 'ម្ហូបការ']},
}

GSC_ROW_LIMIT = 50

# 本檔在 devops/Tools/,憑證載入的單一真本在 devops/。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sa_credentials import load_env as shared_load_env  # noqa: E402

#: 下面的查詢仍支援專案後綴鍵名(CLOUDFLARE_API_TOKEN_CKM),所以環境變數覆蓋也要涵蓋它們。
SUFFIXED_ENV_KEYS = tuple(
    f"{base}_{proj['suffix']}"
    for proj in PROJECTS.values()
    for base in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ZONE_ID",
                 "CLOUDFLARE_ACCOUNT_ID", "GOOGLE_SERVICE_ACCOUNT_KEY")
)


def load_env(path=ENV_PATH):
    # 2026-08-31:改為委派 devops/sa_credentials.py 的 load_env()。原本這裡只讀檔案、
    # 從不查 os.environ,而且檔案不在就 raise——在 CI 裡憑證是環境變數而且沒有 .env,
    # 於是同一把有效憑證會被本工具報成「未配置」。環境變數優先於檔案,檔案來源不變。
    # fail-closed 保留:兩個來源都湊不出任何憑證時仍然 raise,不讓它跑出一份空報表。
    env = shared_load_env(extra_keys=SUFFIXED_ENV_KEYS, path=path)
    if not env:
        raise FileNotFoundError("環境變數與 .env 都沒有任何憑證:" + path)
    return env


# ------------------------------------------------------------------ 1. Cloudflare HTTP 邊緣流量
CF_QUERY = """query { viewer { zones(filter: {zoneTag: "%s"}) {
    httpRequests1dGroups(limit: %d, orderBy: [date_ASC], filter: {date_geq: "%s"}) {
      dimensions { date }
      sum { requests pageViews threats bytes }
      uniq { uniques }
    } } } }"""


def cf_traffic(token, zone_id, days):
    """查詢 Cloudflare 邊緣 HTTP 請求日序列與威脅統計。"""
    since = (date.today() - timedelta(days=days)).isoformat()
    body = json.dumps({"query": CF_QUERY % (zone_id, max(days, 1), since)}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql", data=body,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        payload = json.loads(urllib.request.urlopen(req, timeout=25).read())
    except urllib.error.HTTPError as e:
        return [], "HTTP %d:%s" % (e.code, e.read().decode("utf-8", "replace")[:160])
    except Exception as e:
        return [], "%s:%s" % (type(e).__name__, str(e)[:160])

    if payload.get("errors"):
        return [], payload["errors"][0].get("message", "未知的 GraphQL 錯誤")[:200]

    zones = (payload.get("data") or {}).get("viewer", {}).get("zones") or []
    if not zones:
        return [], "GraphQL 回應沒有 zone;確認 token 對這個 zone 有 Analytics:Read"

    return [{
        "date": g["dimensions"]["date"],
        "requests": g["sum"]["requests"],
        "page_views": g["sum"]["pageViews"],
        "threats": g["sum"].get("threats", 0),
        "uniques": g["uniq"]["uniques"],
        "bytes": g["sum"]["bytes"],
    } for g in (zones[0].get("httpRequests1dGroups") or [])], None


# ------------------------------------------------------------------ 2. Cloudflare RUM 真實訪客
def cf_rum_analytics(token, account_id, days):
    """查詢 Cloudflare Web Analytics (RUM) 100% 零 Cookie 真實訪客與頁面活躍度。"""
    if not token or not account_id:
        return {}, None
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    query = """query {
      viewer {
        accounts(filter: {accountTag: "%s"}) {
          by_path: rumPageloadEventsAdaptiveGroups(
            limit: 8,
            filter: {datetime_geq: "%s"},
            orderBy: [count_DESC]
          ) {
            count
            sum { visits }
            dimensions { requestPath }
          }
          by_device: rumPageloadEventsAdaptiveGroups(
            limit: 5,
            filter: {datetime_geq: "%s"},
            orderBy: [count_DESC]
          ) {
            count
            sum { visits }
            dimensions { deviceType }
          }
          by_country: rumPageloadEventsAdaptiveGroups(
            limit: 6,
            filter: {datetime_geq: "%s"},
            orderBy: [count_DESC]
          ) {
            count
            sum { visits }
            dimensions { countryName }
          }
        }
      }
    }""" % (account_id, since, since, since)

    body = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql", data=body,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        payload = json.loads(urllib.request.urlopen(req, timeout=25).read())
        accs = (payload.get("data") or {}).get("viewer", {}).get("accounts") or []
        if not accs:
            return {}, None
        acc = accs[0]
        paths = [{
            "path": p.get("dimensions", {}).get("requestPath"),
            "views": p.get("count", 0),
            "visits": (p.get("sum") or {}).get("visits", 0)
        } for p in (acc.get("by_path") or [])]
        devices = [{
            "device": d.get("dimensions", {}).get("deviceType"),
            "views": d.get("count", 0),
            "visits": (d.get("sum") or {}).get("visits", 0)
        } for d in (acc.get("by_device") or [])]
        countries = [{
            "country": c.get("dimensions", {}).get("countryName"),
            "views": c.get("count", 0),
            "visits": (c.get("sum") or {}).get("visits", 0)
        } for c in (acc.get("by_country") or [])]
        total_visits = sum(d["visits"] for d in devices)
        total_views = sum(d["views"] for d in devices)
        return {
            "total_visits": total_visits,
            "total_views": total_views,
            "devices": devices,
            "paths": paths,
            "countries": countries
        }, None
    except Exception as e:
        return {}, str(e)


# ------------------------------------------------------------------ 3. Cloudflare WAF 安全威脅日誌
def cf_waf_security(token, zone_id):
    """查詢最近 24 小時被 403 阻擋的惡意探測、Challenge 質詢與攻擊來源國家。"""
    if not token or not zone_id:
        return {}, None
    since_23h = (datetime.now(timezone.utc) - timedelta(hours=23)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = """query {
      viewer {
        zones(filter: {zoneTag: "%s"}) {
          blocked_403: httpRequestsAdaptiveGroups(
            limit: 8,
            filter: {datetime_geq: "%s", edgeResponseStatus: 403},
            orderBy: [count_DESC]
          ) {
            count
            dimensions { clientRequestPath clientCountryName }
          }
          challenge_bots: httpRequestsAdaptiveGroups(
            limit: 6,
            filter: {datetime_geq: "%s", clientRequestPath_like: "%%challenge%%"},
            orderBy: [count_DESC]
          ) {
            count
            dimensions { clientRequestPath clientCountryName }
          }
        }
      }
    }""" % (zone_id, since_23h, since_23h)

    body = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql", data=body,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        payload = json.loads(urllib.request.urlopen(req, timeout=25).read())
        zones = (payload.get("data") or {}).get("viewer", {}).get("zones") or []
        if not zones:
            return {}, None
        z = zones[0]
        blocked = [{
            "path": b.get("dimensions", {}).get("clientRequestPath"),
            "country": b.get("dimensions", {}).get("clientCountryName"),
            "count": b.get("count", 0)
        } for b in (z.get("blocked_403") or [])]
        challenges = [{
            "path": ch.get("dimensions", {}).get("clientRequestPath"),
            "country": ch.get("dimensions", {}).get("clientCountryName"),
            "count": ch.get("count", 0)
        } for ch in (z.get("challenge_bots") or [])]
        return {
            "blocked_paths": blocked,
            "challenges": challenges,
            "total_blocked_sample": sum(b["count"] for b in blocked),
            "total_challenge_sample": sum(ch["count"] for ch in challenges)
        }, None
    except Exception as e:
        return {}, str(e)


# ------------------------------------------------------------------ 4. Google Search Console
def gsc_report(key_json, site_url, days, brand_terms=None):
    """查詢 Google Search Console 搜尋關鍵字表現與品牌詞社群歸因。"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        return {}, "缺少套件:%s(pip install google-api-python-client google-auth)" % e

    try:
        info = json.loads(key_json)
    except Exception as e:
        return {}, "服務帳號金鑰不是合法 JSON:%s" % e

    try:
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
        svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
        start = (date.today() - timedelta(days=days)).isoformat()
        end = (date.today() - timedelta(days=1)).isoformat()

        def run(dims):
            resp = svc.searchanalytics().query(siteUrl=site_url, body={
                "startDate": start, "endDate": end,
                "dimensions": dims, "rowLimit": GSC_ROW_LIMIT}).execute()
            return [{
                "key": r["keys"][0],
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "ctr": round(r.get("ctr", 0) * 100, 2),
                "position": round(r.get("position", 0), 1),
            } for r in resp.get("rows", [])]

        raw_queries = run(["query"])
        raw_pages = run(["page"])

        # 品牌詞拆解歸因
        brand_terms = brand_terms or []
        brand_q = []
        non_brand_q = []
        for q in raw_queries:
            q_lower = q["key"].lower()
            is_brand = any(t.lower() in q_lower for t in brand_terms)
            if is_brand:
                brand_q.append(q)
            else:
                non_brand_q.append(q)

        brand_imps = sum(q["impressions"] for q in brand_q)
        brand_clicks = sum(q["clicks"] for q in brand_q)
        non_brand_imps = sum(q["impressions"] for q in non_brand_q)
        non_brand_clicks = sum(q["clicks"] for q in non_brand_q)
        total_imps = brand_imps + non_brand_imps

        attribution = {
            "brand_terms": brand_terms,
            "brand_impressions": brand_imps,
            "brand_clicks": brand_clicks,
            "brand_ctr": round(brand_clicks / max(brand_imps, 1) * 100, 2),
            "brand_share_percent": round(brand_imps / max(total_imps, 1) * 100, 2),
            "non_brand_impressions": non_brand_imps,
            "non_brand_clicks": non_brand_clicks,
            "non_brand_ctr": round(non_brand_clicks / max(non_brand_imps, 1) * 100, 2),
            "brand_queries": brand_q,
            "non_brand_queries": non_brand_q
        }

        # SEO 打擊區機會詞 (Strike-Zone): 有曝光但排名在 2.0~20.0，最容易靠社群/論壇推進到前 3 名的黃金關鍵字
        strike_zone = [
            q for q in non_brand_q
            if q["impressions"] >= 2 and 2.0 <= q["position"] <= 20.0
        ]
        strike_zone.sort(key=lambda x: (x["impressions"], -x["position"]), reverse=True)

        return {
            "account": info.get("client_email"),
            "site": site_url,
            "period": start + " ~ " + end,
            "queries": raw_queries,
            "pages": raw_pages,
            "attribution": attribution,
            "strike_zone": strike_zone
        }, None
    except Exception as e:
        return {}, "%s:%s" % (type(e).__name__, str(e)[:200])


# ------------------------------------------------------------------ 5. 主採集與整合流程
def collect(names, days, env):
    out = {}
    for name in names:
        cfg = PROJECTS[name]
        s = cfg["suffix"]
        rec = {"project": name, "domain": cfg["domain"], "days": days, "errors": []}

        # 2026-08-30:加上無後綴回退。憑證拆到各專案自己的 devops/.env 之後,
        # 鍵名不再需要用專案名當後綴;保留後綴查詢是為了相容尚未遷移的環境。
        # seo_topic_injector.py 本來就是這個形狀,這裡補齊。
        token = env.get("CLOUDFLARE_API_TOKEN_" + s) or env.get("CLOUDFLARE_API_TOKEN")
        zone = env.get("CLOUDFLARE_ZONE_ID_" + s) or env.get("CLOUDFLARE_ZONE_ID")
        acc_id = env.get("CLOUDFLARE_ACCOUNT_ID_" + s) or env.get("CLOUDFLARE_ACCOUNT_ID")

        if token and zone:
            # 1. 邊緣流量
            series, err = cf_traffic(token, zone, days)
            if err:
                rec["errors"].append("Cloudflare:" + err)
            rec["cloudflare"] = {
                "series": series,
                "total_page_views": sum(d["page_views"] for d in series),
                "total_requests": sum(d["requests"] for d in series),
                "total_uniques": sum(d["uniques"] for d in series),
                "total_threats": sum(d.get("threats", 0) for d in series),
            }
            # 2. RUM 真實訪客
            if acc_id:
                rum_data, rum_err = cf_rum_analytics(token, acc_id, days)
                if rum_data:
                    rec["rum"] = rum_data

            # 3. WAF 安全防禦
            waf_data, waf_err = cf_waf_security(token, zone)
            if waf_data:
                rec["waf"] = waf_data
        else:
            rec["errors"].append(
                "Cloudflare:未設定 CLOUDFLARE_API_TOKEN_%s 或 CLOUDFLARE_ZONE_ID_%s" % (s, s))

        # 4. Search Console
        key = env.get("GOOGLE_SERVICE_ACCOUNT_KEY_" + s) or env.get("GOOGLE_SERVICE_ACCOUNT_KEY")
        if key:
            g, err = gsc_report(key, "sc-domain:" + cfg["domain"], days, brand_terms=cfg.get("brand_terms", []))
            if err:
                rec["errors"].append("GSC:" + err)
            rec["gsc"] = g
        else:
            rec["errors"].append("GSC:未設定 GOOGLE_SERVICE_ACCOUNT_KEY_" + s)

        out[name] = rec
    return out


def render(data, show_attribution=False, show_waf=False):
    for name, rec in data.items():
        print("=" * 70)
        print("  %s — %s  (最近 %d 天完整維運儀表板)" % (name, rec["domain"], rec["days"]))
        print("=" * 70)

        # 1. RUM 真實訪客 (Web Analytics)
        rum = rec.get("rum")
        if rum and rum.get("total_visits", 0) > 0:
            print("\n[1. Web Analytics (RUM 零 Cookie 真實訪客)]")
            print("  • 真實讀者會話 (Visits): {:>5,} 位 ｜ 真實頁面載入: {:>5,} 次".format(
                rum["total_visits"], rum["total_views"]))
            dev_str = ", ".join([f"{d['device']}: {d['visits']}訪/{d['views']}載" for d in rum.get("devices", []) if d['visits'] > 0 or d['views'] > 0])
            if dev_str:
                print("  • 裝置分佈: " + dev_str)
            country_str = ", ".join([f"{c['country']}: {c['visits']}訪" for c in rum.get("countries", []) if c['visits'] > 0])
            if country_str:
                print("  • 讀者地區: " + country_str)
            if rum.get("paths"):
                print("  • 真實讀者最常閱讀頁面 (Top Active Paths):")
                for p in rum["paths"][:5]:
                    print("    {:>4} 訪客 / {:>4} 載入  {}".format(p["visits"], p["views"], p["path"] or "/"))

        # 2. Cloudflare 邊緣 HTTP 總吞吐
        cf = rec.get("cloudflare") or {}
        if cf.get("series"):
            threat_pct = (cf.get("total_threats", 0) / max(cf["total_requests"], 1)) * 100
            print("\n[2. Cloudflare 網路邊緣總吞吐 (Edge Requests)]")
            print("  • 總請求數: {:,} ｜ 頁面瀏覽 (PV): {:,} ｜ 獨立來源 IP: {:,}".format(
                cf["total_requests"], cf["total_page_views"], cf["total_uniques"]))
            print("  • 安全狀態: 攔截惡意攻擊與威脅 {:,} 次 ({:.1f}%) ｜ 邊緣 100% 吸收".format(
                cf.get("total_threats", 0), threat_pct))
            for d in cf["series"][-4:]:
                print("    {} ｜ 請求 {:>7,} ｜ 瀏覽 {:>5,} ｜ 攔截威脅 {:>4,}".format(
                    d["date"], d["requests"], d["page_views"], d.get("threats", 0)))

        # 3. WAF 安全防禦與探測日誌
        waf = rec.get("waf")
        if waf and (show_waf or waf.get("total_blocked_sample", 0) > 0 or waf.get("total_challenge_sample", 0) > 0):
            print("\n[3. WAF 安全防禦與惡意掃描日誌 (最近 24 小時)]")
            if waf.get("blocked_paths"):
                print("  • 被 403 阻擋之惡意探測路徑 (Top Blocked Paths):")
                for b in waf["blocked_paths"][:5]:
                    print("    攔截 {:>5,} 次 [{}] ｜ {}".format(b["count"], b["country"] or "未知", b["path"]))
            if waf.get("challenges"):
                print("  • 觸發 Managed Challenge 人機質詢之機器人 (Bot Challenges):")
                for ch in waf["challenges"][:3]:
                    print("    質詢 {:>5,} 次 [{}] ｜ {}".format(ch["count"], ch["country"] or "未知", ch["path"]))

        # 4. Search Console 搜尋表現
        g = rec.get("gsc") or {}
        if g.get("queries"):
            print("\n[4. Google Search Console 搜尋引擎表現] %s" % (g["period"]))
            
            att = g.get("attribution") or {}
            if show_attribution or att.get("brand_impressions", 0) > 0:
                print("  [品牌詞歸因 (Brand Attribution)]")
                print("  • 品牌關鍵字曝光: {:>4} 次 ({:>5.1f}%) ｜ 點擊: {:>3} 次 ｜ CTR: {:>4.1f}%".format(
                    att.get("brand_impressions", 0), att.get("brand_share_percent", 0.0),
                    att.get("brand_clicks", 0), att.get("brand_ctr", 0.0)))
                print("  • 通用關鍵字曝光: {:>4} 次 ｜ 點擊: {:>3} 次 ｜ CTR: {:>4.1f}%".format(
                    att.get("non_brand_impressions", 0), att.get("non_brand_clicks", 0),
                    att.get("non_brand_ctr", 0.0)))
                if att.get("brand_queries"):
                    print("  • 捕獲品牌搜尋詞: " + ", ".join([f"{bq['key']} ({bq['impressions']}曝/{bq['clicks']}點)" for bq in att["brand_queries"][:4]]))

            print("\n  {:<30}{:>7}{:>6}{:>7}{:>7}".format("熱門搜尋詞", "曝光", "點擊", "CTR", "排名"))
            for q in g["queries"][:8]:
                print("  {:<30}{:>7}{:>6}{:>6.1f}%{:>7.1f}".format(
                    q["key"][:28], q["impressions"], q["clicks"], q["ctr"], q["position"]))

            # SEO 打擊區機會詞 (Strike Zone)
            sz = g.get("strike_zone") or []
            if sz:
                print("\n  🎯 [SEO 打擊區機會詞 (Strike-Zone)] —— 最適合選題衝 Google 前 3 名的黃金詞:")
                for s in sz[:5]:
                    print("    • {:<24} ｜ 曝光 {:>3} 次 ｜ 目前排名 {:>4.1f} ｜ 建議：寫 Threads/論壇回文即可攻頂".format(
                        s["key"][:22], s["impressions"], s["position"]))

            if g.get("pages"):
                print("\n  接到最多搜尋曝光的頁面:")
                for p in g["pages"][:4]:
                    print("    {:>6} 曝光 / {:>3} 點擊  {}".format(
                        p["impressions"], p["clicks"], p["key"][:64]))

        for e in rec["errors"]:
            print("\n  [連線提示] " + e)
        print()


def main():
    ap = argparse.ArgumentParser(description="DevOps 4 專案統一維運監控與流量安全儀表板")
    ap.add_argument("--project", choices=sorted(PROJECTS), action="append", help="指定查詢特定專案 (可多次指定)")
    ap.add_argument("--days", type=int, default=7, help="查詢天數 (預設 7 天)")
    ap.add_argument("--waf", "--security", dest="waf", action="store_true", help="強制顯示 WAF 威脅與惡意探測日誌")
    ap.add_argument("--brand-attribution", action="store_true", help="強制顯示品牌搜尋詞社群歸因分析")
    ap.add_argument("--strike-zone", "--seo", dest="strike_zone", action="store_true", help="強制顯示 SEO 打擊區機會詞")
    ap.add_argument("--json", action="store_true", help="輸出 JSON 格式")
    ap.add_argument("--strict", action="store_true", help="任何專案查詢失敗就 exit 1")
    args = ap.parse_args()

    env = load_env()
    names = args.project or list(PROJECTS)
    data = collect(names, args.days, env)

    if args.json:
        print(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
                          "projects": data}, ensure_ascii=False, indent=2))
    else:
        render(data, show_attribution=args.brand_attribution, show_waf=args.waf)

    failed = [n for n, r in data.items() if r["errors"]]
    if failed and args.strict:
        print("[STRICT] %d 個專案有連線錯誤:%s" % (len(failed), "、".join(failed)), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

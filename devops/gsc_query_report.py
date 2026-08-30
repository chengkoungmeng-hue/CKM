"""Pull live Google Search Console search-analytics data for ckmkh.com.

No fallbacks, no synthetic numbers: if the API call fails the script exits non-zero
so a caller can never mistake a placeholder for a measurement.

Usage:
    python devops/gsc_query_report.py [--days 90] [--end YYYY-MM-DD]

Writes devops/reports/gsc_search_queries.json and prints a console summary.
"""

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

SITE = "sc-domain:ckmkh.com"
ENDPOINT = (
    "https://www.googleapis.com/webmasters/v3/sites/"
    "sc-domain%3Ackmkh.com/searchAnalytics/query"
)
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# 2026-08-30:憑證載入移到 devops/sa_credentials.py。原本這裡的判準是「檔案存不存在」,
# 而本機 google_service_account.json 裡是一把已輪替掉的死金鑰,於是本檔與
# check_pulse_indexation.py、notify_indexing.py 三支一起靜默失效——GSC 回不了資料,
# 看起來卻像「這段期間沒有曝光」。新的載入器環境變數優先於檔案,而且回傳前會真的
# 換一次 token,死憑證在那裡就會停下來。
#
# KEY_CANDIDATES 保留為 re-export,因為 check_pulse_indexation.py 從本模組 import 它。
from sa_credentials import KEY_CANDIDATES, get_access_token  # noqa: E402


#: 最近一次 get_token() 實際用到的憑證來源,供摘要行顯示。
#: 這一行是刻意的:三支腳本原本印出「Key: <檔名>」,讓人以為憑證來自那個檔,
#: 而真正生效的可能是環境變數。印來源而不是印檔名,看到的才是實際發生的事。
CREDENTIAL_SOURCE = "(尚未取得)"


def get_token():
    """回傳可用的 access token。憑證是死的會在 sa_credentials 內以非零結束。"""
    global CREDENTIAL_SOURCE
    token, CREDENTIAL_SOURCE = get_access_token(SCOPES)
    return token


def query(token, body):
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8")).get("rows", [])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        sys.exit(f"GSC API {exc.code} for body={json.dumps(body)}\n{detail}")


def rows_to_records(rows, dim_names):
    out = []
    for row in rows:
        rec = dict(zip(dim_names, row.get("keys", [])))
        rec.update(
            clicks=row.get("clicks", 0),
            impressions=row.get("impressions", 0),
            ctr=round(row.get("ctr", 0) * 100, 2),
            position=round(row.get("position", 0), 2),
        )
        out.append(rec)
    return out


def fetch(token, start, end, dimensions=None, filters=None, row_limit=1000):
    body = {"startDate": start, "endDate": end, "rowLimit": row_limit, "dataState": "all"}
    if dimensions:
        body["dimensions"] = dimensions
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    return rows_to_records(query(token, body), dimensions or [])


def table(records, cols, widths, limit=None):
    if not records:
        return "  (no rows)"
    lines = ["  " + "  ".join(c.ljust(w) for c, w in zip(cols, widths))]
    lines.append("  " + "  ".join("-" * w for w in widths))
    for rec in records[:limit]:
        cells = []
        for col, width in zip(cols, widths):
            val = rec.get(col, "")
            text = str(val)
            if len(text) > width:
                text = text[: width - 1] + "…"
            cells.append(text.ljust(width))
        lines.append("  " + "  ".join(cells))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--end", default=None, help="End date YYYY-MM-DD (default: today-2)")
    args = parser.parse_args()

    end = (
        datetime.date.fromisoformat(args.end)
        if args.end
        else datetime.date.today() - datetime.timedelta(days=2)
    )
    start = end - datetime.timedelta(days=args.days - 1)
    s, e = start.isoformat(), end.isoformat()

    token = get_token()
    print(f"Site: {SITE}   Window: {s} → {e} ({args.days} days)   Key: {CREDENTIAL_SOURCE}\n")

    kh_filter = [{"dimension": "country", "operator": "equals", "expression": "khm"}]

    data = {
        "meta": {
            "site": SITE,
            "start_date": s,
            "end_date": e,
            "days": args.days,
            "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "source": "Google Search Console Search Analytics API (live)",
        },
        "totals": fetch(token, s, e, None, None, 1),
        "by_country": fetch(token, s, e, ["country"], None, 50),
        "by_device": fetch(token, s, e, ["device"], None, 10),
        "queries_all": fetch(token, s, e, ["query"], None, 1000),
        "queries_cambodia": fetch(token, s, e, ["query"], kh_filter, 1000),
        "pages_all": fetch(token, s, e, ["page"], None, 1000),
        "pages_cambodia": fetch(token, s, e, ["page"], kh_filter, 1000),
        "query_page_cambodia": fetch(token, s, e, ["query", "page"], kh_filter, 1000),
        "by_month": fetch(token, s, e, ["date"], None, 500),
    }

    for rec in data["pages_all"] + data["pages_cambodia"] + data["query_page_cambodia"]:
        if "page" in rec:
            rec["path"] = rec["page"].replace("https://ckmkh.com", "") or "/"

    out_path = os.path.join("devops", "reports", "gsc_search_queries.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)

    tot = data["totals"][0] if data["totals"] else {}
    print("TOTALS")
    print(
        f"  clicks={tot.get('clicks', 0)}  impressions={tot.get('impressions', 0)}  "
        f"ctr={tot.get('ctr', 0)}%  avg_position={tot.get('position', 0)}\n"
    )

    print(f"COUNTRIES ({len(data['by_country'])} rows)")
    print(table(data["by_country"], ["country", "clicks", "impressions", "ctr", "position"],
                [10, 7, 12, 7, 9], 12))
    print()

    print(f"DEVICES")
    print(table(data["by_device"], ["device", "clicks", "impressions", "ctr", "position"],
                [10, 7, 12, 7, 9]))
    print()

    print(f"TOP QUERIES — ALL COUNTRIES ({len(data['queries_all'])} rows)")
    print(table(data["queries_all"], ["query", "clicks", "impressions", "ctr", "position"],
                [44, 7, 12, 7, 9], 40))
    print()

    print(f"TOP QUERIES — CAMBODIA ONLY ({len(data['queries_cambodia'])} rows)")
    print(table(data["queries_cambodia"], ["query", "clicks", "impressions", "ctr", "position"],
                [44, 7, 12, 7, 9], 40))
    print()

    print(f"TOP PAGES — ALL COUNTRIES ({len(data['pages_all'])} rows)")
    print(table(data["pages_all"], ["path", "clicks", "impressions", "ctr", "position"],
                [52, 7, 12, 7, 9], 30))
    print()

    print(f"TOP PAGES — CAMBODIA ONLY ({len(data['pages_cambodia'])} rows)")
    print(table(data["pages_cambodia"], ["path", "clicks", "impressions", "ctr", "position"],
                [52, 7, 12, 7, 9], 30))
    print()

    print(f"\nSaved raw data to {out_path}")


if __name__ == "__main__":
    main()

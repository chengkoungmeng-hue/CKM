"""Did a published pulse page ever earn a Search Console impression?

The pipeline submits a sitemap and stops. Nothing downstream ever asks whether the
page that was submitted went on to be seen by anybody, which is how 36 pulse entries
accumulated while producing two impressions in Cambodia in ninety days without anyone
noticing. Publication is measured; being read is not. This closes that gap.

For every entry in src/data/pulseData.json older than --min-age-days, this reports the
impressions, clicks and best position the page earned since it went live, and counts how
many earned nothing at all.

No fallbacks and no synthetic numbers. Section 18 of .agents/AGENTS.md records a deleted
script that degraded to hardcoded totals indistinguishable from live output; a zero
printed by this script must always mean "the API said zero", never "the API was not
reachable". Missing credentials or an API error exit non-zero BEFORE any table is
printed. Auth and the HTTP call are imported from gsc_query_report.py rather than
reimplemented -- one client, one failure mode.

This is a reporting tool. It never blocks a publish (section 15), so it belongs in the
dispatch-only measurement workflow and NOT in the daily publishing workflow. It exits 0
on a successful measurement whatever the numbers say; only an inability to measure is a
failure.

Usage:
    python devops/check_pulse_indexation.py [--min-age-days 7] [--days 480]
                                            [--end YYYY-MM-DD]

Writes devops/reports/pulse_indexation.json and prints a console summary.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Auth, the HTTP call and the console table come from the query report; parse_any_date
# from the pulse generator. One date parser and one API client, not copies of each.
import gsc_query_report
from gsc_query_report import SITE, get_token, query, table
from fetch_catering_pulse import parse_any_date

DATA_FILE = "src/data/pulseData.json"
BASE_URL = "https://ckmkh.com"
OUT_PATH = os.path.join("devops", "reports", "pulse_indexation.json")

# A page needs time to be crawled, indexed and shown before a zero means anything.
DEFAULT_MIN_AGE_DAYS = 7
# Search Console retains roughly 16 months. Asking for more is not an error, it just
# returns nothing for the part it no longer holds -- which is why a page older than the
# window is flagged rather than reported as "never seen".
DEFAULT_LOOKBACK_DAYS = 480
# GSC caps a single response; the loop pages until a short page comes back.
ROW_LIMIT = 25000

KH_FILTER = [{"dimension": "country", "operator": "equals", "expression": "khm"}]


def fetch_page_days(token, start, end, filters=None):
    """Every (page, date) row in the window, as {url: [row, ...]}.

    One paginated request set for the whole site rather than one request per URL: the
    per-entry windows are then just a local filter on the daily rows, and the same rows
    give totals and the best position without a second round trip.
    """
    by_url = {}
    start_row = 0
    while True:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": ["page", "date"],
            "rowLimit": ROW_LIMIT,
            "startRow": start_row,
            "dataState": "all",
        }
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]
        rows = query(token, body)          # sys.exit()s on any HTTP error
        for row in rows:
            keys = row.get("keys", [])
            if len(keys) != 2:
                continue
            url, date = keys
            by_url.setdefault(url, []).append(
                {
                    "date": date,
                    "clicks": row.get("clicks", 0),
                    "impressions": row.get("impressions", 0),
                    "position": row.get("position", 0),
                }
            )
        if len(rows) < ROW_LIMIT:
            return by_url
        start_row += len(rows)


def aggregate(by_url, urls, window_start):
    """Sum the daily rows for a set of equivalent URLs from window_start onwards.

    best position is the lowest daily average the page reached, not the window average:
    the question here is whether the page was ever shown at all, so the single best day
    is the more informative one. Days with zero impressions carry a meaningless position
    and are excluded from it.
    """
    impressions = clicks = 0
    best = None
    for url in urls:
        for row in by_url.get(url, []):
            if row["date"] < window_start:
                continue
            impressions += row["impressions"]
            clicks += row["clicks"]
            if row["impressions"] > 0:
                pos = row["position"]
                best = pos if best is None else min(best, pos)
    return impressions, clicks, best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-age-days", type=int, default=DEFAULT_MIN_AGE_DAYS,
                        help="Ignore entries younger than this (default 7)")
    parser.add_argument("--days", type=int, default=DEFAULT_LOOKBACK_DAYS,
                        help="Measurement window in days (default 480)")
    parser.add_argument("--end", default=None, help="End date YYYY-MM-DD (default: today-2)")
    args = parser.parse_args()

    if not os.path.exists(DATA_FILE):
        print(f"::error::{DATA_FILE} is missing entirely.")
        return 1
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        entries = json.load(fh)
    if not entries:
        print(f"::error::{DATA_FILE} contains no entries.")
        return 1

    # Fail on the credential BEFORE anything prints a number, so an unauthenticated run
    # can never be mistaken for a measured zero.
    # 2026-08-30:原本這裡先檢查「憑證檔存不存在」再往下跑。那個判準擋不住真正的
    # 失敗模式——檔案在、但金鑰已被輪替——所以改由 sa_credentials 在換 token 時失敗。
    # 保留「未取得憑證就不印數字」這個意圖:get_token() 失敗會直接以非零結束。

    end = (
        datetime.date.fromisoformat(args.end)
        if args.end
        else datetime.date.today() - datetime.timedelta(days=2)
    )
    start = end - datetime.timedelta(days=args.days - 1)
    s, e = start.isoformat(), end.isoformat()

    try:
        token = get_token()
    except Exception as exc:                      # noqa: BLE001 - the reason varies
        print(f"::error::Could not obtain a Search Console token from "
              f"{gsc_query_report.CREDENTIAL_SOURCE}: "
              f"{type(exc).__name__}: {exc}")
        return 2

    print(f"Site: {SITE}   Window: {s} -> {e} ({args.days} days)   Key: {gsc_query_report.CREDENTIAL_SOURCE}")
    print(f"Entries: {len(entries)}   Reporting those live at least "
          f"{args.min_age_days} days\n")

    all_rows = fetch_page_days(token, s, e)
    kh_rows = fetch_page_days(token, s, e, KH_FILTER)

    today = datetime.datetime.now(datetime.timezone.utc)
    records, skipped, clipped = [], [], 0

    for entry in entries:
        slug = entry.get("slug")
        pulse_id = entry.get("id")
        if not slug:
            continue
        # The canonical URL is the slug path; /pulse/<id>/ 301s to it (section 3) but was
        # a live page historically and still appears in Search Console, so both are
        # counted. Dropping the alias would report a page that earned an impression as
        # having earned none.
        urls = [f"{BASE_URL}/pulse/{slug}/"]
        if pulse_id and pulse_id != slug:
            urls.append(f"{BASE_URL}/pulse/{pulse_id}/")

        # added_at is when the page reached this site. pub_date is the source blog's own
        # date and can be years earlier, so it is never used as a proxy here. Entries
        # written before added_at existed (pulse-01..27) have no live date at all; they
        # all predate the field, so they are old enough to report, and their age prints
        # as "?" rather than as a number nobody measured.
        raw_added = entry.get("added_at")
        added = parse_any_date(raw_added) if raw_added else None
        if added is not None and added.year < 2000:
            added = None

        if added is not None:
            days_live = (today - added).total_seconds() / 86400.0
            if days_live < args.min_age_days:
                skipped.append(f"{slug} ({days_live:.1f}d)")
                continue
            window_start = max(added.date().isoformat(), s)
            # True when the page is older than the window, so a zero covers only part
            # of its life.
            partial = added.date().isoformat() < s
            days_cell = f"{days_live:.0f}"
        else:
            days_live = None
            window_start = s
            partial = True                 # no live date, so the coverage is unknown
            days_cell = "?"
        if partial:
            clipped += 1

        impressions, clicks, best = aggregate(all_rows, urls, window_start)
        kh_impressions, kh_clicks, _ = aggregate(kh_rows, urls, window_start)

        records.append(
            {
                "id": pulse_id,
                "slug": slug,
                "url": urls[0],
                "days_live": round(days_live, 1) if days_live is not None else None,
                "days": days_cell,
                "window_start": window_start,
                "window_end": e,
                "window_clipped": partial,
                "impressions": impressions,
                "clicks": clicks,
                "best_pos": round(best, 1) if best is not None else "-",
                "kh_impr": kh_impressions,
                "kh_clicks": kh_clicks,
            }
        )

    # Worst first: the pages that earned nothing are the finding, so they lead.
    records.sort(key=lambda r: (r["impressions"], r["kh_impr"], r["slug"]))

    cols = ["slug", "days", "impressions", "clicks", "best_pos", "kh_impr"]
    widths = [46, 5, 11, 6, 8, 7]
    print(f"PULSE PAGES ({len(records)} reported, {len(skipped)} too new)")
    print(table(records, cols, widths))
    print()

    reported = len(records)
    zero = sum(1 for r in records if r["impressions"] == 0)
    kh_zero = sum(1 for r in records if r["kh_impr"] == 0)
    total_impr = sum(r["impressions"] for r in records)
    total_clicks = sum(r["clicks"] for r in records)
    kh_impr = sum(r["kh_impr"] for r in records)
    kh_clicks = sum(r["kh_clicks"] for r in records)

    summary_lines = [
        "### Pulse indexation",
        "",
        f"Window `{s}` to `{e}`, measured from each page's own live date.",
        "",
        "| check | value |",
        "| :--- | :--- |",
        f"| entries in dataset | {len(entries)} |",
        f"| reported (live >= {args.min_age_days} days) | {reported} |",
        f"| too new to judge | {len(skipped)} |",
        f"| **zero impressions, all countries** | **{zero} of {reported}** |",
        f"| zero impressions, Cambodia | {kh_zero} of {reported} |",
        f"| total impressions | {total_impr} |",
        f"| total clicks | {total_clicks} |",
        f"| Cambodia impressions | {kh_impr} |",
        f"| Cambodia clicks | {kh_clicks} |",
    ]
    if clipped:
        summary_lines.append(
            f"| older than the window, or live date unknown | {clipped} |"
        )
    summary = "\n".join(summary_lines)
    print(summary)
    if clipped:
        print(f"\nNote: {clipped} page(s) are older than the measurement window or carry "
              f"no added_at, so a zero there means 'nothing in this window', not 'never'.")
    if skipped:
        print(f"Too new to judge: {', '.join(skipped)}")

    step_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write(summary + "\n")

    payload = {
        "meta": {
            "site": SITE,
            "start_date": s,
            "end_date": e,
            "days": args.days,
            "min_age_days": args.min_age_days,
            "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "source": "Google Search Console Search Analytics API (live)",
        },
        "summary": {
            "entries": len(entries),
            "reported": reported,
            "too_new": len(skipped),
            "zero_impressions": zero,
            "zero_impressions_cambodia": kh_zero,
            "impressions": total_impr,
            "clicks": total_clicks,
            "impressions_cambodia": kh_impr,
            "clicks_cambodia": kh_clicks,
            "window_clipped_or_undated": clipped,
        },
        "pages": records,
        "too_new": skipped,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\nSaved raw data to {OUT_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

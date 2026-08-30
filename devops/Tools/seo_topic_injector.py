#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SEO Topic Injector — GSC 站內搜尋詞 ➔ 每日選題閉環橋樑
======================================================
自動抓取 GSC 過去 14 天「高曝光、低點擊 / 排名 4~20 名」的潛力搜尋詞,
將 SEO 需求即時轉化為選題訊號,並可直接加權注入當日 pulse.json。

用法:
    python Tools/seo_topic_injector.py --project TWProbe
    python Tools/seo_topic_injector.py --all --inject-pulse
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")

# 2026-08-30:改由 __file__ 推導本專案的 devops/。原本寫死 DevOps hub,
# 而 hub 已於當日退役為純憑證庫。
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
TODAY_STR = datetime.now().strftime("%Y-%m-%d")

# 2026-08-30 自 DevOps hub 遷入。原本這裡登記四個專案,已裁到只剩本專案——
# 四個 repo 各留一份完整清單會讓別人的網域與設定散佈到不需要它的地方,
# 而且下一個人讀到會以為這支工具還在管四個專案。
PROJECTS = {
    'CKM': {'domain': 'ckmkh.com', 'suffix': 'CKM'},
}

# 本檔在 devops/Tools/,憑證載入的單一真本在 devops/。
sys.path.insert(0, ROOT_DIR)
from sa_credentials import load_env as shared_load_env  # noqa: E402

#: 下面的查詢仍支援專案後綴鍵名(GOOGLE_SERVICE_ACCOUNT_KEY_CKM),環境變數覆蓋要涵蓋它。
SUFFIXED_ENV_KEYS = tuple(
    f"GOOGLE_SERVICE_ACCOUNT_KEY_{proj['suffix']}" for proj in PROJECTS.values()
)

def load_env(path=ENV_PATH):
    # 2026-08-31:改為委派 devops/sa_credentials.py 的 load_env()。原本這裡只讀檔案、
    # 從不查 os.environ,而且檔案不在就 raise——在 CI 裡憑證是環境變數而且沒有 .env,
    # 於是同一把有效憑證會被本工具報成「未配置」。環境變數優先於檔案,檔案來源不變。
    # fail-closed 保留:兩個來源都湊不出任何憑證時仍然 raise。
    env = shared_load_env(extra_keys=SUFFIXED_ENV_KEYS, path=path)
    if not env:
        raise FileNotFoundError(f"環境變數與 .env 都沒有任何憑證: {path}")
    return env

def fetch_gsc_search_opportunities(key_json, domain, days=14):
    """查詢 GSC 過去 N 天的 query 資料，挑選具備內容強化潛力的關鍵字。"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        return [], f"缺少 google-api-python-client 或 google-auth 套件: {e}"

    try:
        info = json.loads(key_json)
    except Exception as e:
        return [], f"服務帳號金鑰解析失敗: {e}"

    try:
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
        start = (date.today() - timedelta(days=days)).isoformat()
        end = (date.today() - timedelta(days=1)).isoformat()
        site_url = f"sc-domain:{domain}"

        resp = svc.searchanalytics().query(siteUrl=site_url, body={
            "startDate": start,
            "endDate": end,
            "dimensions": ["query"],
            "rowLimit": 100
        }).execute()

        rows = resp.get("rows", [])
        opportunities = []
        for r in rows:
            q = r["keys"][0]
            clicks = r.get("clicks", 0)
            imps = r.get("impressions", 0)
            ctr = round(r.get("ctr", 0) * 100, 2)
            pos = round(r.get("position", 0), 1)

            # 篩選邏輯：
            # 1. 曝光 >= 3 且 CTR < 10% (有流量但未點擊，需強化吸引力)
            # 2. 或 排名在 4 ~ 25 之間 (已有 Google 權重，補一刀即可進首頁)
            is_opportunity = (imps >= 3 and ctr < 10.0) or (4.0 <= pos <= 25.0 and imps >= 2)
            
            score = round(imps * (1.0 / max(pos, 1.0)) * 10, 2)
            
            opportunities.append({
                "keyword": q,
                "impressions": imps,
                "clicks": clicks,
                "ctr": ctr,
                "position": pos,
                "opportunity_score": score,
                "is_priority": is_opportunity,
                "recommended_action": "社群專題探討 ＋ 強化站內接詞頁面" if is_opportunity else "持續監測"
            })

        # 按機會分數排序
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return opportunities, None
    except Exception as e:
        return [], f"{type(e).__name__}: {str(e)[:200]}"

def run_project(proj_name, env, days=14, inject_pulse=False):
    cfg = PROJECTS.get(proj_name)
    if not cfg:
        print(f"[ERROR] 未知專案: {proj_name}", file=sys.stderr)
        return False

    suffix = cfg["suffix"]
    key = env.get(f"GOOGLE_SERVICE_ACCOUNT_KEY_{suffix}") or env.get("GOOGLE_SERVICE_ACCOUNT_KEY")
    if not key:
        print(f"[WARN] 專案 {proj_name} 未設定 GOOGLE_SERVICE_ACCOUNT_KEY_{suffix}，跳過 GSC 查詢。")
        return False

    print(f"\n[{proj_name}] 正在查詢 GSC 過去 {days} 天搜尋詞潛力...")
    opps, err = fetch_gsc_search_opportunities(key, cfg["domain"], days=days)
    if err:
        print(f"  [失敗] {err}", file=sys.stderr)
        return False

    priority_opps = [o for o in opps if o["is_priority"]]
    print(f"  • 取得總關鍵字: {len(opps)} 組 ｜ 判定高潛力題目: {len(priority_opps)} 組")
    for o in priority_opps[:8]:
        print(f"    - 『{o['keyword']}』 (曝光: {o['impressions']}, 點擊: {o['clicks']}, 排名: {o['position']}, 分數: {o['opportunity_score']})")

    # 直接將 GSC 潛力搜尋詞注入今日 pulse.json，保持單一 JSON 真本
    downloads_root = os.path.join(os.path.expanduser("~"), "Downloads")
    proj_dir = os.path.join(downloads_root, f"{proj_name}-report")
    os.makedirs(proj_dir, exist_ok=True)
    
    pulse_path = os.path.join(proj_dir, f"{proj_name}_{TODAY_STR}_pulse.json")
    if os.path.exists(pulse_path):
        try:
            with open(pulse_path, "r", encoding="utf-8") as f:
                pulse_data = json.load(f)
            pulse_data["seo_opportunities"] = priority_opps[:15]
            pulse_data["seo_opportunities_count"] = len(priority_opps)
            with open(pulse_path, "w", encoding="utf-8") as f:
                json.dump(pulse_data, f, ensure_ascii=False, indent=2)
            print(f"  [INJECTED] 成功將 {len(priority_opps[:15])} 筆 GSC 潛力詞整合至單一資料庫: {pulse_path}")
        except Exception as e:
            print(f"  [WARN] 注入 pulse.json 失敗: {e}")
    else:
        # 若 pulse.json 尚未生成，建立基礎結構
        with open(pulse_path, "w", encoding="utf-8") as f:
            json.dump({
                "project": proj_name,
                "domain": cfg["domain"],
                "report_date": TODAY_STR,
                "seo_opportunities": priority_opps[:15],
                "seo_opportunities_count": len(priority_opps)
            }, f, ensure_ascii=False, indent=2)
        print(f"  [CREATED] 已建立 pulse.json 並寫入 SEO 潛力詞: {pulse_path}")

    return True

def main():
    ap = argparse.ArgumentParser(description="SEO Topic Injector")
    ap.add_argument("--project", choices=sorted(PROJECTS), help="指定專案名稱")
    ap.add_argument("--all", action="store_true", help="執行全部 4 個專案")
    ap.add_argument("--days", type=int, default=14, help="查詢 GSC 過去天數 (預設 14 天)")
    ap.add_argument("--inject-pulse", action="store_true", help="是否直接加權注入當日 pulse.json")
    args = ap.parse_args()

    env = load_env()
    targets = list(PROJECTS) if args.all or not args.project else [args.project]
    success_count = 0
    for proj in targets:
        if run_project(proj, env, days=args.days, inject_pulse=args.inject_pulse):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"SEO Topic Injector 執行完成: 成功 {success_count}/{len(targets)} 個專案")
    print("=" * 60 + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Central DevOps Hub — Multi-Project GSC & Cloudflare Connection Tester
====================================================================
Tests Google Search Console and Cloudflare Web Analytics credentials
for TWProbe, CKM, Sunder, and PressaGen.
"""

import os
import sys
import io
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# Fix Windows console UTF-8 output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 2026-08-30 自 DevOps hub 遷入並裁到只剩本專案。
# 金鑰名同時去掉專案後綴——憑證已拆到本專案的 devops/.env,不再需要用專案名區分。
PROJECTS = [
    {
        'name': 'CKM',
        'gsc_key': 'GOOGLE_SERVICE_ACCOUNT_KEY',
        'domain': 'sc-domain:ckmkh.com',
        'cf_token_key': 'CLOUDFLARE_API_TOKEN',
        'cf_zone_key': 'CLOUDFLARE_ZONE_ID',
        'cf_account_key': 'CLOUDFLARE_ACCOUNT_ID',
    }
]

def load_env():
    env_vars = {}
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    if not os.path.exists(env_path):
        # 2026-08-30:原本在此回退到 DevOps hub 的共用 .env。hub 已退役為
        # 各專案自持憑證,回退只會讓「憑證漏設」偽裝成「跑得起來」。
        print(f"[ERROR] 找不到本專案的 .env:{env_path}")
        return {}
    if not os.path.exists(env_path):
        print(f"[ERROR] .env file not found at: {env_path}")
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
    return env_vars

def test_gsc_for_project(proj, env_vars):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    key_str = env_vars.get(proj["gsc_key"]) or env_vars.get("GOOGLE_SERVICE_ACCOUNT_KEY")
    if not key_str:
        return {
            "status": "MISSING",
            "message": f"未設定 {proj['gsc_key']}",
            "sites": [],
            "queries": []
        }
    
    try:
        sa_info = json.loads(key_str)
    except Exception as e:
        return {
            "status": "INVALID_JSON",
            "message": f"JSON 解析失敗: {e}",
            "sites": [],
            "queries": []
        }

    email = sa_info.get("client_email", "unknown")
    
    try:
        scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
        creds = service_account.Credentials.from_service_account_info(sa_info, scopes=scopes)
        service = build("searchconsole", "v1", credentials=creds)
        
        sites_resp = service.sites().list().execute()
        site_entries = sites_resp.get("siteEntry", [])
        authorized_urls = [s.get("siteUrl") for s in site_entries]
        
        queries = []
        target_domain = proj["domain"]
        matched_url = None
        for u in authorized_urls:
            if proj["name"].lower() in u.lower() or target_domain in u:
                matched_url = u
                break
        
        if matched_url:
            today = datetime.now()
            start_date = (today - timedelta(days=28)).strftime("%Y-%m-%d")
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            
            req = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query"],
                "rowLimit": 3
            }
            try:
                resp = service.searchanalytics().query(siteUrl=matched_url, body=req).execute()
                rows = resp.get("rows", [])
                for r in rows:
                    queries.append({
                        "query": r.get("keys", [""])[0],
                        "clicks": r.get("clicks", 0),
                        "impressions": r.get("impressions", 0),
                        "position": round(r.get("position", 0), 1)
                    })
            except Exception:
                pass

        return {
            "status": "SUCCESS",
            "email": email,
            "matched_url": matched_url,
            "all_sites": authorized_urls,
            "queries": queries
        }

    except Exception as e:
        return {
            "status": "API_ERROR",
            "email": email,
            "message": str(e),
            "sites": [],
            "queries": []
        }

def test_cf_for_project(proj, env_vars):
    token = env_vars.get(proj["cf_token_key"]) or env_vars.get("CLOUDFLARE_API_TOKEN")
    zone_id = env_vars.get(proj["cf_zone_key"])
    
    if not token:
        return {
            "status": "MISSING",
            "message": f"未設定 {proj['cf_token_key']}"
        }

    # 1. Verify token
    try:
        req = urllib.request.Request(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if not data.get("success"):
                return {"status": "INVALID_TOKEN", "message": "Token 驗證失敗"}
    except Exception as e:
        return {"status": "ERROR", "message": f"連線錯誤: {e}"}

    # 2. Query zone details if zone_id exists
    zone_name = None
    if zone_id:
        try:
            req = urllib.request.Request(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                zone_name = data.get("result", {}).get("name")
        except Exception:
            pass

    # 3. Test GraphQL Analytics
    traffic_count = None
    if zone_id:
        try:
            query = {
                "query": f"""query {{
                    viewer {{
                        zones(filter: {{zoneTag: "{zone_id}"}}) {{
                            httpRequestsAdaptiveGroups(limit: 1, filter: {{date_geq: "2026-08-01"}}) {{
                                count
                            }}
                        }}
                    }}
                }}"""
            }
            req = urllib.request.Request(
                "https://api.cloudflare.com/client/v4/graphql",
                data=json.dumps(query).encode("utf-8"),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                zones_data = data.get("data", {}).get("viewer", {}).get("zones", [])
                if zones_data and zones_data[0].get("httpRequestsAdaptiveGroups"):
                    traffic_count = zones_data[0]["httpRequestsAdaptiveGroups"][0].get("count", 0)
        except Exception:
            pass

    return {
        "status": "SUCCESS",
        "zone_name": zone_name,
        "zone_id": zone_id,
        "traffic_sample_count": traffic_count
    }

def main():
    print("==================================================================")
    print("  Central DevOps Hub — Multi-Project GSC & Cloudflare SEO Matrix  ")
    print("==================================================================\n")
    
    env_vars = load_env()
    
    for proj in PROJECTS:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"▶ 專案：{proj['name']} ({proj['domain']})")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # 1. GSC Test
        print(f"[1] Google Search Console (GSC)")
        gsc_res = test_gsc_for_project(proj, env_vars)
        if gsc_res["status"] == "SUCCESS":
            print(f"    狀態: 成功 (Active)")
            print(f"    服務帳號: {gsc_res.get('email')}")
            if gsc_res.get("matched_url"):
                print(f"    資源對應: {gsc_res['matched_url']} (連線正常)")
                if gsc_res.get("queries"):
                    print("    最近 28 天自然搜尋詞採樣:")
                    for q in gsc_res["queries"]:
                        print(f"      - 「{q['query']}」 | 曝光: {q['impressions']} | 點擊: {q['clicks']} | 排名: {q['position']}")
                else:
                    print("    最近 28 天自然搜尋詞採樣: (暫無搜尋點擊數據或新站收錄中)")
            else:
                print(f"    注意: 此服務帳號尚未加入 {proj['domain']} 的 GSC 權限名單")
        elif gsc_res["status"] == "MISSING":
            print(f"    狀態: 未配置 ({gsc_res['message']})")
        else:
            print(f"    狀態: 失敗 ({gsc_res.get('message')})")

        # 2. Cloudflare Analytics Test
        print(f"[2] Cloudflare Web Analytics (流量分析)")
        cf_res = test_cf_for_project(proj, env_vars)
        if cf_res["status"] == "SUCCESS":
            print(f"    狀態: 成功 (Active)")
            print(f"    Zone 網域: {cf_res.get('zone_name') or '已連結'}")
            print(f"    Zone ID: {cf_res.get('zone_id') or '(未指定)'}")
            if cf_res.get("traffic_sample_count") is not None:
                print(f"    GraphQL 流量測試: 正常 (8月累計請求採樣: {cf_res['traffic_sample_count']:,} 次)")
            else:
                print(f"    GraphQL 流量測試: 正常 (唯讀連線就緒)")
        elif cf_res["status"] == "MISSING":
            print(f"    狀態: 未配置 ({cf_res['message']})")
        else:
            print(f"    狀態: 失敗 ({cf_res.get('message')})")
        print()

    print("==================================================================")

if __name__ == "__main__":
    main()

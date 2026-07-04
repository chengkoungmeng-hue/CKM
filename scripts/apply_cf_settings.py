import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
ZONE_ID = 'd459c80e06d000c6e1927783fc6b3a7a'
BASE_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}"

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

def patch_setting(setting_name, payload):
    res = requests.patch(f"{BASE_URL}/settings/{setting_name}", headers=headers, json=payload)
    print(f"[{setting_name}] {res.status_code}: {res.text}")

def put_bot_management(payload):
    res = requests.put(f"{BASE_URL}/bot_management", headers=headers, json=payload)
    print(f"[Bot Management] {res.status_code}: {res.text}")

def put_ruleset_phase(phase, payload):
    res = requests.put(f"{BASE_URL}/rulesets/phases/{phase}/entrypoint", headers=headers, json=payload)
    print(f"[Ruleset {phase}] {res.status_code}: {res.text}")

if __name__ == "__main__":
    print("--- Applying Settings ---")
    
    # 1. Zone Settings
    patch_setting("brotli", {"value": "on"})
    patch_setting("early_hints", {"value": "on"})
    patch_setting("minify", {"value": {"css": "on", "html": "on", "js": "on"}})
    patch_setting("browser_cache_ttl", {"value": 14400})

    # 2. Bot Management (Skipped: 403 Forbidden for this token/plan)
    # put_bot_management({"fight_mode": False})

    # 3. Cache Rules (Astro Static Assets)
    cache_payload = {
        "rules": [
            {
                "action": "set_cache_settings",
                "action_parameters": {
                    "cache": True,
                    "edge_ttl": {"mode": "override_origin", "default": 31536000},
                    "browser_ttl": {"mode": "override_origin", "default": 31536000}
                },
                "expression": '(http.request.uri.path contains "/_astro/") or (http.request.uri.path contains "/assets/")',
                "description": "Astro Static Assets Cache"
            }
        ]
    }
    put_ruleset_phase("http_request_cache_settings", cache_payload)

    # 4. WAF Custom Rules (Skip Rule)
    waf_payload = {
        "rules": [
            {
                "action": "skip",
                "action_parameters": {
                    "phases": ["http_ratelimit", "http_request_sbfm", "http_request_firewall_managed"]
                },
                "expression": '(http.request.uri.path eq "/robots.txt") or (http.request.uri.path contains ".xml" and http.request.uri.path contains "sitemap")',
                "description": "SEO Bypass (The Security Guard Protocol)"
            }
        ]
    }
    put_ruleset_phase("http_request_firewall_custom", waf_payload)

    # 5. Rate Limiting
    rl_payload = {
        "rules": [
            {
                "action": "block",
                "ratelimit": {
                    "characteristics": ["ip.src", "cf.colo.id"],
                    "period": 10,
                    "requests_per_period": 50,
                    "mitigation_timeout": 10
                },
                "expression": "true",
                "description": "API Rate Limiting 50/10s"
            }
        ]
    }
    put_ruleset_phase("http_ratelimit", rl_payload)

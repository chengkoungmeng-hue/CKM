// devops/cloudflare_audit.js
import fs from 'fs';
import path from 'path';

function getEnvToken() {
  if (process.env.CLOUDFLARE_API_TOKEN) return process.env.CLOUDFLARE_API_TOKEN;
  const envPath = path.join(process.cwd(), '.env');
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, 'utf-8');
    const match = content.match(/CLOUDFLARE_API_TOKEN=["']?([^"'\r\n]+)["']?/);
    if (match) return match[1];
  }
  return null;
}

const API_TOKEN = getEnvToken();

if (!API_TOKEN) {
  console.error('❌ Error: CLOUDFLARE_API_TOKEN not found in environment or .env file.');
  process.exit(1);
}

async function cfFetch(endpoint) {
  const url = `https://api.cloudflare.com/client/v4${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    return await response.json();
  } catch (e) {
    return { success: false, error: e.message };
  }
}

async function auditCloudflareDeep() {
  console.log('🌐 Connecting to Cloudflare API for Deep Audit (WAF, Cache, Speed)...');
  
  const verifyRes = await cfFetch('/user/tokens/verify');
  if (!verifyRes.success) {
    console.error('❌ Token Verification Failed');
    process.exit(1);
  }

  const zonesRes = await cfFetch('/zones');
  const ckmZone = zonesRes.result.find(z => z.name === 'ckmkh.com') || zonesRes.result[0];
  const zoneId = ckmZone.id;

  console.log(`🎯 Target Zone: ${ckmZone.name} (${zoneId})`);

  // 1. Fetch All Settings
  console.log('📥 1. Fetching Global Settings...');
  const settingsRes = await cfFetch(`/zones/${zoneId}/settings`);

  // 2. Fetch WAF & Firewall Rules
  console.log('📥 2. Fetching WAF & Firewall Rules...');
  const firewallRulesRes = await cfFetch(`/zones/${zoneId}/firewall/rules`);
  const customRulesetsRes = await cfFetch(`/zones/${zoneId}/rulesets/phases/http_request_firewall_custom/entrypoint`);
  const managedRulesetsRes = await cfFetch(`/zones/${zoneId}/rulesets/phases/http_request_firewall_managed/entrypoint`);

  // 3. Fetch Cache Rules & Page Rules
  console.log('📥 3. Fetching Cache Rules & Page Rules...');
  const cacheRulesetsRes = await cfFetch(`/zones/${zoneId}/rulesets/phases/http_request_cache_settings/entrypoint`);
  const pageRulesRes = await cfFetch(`/zones/${zoneId}/pagerules`);

  // 4. Fetch Speed & Optimization Settings
  console.log('📥 4. Fetching Speed & Optimization Settings...');
  const settingsMap = settingsRes.result ? settingsRes.result.reduce((acc, s) => {
    acc[s.id] = s.value;
    return acc;
  }, {}) : {};

  const auditReport = {
    timestamp: new Date().toISOString(),
    zone: {
      id: ckmZone.id,
      name: ckmZone.name,
      plan: ckmZone.plan?.name,
      status: ckmZone.status
    },
    wafAndSecurity: {
      securityLevel: settingsMap.security_level,
      browserCheck: settingsMap.browser_check,
      wafLegacy: settingsMap.waf,
      firewallRules: firewallRulesRes.result || [],
      customWafRuleset: customRulesetsRes.result || null,
      managedWafRuleset: managedRulesetsRes.result || null
    },
    cacheConfiguration: {
      cacheLevel: settingsMap.cache_level,
      browserCacheTtl: settingsMap.browser_cache_ttl,
      edgeCacheTtl: settingsMap.edge_cache_ttl,
      developmentMode: settingsMap.development_mode,
      alwaysOnline: settingsMap.always_online,
      pageRules: pageRulesRes.result || [],
      cacheRuleset: cacheRulesetsRes.result || null
    },
    speedAndOptimization: {
      brotli: settingsMap.brotli,
      earlyHints: settingsMap.early_hints,
      http2: settingsMap.http2,
      http3: settingsMap.http3,
      zeroRtt: settingsMap['0rtt'],
      autoMinify: settingsMap.minify,
      polish: settingsMap.polish,
      webp: settingsMap.webp,
      rocketLoader: settingsMap.rocket_loader,
      mirage: settingsMap.mirage
    }
  };

  const reportPath = path.join(process.cwd(), 'devops', 'reports', 'cloudflare_audit_summary.json');
  fs.writeFileSync(reportPath, JSON.stringify(auditReport, null, 2), 'utf-8');
  console.log(`\n✅ Deep Audit Complete! Report saved to ${reportPath}`);
}

auditCloudflareDeep().catch(err => {
  console.error('❌ Audit Error:', err);
  process.exit(1);
});

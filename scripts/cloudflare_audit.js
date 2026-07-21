// scripts/cloudflare_audit.js
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
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${API_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
}

async function auditCloudflare() {
  console.log('🌐 Authenticating with Cloudflare API...');
  
  // 1. Verify Token
  const verifyRes = await cfFetch('/user/tokens/verify');
  console.log('Token Status:', verifyRes.success ? '✅ Active' : '❌ Invalid');

  // 2. Fetch Zones
  const zonesRes = await cfFetch('/zones');
  if (!zonesRes.success || !zonesRes.result || zonesRes.result.length === 0) {
    console.error('❌ Could not fetch zones:', JSON.stringify(zonesRes.errors));
    process.exit(1);
  }

  console.log(`\nFound ${zonesRes.result.length} Zone(s):`);
  const ckmZone = zonesRes.result.find(z => z.name === 'ckmkh.com') || zonesRes.result[0];
  console.log(`🎯 Targeted Zone: ${ckmZone.name} (ID: ${ckmZone.id}) - Status: ${ckmZone.status}`);

  const zoneId = ckmZone.id;

  // 3. Fetch Settings
  console.log('\n📥 Fetching Zone Settings...');
  const settingsRes = await cfFetch(`/zones/${zoneId}/settings`);

  // 4. Fetch DNS Records
  console.log('📥 Fetching DNS Records...');
  const dnsRes = await cfFetch(`/zones/${zoneId}/dns_records`);

  // 5. Fetch Page Rules / Rulesets
  console.log('📥 Fetching Custom Rulesets...');
  const rulesetsRes = await cfFetch(`/zones/${zoneId}/rulesets`);

  const reportData = {
    timestamp: new Date().toISOString(),
    tokenValid: verifyRes.success,
    zone: {
      id: ckmZone.id,
      name: ckmZone.name,
      status: ckmZone.status,
      paused: ckmZone.paused,
      type: ckmZone.type,
      nameServers: ckmZone.name_servers,
      plan: ckmZone.plan?.name
    },
    settings: settingsRes.result ? settingsRes.result.reduce((acc, s) => {
      acc[s.id] = s.value;
      return acc;
    }, {}) : {},
    dnsRecords: dnsRes.result ? dnsRes.result.map(r => ({
      type: r.type,
      name: r.name,
      content: r.content,
      proxied: r.proxied,
      ttl: r.ttl
    })) : [],
    rulesets: rulesetsRes.result ? rulesetsRes.result.map(rs => ({
      id: rs.id,
      name: rs.name,
      phase: rs.phase
    })) : []
  };

  const reportPath = path.join(process.cwd(), 'scripts', 'cloudflare_audit_summary.json');
  fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2), 'utf-8');
  console.log(`\n✅ Audit Complete! Cloudflare configuration saved to ${reportPath}`);
}

auditCloudflare().catch(err => {
  console.error('❌ Audit Failed:', err);
  process.exit(1);
});

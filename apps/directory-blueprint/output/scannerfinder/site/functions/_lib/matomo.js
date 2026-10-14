// Matomo Reporting API (stats.mkstack.com, site 3). Token: Pages secret MATOMO_TOKEN, view-only user
// `scannerfinder-api`, "secure requests only" → sent in a POST body, never in a URL. Answers are cached for an hour.
export async function matomo(env, method, params = {}) {
  if (!env.MATOMO_TOKEN) return null;
  const query = { module: 'API', method, idSite: env.MATOMO_SITE_ID || '3', period: 'range', date: 'last30', format: 'JSON', filter_limit: '-1', ...params };
  const key = new Request('https://matomo-cache.scannerfinder.internal/?' + new URLSearchParams(query).toString());
  const cache = caches.default;
  const hit = await cache.match(key);
  if (hit) return hit.json();
  try {
    const r = await fetch(env.MATOMO_URL, { method: 'POST', body: new URLSearchParams({ ...query, token_auth: env.MATOMO_TOKEN }) });
    const data = await r.json();
    if (!r.ok || (data && data.result === 'error')) { console.log(`[matomo] ${method}: ${r.status} ${data && data.message}`); return null; }
    await cache.put(key, new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json', 'cache-control': 'max-age=3600' } }));
    return data;
  } catch (e) {
    console.log(`[matomo] ${method}: ${e && e.message}`);
    return null;
  }
}

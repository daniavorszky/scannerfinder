// GET /api/claim/benchmark: where the signed-in practitioner stands against their peers (plan § Faza 3).
// Only aggregates of 5+ peers are returned (the practitioner is never counted among their own peers) and only
// the interquartile range, never min/max, so no single practice's price can be read back.
import { json } from '../../_lib/util.js';
import { tokenClaim, sessionFrom, listing } from '../../_lib/claim.js';
import { matomo } from '../../_lib/matomo.js';
import bench from '../../_data/benchmark-data.json';

const MIN_GROUP = 5;
const EVENT_TYPES = ['phone', 'website', 'directions', 'maps', 'booking'];

const quant = (sorted, q) => { const i = (sorted.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo); };
function summary(values, mine) {
  const v = values.filter((x) => typeof x === 'number' && x > 0).sort((a, b) => a - b);
  if (v.length < MIN_GROUP) return { n: v.length, ok: false };
  const out = { n: v.length, ok: true, median: quant(v, 0.5), p25: quant(v, 0.25), p75: quant(v, 0.75) };
  if (typeof mine === 'number' && mine > 0) out.percentile = Math.round(100 * (v.filter((x) => x < mine).length + v.filter((x) => x === mine).length / 2) / v.length);
  return out;
}
const km = (a, b) => { const R = 6371, t = Math.PI / 180, dLat = (b.lat - a.lat) * t, dLng = (b.lng - a.lng) * t; const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * t) * Math.cos(b.lat * t) * Math.sin(dLng / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(h)); };

export async function onRequestGet({ request, env }) {
  const c = await tokenClaim(env, sessionFrom(request), 'session');
  if (!c) return json({ ok: false, error: 'signed_out' }, 401);
  const me = bench.peers[c.listing_slug];
  const pub = listing(c.listing_slug);
  if (!me || !pub) return json({ ok: false, error: 'no_listing' }, 200);

  // Approved claims replace the seed price and devices of their listing (also private prices: aggregates only).
  const peers = Object.fromEntries(Object.entries(bench.peers).map(([s, p]) => [s, { ...p }]));
  const approved = await env.DB.prepare(`SELECT c.listing_slug AS slug, p.data FROM claims c JOIN profile_public p ON p.claim_id = c.id
    WHERE c.status = 'approved' AND p.reviewed_at IS NOT NULL
      AND p.version = (SELECT max(version) FROM profile_public WHERE claim_id = c.id AND reviewed_at IS NOT NULL)`).all();
  for (const row of approved.results || []) {
    const p = peers[row.slug]; if (!p) continue;
    const d = JSON.parse(row.data);
    if (d.session_price && bench.fx[d.currency]) { p.pu = d.session_price * bench.fx[d.currency]; p.mu = d.session_minutes || null; }
    if (d.devices && d.devices.length) p.dv = d.devices.map((n) => bench.devices[n]).filter(Boolean);
  }
  // The practitioner's own answer counts for them even before approval.
  const mine = await env.DB.prepare('SELECT data FROM profile_public WHERE claim_id = ?1 ORDER BY version DESC LIMIT 1').bind(c.id).first();
  const own = mine ? JSON.parse(mine.data) : {};
  const you = peers[c.listing_slug];
  if (own.session_price && bench.fx[own.currency]) { you.pu = own.session_price * bench.fx[own.currency]; you.mu = own.session_minutes || you.mu; }
  if (own.devices && own.devices.length) you.dv = own.devices.map((n) => bench.devices[n]).filter(Boolean);
  const cur = bench.fx[own.currency] ? own.currency : bench.fx[pub.cur] ? pub.cur : 'USD';
  const toCur = (usd) => (usd == null ? null : Math.round(usd / bench.fx[cur]));
  const others = Object.entries(peers).filter(([s]) => s !== c.listing_slug).map(([, p]) => p);

  const inCur = (s) => (s.ok ? { ...s, median: toCur(s.median), p25: toCur(s.p25), p75: toCur(s.p75) } : s);
  const country = bench.countries[you.cc], region = bench.regions[you.rg];
  const priceGroups = [
    { label: you.c, scope: 'town', list: others.filter((p) => p.cc === you.cc && p.c === you.c) },
    { label: region, scope: 'region', list: others.filter((p) => p.rg === you.rg) },
    { label: country, scope: 'country', list: others.filter((p) => p.cc === you.cc) },
    ...you.dv.flatMap((k) => [
      { label: `${bench.labels[k]} in ${country}`, scope: 'device-country', list: others.filter((p) => p.cc === you.cc && p.dv.includes(k)) },
      { label: `${bench.labels[k]}, all countries`, scope: 'device', list: others.filter((p) => p.dv.includes(k)) },
    ]),
  ];
  const price = priceGroups.map((g) => ({ label: g.label, scope: g.scope, ...inCur(summary(g.list.map((p) => p.pu), you.pu)) }));
  const perMinute = [
    { label: country, list: others.filter((p) => p.cc === you.cc) },
    { label: 'All countries', list: others },
  ].map((g) => {
    const s = summary(g.list.filter((p) => p.pu && p.mu).map((p) => p.pu / p.mu), you.pu && you.mu ? you.pu / you.mu : null);
    return { label: g.label, ...(s.ok ? { ...s, median: +(s.median / bench.fx[cur]).toFixed(2), p25: +(s.p25 / bench.fx[cur]).toFixed(2), p75: +(s.p75 / bench.fx[cur]).toFixed(2) } : s) };
  });

  const regionPeers = others.filter((p) => p.rg === you.rg);
  const reviewed = regionPeers.filter((p) => p.n > 0);
  const reputation = { region, rating: summary(reviewed.map((p) => p.r), you.n > 0 ? you.r : null), reviews: summary(regionPeers.map((p) => p.n + 0.0001), you.n + 0.0001), you: { rating: you.r, reviews: you.n } };
  reputation.reviews = reputation.reviews.ok ? { ...reputation.reviews, median: Math.round(reputation.reviews.median), p25: Math.round(reputation.reviews.p25), p75: Math.round(reputation.reviews.p75) } : reputation.reviews;

  const near = you.lat != null ? others.filter((p) => p.lat != null && km(you, p) <= 25) : [];
  const competition = { radiusKm: 25, all: near.length, byDevice: you.dv.map((k) => ({ device: bench.labels[k], n: near.filter((p) => p.dv.includes(k)).length })) };
  const completeness = { you: you.pc, region: summary(regionPeers.map((p) => p.pc), you.pc), position: you.pos };

  // Visibility and local demand, last 30 days (Matomo). Region average = all listings of the region, zeros included.
  let visibility = null, demand = null;
  const regionPrefix = pub.p.split('/').slice(0, 4).join('/') + '/';
  const regionSlugs = Object.entries(peers).filter(([, p]) => p.rg === you.rg && p.cc === you.cc).map(([s]) => s);
  const [pages, events, searches, empty] = await Promise.all([
    matomo(env, 'Actions.getPageUrls', { flat: '1', filter_pattern: regionPrefix.replace(/^\//, '') }),
    matomo(env, 'Events.getName', { secondaryDimension: 'eventAction', flat: '1' }),
    matomo(env, 'Actions.getSiteSearchKeywords', { filter_pattern: you.c }),
    matomo(env, 'Actions.getSiteSearchNoResultKeywords', { filter_pattern: you.c }),
  ]);
  if (pages && events) {
    const count = Object.fromEntries(regionSlugs.map((s) => [s, { views: 0, ...Object.fromEntries(EVENT_TYPES.map((t) => [t, 0])) }]));
    for (const row of Array.isArray(pages) ? pages : []) {
      const m = String(row.url || row.label || '').match(/\/company\/[^/]+\/[^/]+\/([^/?#]+)/);
      if (m && count[m[1]]) count[m[1]].views += row.nb_hits || 0;
    }
    for (const row of Array.isArray(events) ? events : []) {
      const i = String(row.label || '').lastIndexOf(' - ');
      if (i < 0) continue;
      const slug = row.label.slice(0, i), type = row.label.slice(i + 3);
      if (count[slug] && type in count[slug]) count[slug][type] += row.nb_events || 0;
    }
    const keys = ['views', ...EVENT_TYPES];
    const avg = Object.fromEntries(keys.map((k) => [k, +(regionSlugs.reduce((a, s) => a + count[s][k], 0) / regionSlugs.length).toFixed(1)]));
    visibility = { period: 'last 30 days', you: count[c.listing_slug], regionAverage: avg, regionListings: regionSlugs.length };
  }
  if (searches && empty) {
    const sum = (rows) => (Array.isArray(rows) ? rows.reduce((a, r) => a + (r.nb_visits || 0), 0) : 0);
    demand = { period: 'last 30 days', place: you.c, searches: sum(searches), noResult: sum(empty) };
  }

  return json({
    ok: true, currency: cur, name: pub.n, listingPath: pub.p,
    you: { price: toCur(you.pu), minutes: you.mu || null, priceIsSeed: !own.session_price && !!you.pu },
    price, perMinute, reputation, competition, completeness, visibility, demand, minGroup: MIN_GROUP,
  });
}

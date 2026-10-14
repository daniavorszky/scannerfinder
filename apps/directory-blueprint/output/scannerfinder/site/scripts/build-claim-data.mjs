// Builds functions/_data/claim-data.json: what the claim flow needs per listing, server-side only.
// Public fields come from the same loader the pages use; ownership hints (website domain, SHA-256 of the
// emails we found) and the session prices found on the practice's own site come from the internal master
// CSVs, which never ship as static files. Runs before `astro build` (package.json).
import fs from 'node:fs';
import crypto from 'node:crypto';
import { loadDirectory, CLAIM_DEVICES } from '../src/lib/load.mjs';

const MASTERS = ['../../../../../data/listings_profiled.csv', '../../../../../data/batch-de-ro/listings_profiled.csv'];
const OUT = 'functions/_data/claim-data.json';
const BENCH = 'functions/_data/benchmark-data.json';
const FX_SOURCE = '../../../../../scripts/merge_prices.py';

function parseCsv(text) {
  const rows = []; let row = [], field = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else q = false; } else field += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',') { row.push(field); field = ''; }
    else if (ch === '\n' || ch === '\r') { if (ch === '\r' && text[i + 1] === '\n') i++; row.push(field); rows.push(row); row = []; field = ''; }
    else field += ch;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  const [head, ...body] = rows;
  return body.filter((r) => r.length > 1).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i] ?? ''])));
}

const hash = (e) => crypto.createHash('sha256').update(e.trim().toLowerCase()).digest('hex');
const host = (u) => { try { return new URL(/^https?:/.test(u) ? u : `https://${u}`).hostname.replace(/^www\./, '').toLowerCase(); } catch { return ''; } };
const num = (v) => { const n = Number.parseFloat(String(v).replace(/[^0-9.]/g, '')); return Number.isFinite(n) && n > 0 ? n : null; };
const CURRENCY = { US: 'USD', GB: 'GBP', DE: 'EUR', IE: 'EUR', RO: 'RON', CA: 'CAD', AU: 'AUD', NZ: 'NZD', ZA: 'ZAR' };

const master = new Map();
let haveMaster = false;
for (const p of MASTERS) {
  if (!fs.existsSync(p)) continue;
  haveMaster = true;
  for (const r of parseCsv(fs.readFileSync(p, 'utf8'))) if (r.cid) master.set(r.cid, r);
}
if (!haveMaster) console.warn('[claim-data] master CSVs not found: building without ownership hints or found prices');

const { listings } = loadDirectory();
const csvRows = new Map(parseCsv(fs.readFileSync('src/data/listings.csv', 'utf8')).map((r) => [r.slug, r]));
const out = {};
for (const l of listings) {
  const r = csvRows.get(l.slug) || {};
  const m = master.get(r.cid) || {};
  const emails = new Set(
    [m.final_email, m.best_email, m.mc_best_email, m.mc_all_emails, m.emails, m.site_emails]
      .join(';').split(/[;,\s]+/).map((e) => e.trim().toLowerCase()).filter((e) => /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/.test(e))
  );
  const initial = num(m.scan_price_initial) ?? num(m.scan_price_single);
  out[l.slug] = {
    n: l.name, c: l.city, cc: l.stateCode, co: l.country.name, p: l.path,
    ph: l.phone || '', w: l.website || '', d: host(l.website || r.domain || ''),
    e: [...emails].map(hash),
    dv: (r.devices || '').split(/[;|]/).map((s) => s.trim()).filter(Boolean),
    dm: r.device_models || '', bk: r.booking_platform || '',
    rm: r.remote_sessions === 'true', fc: r.free_consultation === 'true',
    cur: CURRENCY[l.stateCode] || 'USD',
    // Found on the practice's own website, not published; shown back to the owner to confirm or correct.
    fp: initial ? { i: initial, f: num(m.scan_price_followup), cur: m.scan_price_currency || CURRENCY[l.stateCode], min: num(m.scan_duration_min) } : null,
  };
}
fs.mkdirSync('functions/_data', { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(out));
const vals = Object.values(out);
console.log(`[claim-data] ${vals.length} listings, ${vals.filter((v) => v.e.length).length} with known emails, ${vals.filter((v) => v.d).length} with a domain, ${vals.filter((v) => v.fp).length} with a found price`);

// Benchmark peers (plan § Faza 3): one compact row per listing for /api/claim/benchmark. Seed session prices are
// the same set /statistics/ uses (src/data/session-prices.json, USD); approved claims override them at request
// time. FX comes from merge_prices.py so there is one rate table.
const fxText = fs.existsSync(FX_SOURCE) ? fs.readFileSync(FX_SOURCE, 'utf8').match(/^FX = (\{[^}]*\})/m) : null;
const FX = fxText ? JSON.parse(fxText[1]) : { USD: 1 };
const seedPrices = fs.existsSync('src/data/session-prices.json') ? JSON.parse(fs.readFileSync('src/data/session-prices.json', 'utf8')) : {};
const dir = loadDirectory();
const position = new Map();
for (const c of dir.cities) c.listings.forEach((l, i) => position.set(l.slug, [i + 1, c.listings.length]));
const deviceKeys = Object.values(CLAIM_DEVICES);
const peers = {};
for (const l of dir.listings) {
  const r = csvRows.get(l.slug) || {};
  const m = master.get(r.cid) || {};
  const seed = typeof seedPrices[l.slug] === 'number' ? seedPrices[l.slug] : (seedPrices[l.slug] && seedPrices[l.slug].usd);
  peers[l.slug] = {
    cc: l.stateCode, rg: l.citySlug, c: l.city,
    lat: l.lat ? Number(l.lat.toFixed(4)) : null, lng: l.lng ? Number(l.lng.toFixed(4)) : null,
    dv: deviceKeys.filter((k) => (l.attrs.find((a) => a.key === k) || {}).value === 'true'),
    r: l.rating || 0, n: l.reviews || 0, pc: Number(r.profile_completeness) || 0,
    pu: seed || null, mu: seed ? num(m.scan_duration_min) : null,
    pos: position.get(l.slug) || null,
  };
}
fs.writeFileSync(BENCH, JSON.stringify({ fx: FX, devices: CLAIM_DEVICES, labels: Object.fromEntries(JSON.parse(fs.readFileSync('src/data/attributes.json', 'utf8')).filter((a) => deviceKeys.includes(a.key)).map((a) => [a.key, a.label])), regions: Object.fromEntries(dir.cities.map((c) => [c.slug, c.name])), countries: Object.fromEntries(dir.countries.map((c) => [c.code, c.name])), peers }));
console.log(`[benchmark-data] ${Object.keys(peers).length} peers, ${Object.values(peers).filter((p) => p.pu).length} seed prices, FX ${fxText ? 'from merge_prices.py' : 'MISSING (USD only)'}`);

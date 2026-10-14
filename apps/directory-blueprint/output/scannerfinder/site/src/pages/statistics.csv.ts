import type { APIRoute } from 'astro';
import { loadStats } from '../lib/stats.mjs';

// /statistics.csv: the device × country matrix behind /statistics/, one row per country plus an "All" row,
// then the remote-session and device-naming shares. CC BY 4.0 (stated on /statistics/).
export const GET: APIRoute = () => {
  const S = loadStats();
  const q = (v: unknown) => { const s = String(v ?? ''); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const head = ['country', 'listed_practitioners', ...S.devices.map((d: any) => d.d.label), 'name_a_device', 'offer_remote_sessions', 'median_session_price_usd', 'price_sample'];
  const rows = S.countries.map((c: any) => [c.co.name, c.total, ...S.devices.map((d: any) => c.cells.find((x: any) => x.key === d.d.key).n), c.named, c.remote, c.price.ok ? c.price.median : '', c.price.n]);
  rows.push(['All countries', S.total, ...S.devices.map((d: any) => d.n), S.named, S.remote, S.price.ok ? S.price.median : '', S.price.n]);
  const csv = [`# ${S.dir.site.brand} bioresonance practitioner statistics, ${S.dir.buildDate}. Source: https://${S.dir.site.domain}/statistics/ (CC BY 4.0)`, head, ...rows]
    .map((r) => (Array.isArray(r) ? r.map(q).join(',') : r)).join('\n') + '\n';
  return new Response(csv, { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
};

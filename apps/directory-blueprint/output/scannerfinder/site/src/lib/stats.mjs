// Directory statistics for /statistics/ and /statistics.csv (2026-10-14). Everything is counted from the
// listings at build time, so the numbers move with the data. Session prices: only aggregated medians (Dan,
// 2026-10-14) from src/data/session-prices.json (scripts/export_session_prices.py), shown when n >= PRICE_MIN.
// No average ratings (they all sit between 4.8 and 5.0 and say nothing).
import { loadDirectory, attrValue } from './load.mjs';
import prices from '../data/session-prices.json';

export const PRICE_MIN = 5;
const quant = (v, q) => { const a = [...v].sort((x, y) => x - y); const i = (a.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i); return Math.round(a[lo] + (a[hi] - a[lo]) * (i - lo)); };
const priceSummary = (ls) => { const v = ls.map((l) => prices[l.slug]).filter((x) => x != null); return v.length ? { n: v.length, median: quant(v, .5), p25: quant(v, .25), p75: quant(v, .75), ok: v.length >= PRICE_MIN } : { n: 0, ok: false }; };

const yes = (l, key) => attrValue(l, key) === 'true';
const pct = (n, d) => (d ? Math.round((100 * n) / d) : 0);

let cache = null;
export function loadStats() {
  if (cache) return cache;
  const dir = loadDirectory();
  const { listings, countries, devices } = dir;
  const total = listings.length;
  const deviceKeys = devices.map((d) => d.key);
  const namesDevice = (l) => deviceKeys.some((k) => yes(l, k));

  // 1. Technology × country matrix and the leading device per country.
  const byCountry = [...countries].sort((a, b) => b.count - a.count).map((co) => {
    const ls = listings.filter((l) => l.country.code === co.code);
    const cells = devices.map((d) => ({ key: d.key, label: d.label, n: ls.filter((l) => yes(l, d.key)).length }));
    const ranked = [...cells].filter((c) => c.n > 0).sort((a, b) => b.n - a.n);
    const named = ls.filter(namesDevice).length;
    return {
      co, total: ls.length, cells, leader: ranked[0] || null, second: ranked[1] || null,
      named, namedPct: pct(named, ls.length),
      remote: ls.filter((l) => yes(l, 'remote_sessions')).length, remotePct: pct(ls.filter((l) => yes(l, 'remote_sessions')).length, ls.length),
      price: priceSummary(ls),
    };
  });

  // 2. Technology profiles.
  const named = listings.filter(namesDevice);
  const byDevice = [...devices].map((d) => {
    const ls = listings.filter((l) => yes(l, d.key));
    const remote = ls.filter((l) => yes(l, 'remote_sessions')).length;
    return { d, n: ls.length, countries: d.byCountry.length, remote, remotePct: pct(remote, ls.length), sharePct: pct(ls.length, named.length), price: priceSummary(ls) };
  }).sort((a, b) => b.n - a.n);

  // 4. Who offers scan sessions: the Google primary category.
  const types = [...listings.reduce((m, l) => m.set(l.type || 'Other', (m.get(l.type || 'Other') || 0) + 1), new Map())]
    .map(([type, n]) => ({ type, n, p: pct(n, total) })).sort((a, b) => b.n - a.n);

  // 5. Transparency.
  const multi = listings.filter((l) => deviceKeys.filter((k) => yes(l, k)).length >= 2).length;
  const remoteAll = listings.filter((l) => yes(l, 'remote_sessions')).length;

  return cache = {
    price: priceSummary(listings),
    dir, total, countries: byCountry, devices: byDevice, types,
    named: named.length, namedPct: pct(named.length, total), multi, remote: remoteAll, remotePct: pct(remoteAll, total),
  };
}

// Short "in numbers" blocks for the country, device and device × country pages (StatBlock.astro).
// Each returns { facts: [{ v, l }], sentence } or null when there is too little data to say anything.
const ordinal = (n) => n + (['th', 'st', 'nd', 'rd'][(n % 100 - 20) % 10] || ['th', 'st', 'nd', 'rd'][n % 100] || 'th');

export function countryBlock(code) {
  const S = loadStats();
  const c = S.countries.find((x) => x.co.code === code);
  if (!c || !c.total) return null;
  const ls = S.dir.listings.filter((l) => l.country.code === code);
  const type = [...ls.reduce((m, l) => m.set(l.type || 'Other', (m.get(l.type || 'Other') || 0) + 1), new Map())].sort((a, b) => b[1] - a[1])[0];
  const lead = c.leader && c.second && c.second.n === c.leader.n ? `${c.leader.label} and ${c.second.label} (tied)` : c.leader?.label;
  return {
    title: `Bioresonance in ${c.co.inName} in numbers`,
    facts: [
      { v: c.total.toLocaleString('en-US'), l: 'listed practitioners' },
      ...(c.leader ? [{ v: lead, l: 'most-named device', small: true }] : []),
      { v: `${c.namedPct}%`, l: 'name their device' },
      { v: `${c.remotePct}%`, l: 'offer remote sessions' },
    ],
    sentence: `${c.namedPct}% of the ${c.total} practitioners listed in ${c.co.inName} name the device they use${c.leader ? (c.second && c.second.n === c.leader.n ? `; the most named are ${c.leader.label} and ${c.second.label}, with ${c.leader.n} each` : `; the most named is ${c.leader.label}, with ${c.leader.n}`) : ''}. ${c.remotePct}% offer remote sessions, against ${S.remotePct}% across all ${S.countries.length} countries.${type ? ` The most common type of practice is "${type[0]}" (${pct(type[1], c.total)}%).` : ''}${c.price.ok ? ` The median published price of a session in ${c.co.inName} is about $${c.price.median} (${c.price.n} practitioner websites).` : ''}`,
  };
}

export function deviceBlock(key) {
  const S = loadStats();
  const i = S.devices.findIndex((x) => x.d.key === key);
  if (i < 0) return null;
  const d = S.devices[i];
  const leads = S.countries.filter((c) => c.leader && c.cells.find((x) => x.key === key).n === c.leader.n && c.leader.n > 0)
    .map((c) => c.co.inName + (c.cells.filter((x) => x.n === c.leader.n).length > 1 ? ' (joint)' : ''));
  return {
    title: `${d.d.label} in numbers`,
    facts: [
      { v: d.n.toLocaleString('en-US'), l: 'listed practitioners' },
      { v: d.countries, l: d.countries === 1 ? 'country' : 'countries' },
      { v: ordinal(i + 1), l: `of ${S.devices.length} devices by practitioners` },
      { v: `${d.remotePct}%`, l: 'offer remote sessions' },
    ],
    sentence: `${d.n} practitioners in ${d.countries} ${d.countries === 1 ? 'country' : 'countries'} name ${d.d.label}, ${d.sharePct}% of all listed practitioners who name a device, which makes it the ${i === 0 ? '' : ordinal(i + 1) + ' '}most-named of ${S.devices.length}. ${leads.length ? `It is the most-named device in ${leads.join(', ').replace(/, ([^,]*)$/, ' and $1')}. ` : ''}${d.remotePct}% of ${d.d.label} practitioners offer remote sessions, against ${S.remotePct}% across the directory.${d.price.ok ? ` The median published price of a ${d.d.label} session is $${d.price.median} (${d.price.n} practitioner websites), against $${S.price.median} for all devices.` : ''}`,
  };
}

export function deviceCountryBlock(key, code) {
  const S = loadStats();
  const c = S.countries.find((x) => x.co.code === code);
  const d = S.devices.find((x) => x.d.key === key);
  if (!c || !d) return null;
  const ranked = c.cells.filter((x) => x.n > 0).sort((a, b) => b.n - a.n);
  const mine = c.cells.find((x) => x.key === key);
  if (!mine || !mine.n) return null;
  const rank = ranked.filter((x) => x.n > mine.n).length + 1;
  const tied = ranked.filter((x) => x.n === mine.n).length > 1;
  const ls = S.dir.listings.filter((l) => l.country.code === code && yes(l, key));
  const remote = pct(ls.filter((l) => yes(l, 'remote_sessions')).length, ls.length);
  const leader = ranked[0];
  return {
    title: `${d.d.label} in ${c.co.inName} in numbers`,
    facts: [
      { v: mine.n, l: `of ${c.total} practitioners in ${c.co.inName}` },
      { v: `${pct(mine.n, c.named)}%`, l: 'of those who name a device' },
      { v: `${tied ? '=' : ''}${ordinal(rank)}`, l: `of ${ranked.length} devices in ${c.co.inName}` },
      { v: `${remote}%`, l: 'offer remote sessions' },
    ],
    sentence: `${mine.n} of the ${c.total} practitioners listed in ${c.co.inName} ${mine.n === 1 ? 'names' : 'name'} ${d.d.label} (${pct(mine.n, c.named)}% of those who name a device), ${rank === 1 ? (tied ? 'level with the most-named device there' : 'more than any other device') : `${tied ? 'joint ' : ''}${ordinal(rank)} behind ${leader.label} (${leader.n})`}. ${mine.n === 1 ? (remote ? 'They offer' : 'They do not offer') + ' remote sessions.' : `${remote}% of them offer remote sessions.`}`,
  };
}

// Directory Blueprint: data layer. Plain JS so astro.config.mjs and pages share it.
// Reads src/data/site.json, listings.csv, attributes.json, city-copy.json.
// Rules implemented here come from wiki/framework/site-architecture.md, page-types.md,
// listings-cleaning.md (thin), monetization-slots.md (sort order), seo/launch-lean.md.
import fs from 'node:fs';
import path from 'node:path';

// Resolved from the project root, not import.meta.url: Astro bundles this file into dist/chunks
// at build time and the relative path would break. Override with DIRECTORY_DATA_DIR if needed.
const DATA = process.env.DIRECTORY_DATA_DIR || path.join(process.cwd(), 'src', 'data');
const read = (f) => fs.readFileSync(path.join(DATA, f), 'utf8');

export function loadSite() {
  const site = JSON.parse(read('site.json'));
  // The state's URL segment is its full name (/company/florida/), unless site.json sets state.slug.
  site.state.slug = site.state.slug || site.state.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  return site;
}

// Minimal RFC 4180 CSV parser (quotes, escaped quotes, newlines in quoted fields).
export function parseCsv(text) {
  const rows = []; let row = []; let field = ''; let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else q = false; }
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); field = ''; rows.push(row); row = [];
    } else field += c;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  const header = (rows.shift() || []).map((h) => h.replace(/^﻿/, '').trim());
  return rows.filter((r) => r.length > 1 || (r[0] || '').trim()).map((r) => {
    const o = {}; header.forEach((h, i) => (o[h] = (r[i] ?? '').trim())); return o;
  });
}

export const slugify = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'x';
const truthy = (v) => /^(true|yes|1|y)$/i.test((v || '').trim());
const num = (v) => { const n = parseFloat(v); return Number.isFinite(n) ? n : 0; };
const int = (v) => Math.round(num(v));

export function formatPhone(p) {
  const d = (p || '').replace(/\D/g, '');
  const t = d.length === 11 && d[0] === '1' ? d.slice(1) : d;
  return t.length === 10 ? `(${t.slice(0, 3)}) ${t.slice(3, 6)}-${t.slice(6)}` : (p || '');
}
// Schema.org telephone in E.164 (+13055551234). US numbers; anything else is passed through as given.
export function e164(p) {
  const d = String(p || '').replace(/\D/g, '');
  if (d.length === 10) return '+1' + d;
  if (d.length === 11 && d[0] === '1') return '+' + d;
  return p || undefined;
}
// The schema.org type of a listed business: niche.schemaType in site.json (the closest LocalBusiness
// subtype, e.g. RoofingContractor, Plumber, Electrician; wiki/seo/schema.md), LocalBusiness when unset.
export function businessType(site) { return (site.niche && site.niche.schemaType) || 'LocalBusiness'; }
export function telHref(p) {
  const d = (p || '').replace(/\D/g, '');
  return d ? `tel:+${d.length === 10 ? '1' + d : d}` : '';
}

// Outscraper working_hours arrives as a JSON-ish string: {"Monday": "8AM-5PM", ...}
export function parseHours(raw) {
  if (!raw) return [];
  let obj = null;
  try { obj = JSON.parse(raw); } catch { try { obj = JSON.parse(raw.replace(/'/g, '"')); } catch { return []; } }
  if (!obj || typeof obj !== 'object') return [];
  const order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  return order.filter((d) => d in obj).map((d) => ({ day: d, hours: String(obj[d]) }));
}
// "8AM-5PM" -> { opens: "08:00", closes: "17:00" } for schema; null when not parseable.
export function hoursToSpec(h) {
  const m = /^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)\s*[-–]\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$/i.exec((h || '').trim());
  if (!m) return null;
  const to24 = (hh, mm, ap) => { let x = parseInt(hh, 10) % 12; if (/pm/i.test(ap)) x += 12; return `${String(x).padStart(2, '0')}:${mm || '00'}`; };
  return { opens: to24(m[1], m[2], m[3]), closes: to24(m[4], m[5], m[6]) };
}

function haversine(a, b) {
  const R = 6371, toRad = (x) => (x * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat), dLon = toRad(b.lng - a.lng);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

let cache = null;
export function loadDirectory() {
  if (cache) return cache;
  const site = loadSite();
  const attributes = JSON.parse(read('attributes.json'));
  const cityCopyRaw = JSON.parse(read('city-copy.json'));
  const cityCopy = Object.fromEntries(Object.entries(cityCopyRaw).filter(([k]) => !k.startsWith('_')));
  const rows = parseCsv(read('listings.csv'));
  const stateSlug = site.state.slug;
  // Location pages sit under /directory/<state>/<city>/, business pages under /company/<state>/<city>/<business>/
  // (wiki/framework/site-architecture.md).
  const DIR = `/directory/${stateSlug}`, CO = `/company/${stateSlug}`;

  // Listings
  const seen = new Set();
  const listings = rows.map((r) => {
    const city = r.city || 'Unknown';
    const citySlug = r.city_slug || slugify(city);
    let slug = r.slug || slugify(`${r.name}-${city}`);
    if (seen.has(slug)) slug = `${slug}-${r.postal_code || seen.size}`;
    seen.add(slug);
    const attrs = attributes.map((a) => ({ key: a.key, label: a.label, value: normalizeAttr(r[a.key]) }));
    const featured = (r.featured || '').toLowerCase().trim(); // '', city, county, state
    const premium = truthy(r.premium);
    const claimed = truthy(r.claimed);
    const bestOfRank = int(r.best_of_rank) || 0;
    const reviews = int(r.reviews);
    const rating = num(r.rating);
    const description = r.description_enriched || r.description || '';
    const thin = r.thin ? truthy(r.thin) : reviews < 5 || !description;
    const optimized = Boolean(featured) || (claimed && premium);
    const photos = optimized && r.photos ? r.photos.split(/[|,]/).map((s) => s.trim()).filter(Boolean) : [];
    const hours = parseHours(r.working_hours);
    return {
      name: r.name, slug, city, citySlug, stateCode: r.state_code || site.state.code, postalCode: r.postal_code,
      county: r.county, address: r.address, street: r.street, phone: r.phone, website: r.website,
      lat: num(r.latitude), lng: num(r.longitude), rating, reviews, reviewsTags: r.reviews_tags,
      socials: (r.socials || '').split('|').map((s) => s.trim()).filter(Boolean).map((s) => { const i = s.indexOf('='); return i > 0 ? { network: s.slice(0, i), url: s.slice(i + 1) } : null; }).filter(Boolean),
      type: r.type, subtypes: r.subtypes, description, hours, verifiedOnGoogle: truthy(r.verified),
      mapLink: r.location_link || '', areaService: truthy(r.area_service), placeId: r.place_id,
      featured, featuredCities: (r.featured_cities || '').split(/[|,]/).map((s) => s.trim()).filter(Boolean),
      premium, claimed, bestOfRank, thin, optimized, photos, attrs,
      path: `${CO}/${citySlug}/${slug}/`,
      cityPath: `${DIR}/${citySlug}/`,
      score: rating * Math.log10(reviews + 1),
      // `owned` is intentionally not read here. It must never change rendering (footprint-rules.md).
    };
  });

  // Cities: floor, fold under-floor cities into the nearest city with a page
  const byCity = new Map();
  for (const l of listings) {
    if (!byCity.has(l.citySlug)) byCity.set(l.citySlug, { slug: l.citySlug, name: l.city, listings: [] });
    byCity.get(l.citySlug).listings.push(l);
  }
  const all = [...byCity.values()].map((c) => ({ ...c, lat: avg(c.listings.map((l) => l.lat)), lng: avg(c.listings.map((l) => l.lng)) }));
  const floor = site.cityFloor || 3;
  const pages = all.filter((c) => c.listings.length >= floor);
  const folded = all.filter((c) => c.listings.length < floor);
  // foldMaxKm (site.json, optional): an under-floor city further than this from every city page
  // is not folded. It gets a page of its own, indexed and in the sitemap like any city page (Shawn,
  // 2026-09-29), listed under "Smaller towns" on the state hub and left out of the navigation.
  const foldMaxKm = Number(site.foldMaxKm) || Infinity;
  const remote = [];
  for (const f of folded) {
    let best = null, bd = Infinity;
    for (const p of pages) { const d = haversine(f, p); if (d < bd) { bd = d; best = p; } }
    if (best && bd > foldMaxKm) { remote.push({ ...f, underFloor: true }); continue; }
    if (best) {
      for (const l of f.listings) {
        l.foldedFrom = l.city; l.citySlug = best.slug; l.city = best.name;
        l.path = `${CO}/${best.slug}/${l.slug}/`; l.cityPath = `${DIR}/${best.slug}/`;
        best.listings.push(l);
      }
    }
  }
  const sortAttr = site.sortAttribute || '';
  const cities = [...pages, ...remote].map((c) => {
    const sorted = sortListings(c.listings, c.slug, sortAttr);
    const copy = cityCopy[c.slug] || null;
    const path = `${DIR}/${c.slug}/`;
    return {
      ...c, listings: sorted, path, copy, underFloor: Boolean(c.underFloor),
      count: sorted.length,
      featured: sorted.filter((l) => isFeaturedIn(l, c.slug)),
      bestOf: sorted.filter((l) => l.bestOfRank > 0),
      title: `${site.niche.title} in ${c.name}, ${site.state.code}`,
      avgRating: avg(sorted.filter((l) => l.reviews > 0).map((l) => l.rating)),
      totalReviews: sorted.reduce((s, l) => s + l.reviews, 0),
      attrCounts: Object.fromEntries(attributes.map((a) => [a.key, sorted.filter((l) => attrValue(l, a.key) === 'true').length])),
    };
  }).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
  // indexCities: the cities that clear the floor. Navigation, the home grid and the counts use these.
  const indexCities = cities.filter((c) => !c.underFloor);
  for (const c of cities) {
    c.nearby = indexCities.filter((o) => o !== c).map((o) => ({ o, d: haversine(c, o) })).sort((x, y) => x.d - y.d).slice(0, 5).map((x) => x.o);
  }
  const cityBySlug = Object.fromEntries(cities.map((c) => [c.slug, c]));
  // Related listings: every listing page links the next four in its city's order, wrapping at the end, so
  // each listing page is linked from four others and none is a dead end. A town with a single listing
  // borrows the top of the nearest city page.
  for (const l of listings) l.related = [];
  for (const c of cities) {
    const n = c.listings.length;
    c.listings.forEach((l, i) => {
      l.related = n > 1 ? Array.from({ length: Math.min(4, n - 1) }, (_, k) => c.listings[(i + 1 + k) % n])
        : (c.nearby[0] ? c.nearby[0].listings.slice(0, 4) : []);
    });
  }
  // Service pages (/services/<slug>/): one per attribute that carries a `service` block in attributes.json
  // ({ title, slug, intro }) and that at least the city floor of listings confirm. No block, no page.
  const services = attributes.filter((a) => a.service && a.service.title).map((a) => {
    const confirmed = listings.filter((l) => attrValue(l, a.key) === 'true').sort((x, y) => y.score - x.score || x.name.localeCompare(y.name));
    const slug = a.service.slug || slugify(a.key);
    return {
      key: a.key, label: a.label, slug, title: a.service.title, intro: a.service.intro || [], path: `/services/${slug}/`,
      listings: confirmed, count: confirmed.length,
      cities: cities.map((c) => ({ city: c, count: c.attrCounts[a.key] || 0 })).filter((x) => x.count > 0).sort((x, y) => y.count - x.count || x.city.name.localeCompare(y.city.name)),
    };
  }).filter((s) => s.count >= floor);
  const missingCopy = cities.filter((c) => !c.copy).map((c) => c.slug);   // every page that renders, small towns included
  if (missingCopy.length && process.env.NODE_ENV !== 'test') {
    console.warn(`[directory] ${missingCopy.length} city page(s) have no entry in city-copy.json and fall back to data-driven copy: ${missingCopy.join(', ')}`);
  }

  const stateFeatured = listings.filter((l) => l.featured === 'state');
  let homeFeatured = [...stateFeatured, ...listings.filter((l) => l.featured === 'county'), ...listings.filter((l) => l.featured === 'city')]
    .filter((l, i, arr) => arr.indexOf(l) === i).slice(0, 6);
  // Design preview (site.featuredPreview): unsold positions show the best real listings, flagged `preview` so the
  // cards carry data-preview and scripts/check_live.py refuses a live site that still shows them. Off at launch.
  if (site.featuredPreview) {
    const best = (list) => [...list].filter((l) => !l.featured && !l.thin && l.reviews >= 25 && l.rating >= 4.5 && (!sortAttr || attrValue(l, sortAttr) === 'true'))
      .sort((a, b) => b.score - a.score);
    // Two of the three positions, so the open-position card stays visible.
    const fill = (have, list) => [...have, ...best(list).filter((l) => !have.includes(l)).slice(0, Math.max(0, 2 - have.length))];
    homeFeatured = fill(homeFeatured, listings);
    homeFeatured.forEach((l) => { if (!l.featured) l.preview = true; });
    for (const c of cities) { c.featured = fill(c.featured, c.listings); c.featured.forEach((l) => { if (!l.featured) l.preview = true; }); }
  }

  // Launch lean: what stays out of the sitemap and gets noindex
  const noindexPaths = new Set();
  for (const l of listings) if (l.thin && !l.claimed && !l.optimized) noindexPaths.add(l.path);
  for (const l of listings) if (l.premium || l.bestOfRank) noindexPaths.add(`/badge/${l.slug}/`);
  for (const p of ['/claim/', '/featured/', '/privacy/', '/terms/', '/contact/', '/search/', '/directory/']) noindexPaths.add(p);

  const stats = {
    listings: listings.length, cities: indexCities.length,
    reviews: listings.reduce((s, l) => s + l.reviews, 0),
    sortAttrTrue: sortAttr ? listings.filter((l) => attrValue(l, sortAttr) === 'true').length : 0,
    sortAttrLabel: sortAttr ? (attributes.find((a) => a.key === sortAttr) || {}).label || '' : '',
    // Directory-wide count of listings answering true per attribute, for copy that cites the data.
    attr: Object.fromEntries(attributes.map((a) => [a.key, listings.filter((l) => attrValue(l, a.key) === 'true').length])),
  };
  cache = { site, attributes, listings, cities, indexCities, services, stats, cityBySlug, homeFeatured, noindexPaths, missingCopy, stateSlug,
    statePath: `${DIR}/`, buildDate: new Date().toISOString().slice(0, 10) };
  return cache;
}

function avg(xs) { const v = xs.filter((x) => Number.isFinite(x) && x !== 0); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : 0; }
function normalizeAttr(v) {
  const s = (v || '').trim().toLowerCase();
  if (!s) return 'not enough info';
  if (/^(true|yes|y|1)$/.test(s)) return 'true';
  if (/^(false|no|n|0)$/.test(s)) return 'false';
  return 'not enough info';
}
export function attrValue(l, key) { return (l.attrs.find((a) => a.key === key) || {}).value || 'not enough info'; }
export function isFeaturedIn(l, citySlug) {
  if (l.featured === 'state') return true;
  if (l.featured === 'county') return l.featuredCities.includes(citySlug) || l.citySlug === citySlug;
  if (l.featured === 'city') return l.citySlug === citySlug;
  return false;
}
// City page order: featured first, then paid best-of positions, then listings where
// site.sortAttribute is true (when set), then everyone else. Within a group: rating x log(reviews).
export function sortListings(list, citySlug, sortAttr = '') {
  const rank = (l) => (isFeaturedIn(l, citySlug) ? 0 : l.bestOfRank ? 1 : sortAttr && attrValue(l, sortAttr) === 'true' ? 2 : 3);
  return [...list].sort((a, b) => rank(a) - rank(b) || (a.bestOfRank || 99) - (b.bestOfRank || 99) || b.score - a.score || a.name.localeCompare(b.name));
}
export function fillFaq(template, site, cityName) {
  return template.replace(/\{plural\}/g, site.niche.plural).replace(/\{singular\}/g, site.niche.singular).replace(/\{city\}/g, cityName).replace(/\{state\}/g, site.state.name);
}
// Fallback FAQs from attribute counts when city-copy.json has no entry (Gate 5 should replace these).
export function attributeFaqs(city, site, attributes, max = 5) {
  const out = [];
  for (const a of attributes) {
    const n = city.attrCounts[a.key] || 0;
    if (n === 0) continue;
    const names = city.listings.filter((l) => attrValue(l, a.key) === 'true').slice(0, 3).map((l) => l.name);
    out.push({ q: fillFaq(a.faq, site, city.name), a: `${n} of the ${city.count} ${site.niche.plural} listed in ${city.name} mention ${a.label.toLowerCase()}, including ${names.join(', ')}. Confirm the details with the business before you sign anything.` });
    if (out.length >= max) break;
  }
  return out;
}
export function topAttrs(l, n = 3) { return l.attrs.filter((a) => a.value === 'true').slice(0, n); }

// The Astro compiler does not accept <p> elements inside a .map() expression, so paragraph
// lists are rendered as one HTML string on the wrapper: <div set:html={paragraphs(list)}></div>
export function escapeHtml(s) { return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
export function paragraphs(list) { return (list || []).filter(Boolean).map((t) => `<p>${escapeHtml(t)}</p>`).join('\n'); }

// Link the first mention of each listed business in a block of copy to its listing page. Names are
// matched whole, longest first, so "Acme Fence Inc" is not caught by "Acme Fence". Returns HTML.
export function linkNames(text, listings) {
  const names = [...listings].filter((l) => l.name && l.name.length > 3).sort((a, b) => b.name.length - a.name.length);
  const parts = [{ t: text, html: false }];
  for (const l of names) {
    const rx = new RegExp(`(^|[^A-Za-z0-9&])(${l.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})(?![A-Za-z0-9])`);
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      if (p.html) continue;
      const m = rx.exec(p.t);
      if (!m) continue;
      const at = m.index + m[1].length;
      parts.splice(i, 1, { t: p.t.slice(0, at), html: false }, { t: `<a href="${l.path}">${escapeHtml(l.name)}</a>`, html: true }, { t: p.t.slice(at + l.name.length), html: false });
      break;
    }
  }
  return parts.map((p) => (p.html ? p.t : escapeHtml(p.t))).join('');
}
export function linkedParagraphs(list, listings) { return (list || []).filter(Boolean).map((t) => `<p>${linkNames(t, listings)}</p>`).join('\n'); }

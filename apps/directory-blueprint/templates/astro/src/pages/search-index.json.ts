import type { APIRoute } from 'astro';
import { loadDirectory, attrValue } from '../lib/load.mjs';

// The search index for public/search.js: every listing and every city page, small fields only.
// Built once per build, fetched by the browser the first time a visitor touches the search box.
export const GET: APIRoute = () => {
  const dir = loadDirectory();
  const cities = dir.cities.map((c) => ({ n: c.name, p: c.path, c: c.count, lat: Number(c.lat.toFixed(4)), lng: Number(c.lng.toFixed(4)) }));
  const listings = dir.listings.map((l) => ({
    n: l.name, p: l.path, c: l.city, t: l.foldedFrom && l.foldedFrom !== l.city ? l.foldedFrom : '',
    r: l.rating, v: l.reviews, a: dir.attributes.filter((a) => attrValue(l, a.key) === 'true').map((a) => a.label),
  }));
  return new Response(JSON.stringify({ cities, listings }), { headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=3600' } });
};

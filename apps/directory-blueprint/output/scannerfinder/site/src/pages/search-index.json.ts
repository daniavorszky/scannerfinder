import type { APIRoute } from 'astro';
import { loadDirectory, attrValue } from '../lib/load.mjs';

// The search index for public/search.js: every listing (town, region, country) and every country and region page, small fields only.
// Built once per build, fetched by the browser the first time a visitor touches the search box.
export const GET: APIRoute = () => {
  const dir = loadDirectory();
  // Places for the location box: the countries first (k: 1, never picked by "near me"), then every region page.
  const cities = [
    ...dir.countries.map((co) => ({ n: co.name, p: co.path, c: co.count, k: 1 })),
    ...dir.cities.map((c) => ({ n: c.name, p: c.path, c: c.count, lat: Number(c.lat.toFixed(4)), lng: Number(c.lng.toFixed(4)) })),
  ];
  const listings = dir.listings.map((l) => ({
    n: l.name, p: l.path, c: l.city, t: l.foldedFrom && l.foldedFrom !== l.city ? l.foldedFrom : '', g: l.region, k: l.country.name, o: l.logo,
    la: Number((l.lat || 0).toFixed(3)), lo: Number((l.lng || 0).toFixed(3)),
    r: l.rating, v: l.reviews, a: dir.attributes.filter((a) => attrValue(l, a.key) === 'true').map((a) => a.label),
  }));
  return new Response(JSON.stringify({ cities, listings }), { headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=3600' } });
};

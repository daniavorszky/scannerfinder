// Gate 5 helper: write the city structure exactly as the site will build it (folds included),
// so the city copy is written from the same membership the pages show.
//
// Usage: node dump-cities.mjs [zip-county.json] <out.json>
//   zip-county.json (optional): a JSON object mapping five-digit ZIP codes to county names,
//   { "80202": "Denver County", ... }, built from a public ZIP-to-county table. When it is given, a
//   listing's county comes from its ZIP; without it the CSV's own `county` column is used (blank on a
//   DataForSEO pull, and on Outscraper rows it can hold a neighborhood name instead of a county).
import fs from 'node:fs';
import { loadDirectory, attrValue } from './src/lib/load.mjs';
const args = process.argv.slice(2);
if (args.length < 1 || args.length > 2) {
  console.error('usage: node dump-cities.mjs [zip-county.json] <out.json>');
  process.exit(2);
}
const outPath = args[args.length - 1];
const zipCounty = args.length === 2 ? JSON.parse(fs.readFileSync(args[0], 'utf8')) : null;
if (!zipCounty) console.log('note: no ZIP-to-county file given; counties come from the CSV\'s county column (empty on a DataForSEO pull)');
const countyOf = (l) => (zipCounty && zipCounty[(l.postalCode || '').slice(0, 5)]) || l.county || '';
process.env.NODE_ENV = 'test';
const dir = loadDirectory();
const out = dir.cities.map((c) => ({
  slug: c.slug, name: c.name, count: c.count, underFloor: c.underFloor, path: c.path,
  avgRating: Number(c.avgRating.toFixed(2)), totalReviews: c.totalReviews, attrCounts: c.attrCounts,
  nearby: c.nearby.map((n) => ({ name: n.name, count: n.count })),
  listings: c.listings.map((l, i) => ({
    position: i + 1, name: l.name, slug: l.slug, rating: l.rating, reviews: l.reviews, thin: l.thin,
    basedIn: l.foldedFrom || '', county: countyOf(l),
    serviceArea: l.areaService, hasWebsite: Boolean(l.website), hasHours: l.hours.length > 0,
    yes: dir.attributes.filter((a) => attrValue(l, a.key) === 'true').map((a) => a.key),
    no: dir.attributes.filter((a) => attrValue(l, a.key) === 'false').map((a) => a.key),
    description: l.description,
  })),
}));
fs.writeFileSync(outPath, JSON.stringify(out));
const withCounty = out.reduce((s, c) => s + c.listings.filter((l) => l.county).length, 0);
console.log(`cities: ${out.length}, with a page in the index: ${out.filter((c) => !c.underFloor).length}, listings: ${out.reduce((s, c) => s + c.count, 0)}, with a county: ${withCounty}`);

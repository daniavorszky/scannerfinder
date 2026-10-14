// Badge SVG per premium or best-of listing (templates/featured-tiers.md). Owners embed it; it links back.
import type { APIRoute } from 'astro';
import { loadDirectory } from '../../lib/load.mjs';
export function getStaticPaths() {
  const { listings } = loadDirectory();
  return listings.filter((l) => l.premium || l.bestOfRank).map((l) => ({ params: { slug: l.slug } }));
}
export const GET: APIRoute = ({ params }) => {
  const { site, listings, buildDate } = loadDirectory();
  const l = listings.find((x) => x.slug === params.slug)!;
  const d = site.design;
  const line1 = l.bestOfRank ? `Best ${site.niche.title} in ${l.city} ${buildDate.slice(0, 4)}` : `Verified ${site.niche.singular}`;
  const line2 = l.bestOfRank ? site.brand : `on ${site.brand}`;
  const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="220" height="64" viewBox="0 0 220 64" role="img" aria-label="${esc(line1)} ${esc(line2)}">
  <rect width="220" height="64" rx="8" fill="${d.accent}"/>
  <text x="14" y="28" font-family="${esc(d.bodyFont)}" font-size="13" font-weight="700" fill="${d.accentText}">${esc(line1)}</text>
  <text x="14" y="48" font-family="${esc(d.bodyFont)}" font-size="12" fill="${d.accentText}">${esc(line2)}</text>
</svg>`;
  return new Response(svg, { headers: { 'Content-Type': 'image/svg+xml' } });
};

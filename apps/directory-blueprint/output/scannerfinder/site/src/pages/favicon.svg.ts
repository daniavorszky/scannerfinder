// Default favicon: the first letter of the brand on the header color, drawn from the design tokens.
// To use a file of your own, put it in public/ and set design.favicon in site.json to its path.
import type { APIRoute } from 'astro';
import { loadDirectory } from '../lib/load.mjs';
export const GET: APIRoute = () => {
  const { site } = loadDirectory();
  const d = site.design;
  const letter = ((d.logoText || site.brand || '').trim()[0] || 'D').toUpperCase().replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="${d.headerBg || d.band || d.accent}"/>
  <text x="32" y="46" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="42" font-weight="700" fill="${d.action || d.accentText}">${letter}</text>
</svg>`;
  return new Response(svg, { headers: { 'Content-Type': 'image/svg+xml' } });
};

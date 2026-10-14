import type { APIRoute } from 'astro';
import { loadSite } from '../lib/load.mjs';
export const GET: APIRoute = () => {
  const site = loadSite();
  return new Response(`User-agent: *\nAllow: /\n\nSitemap: https://${site.domain}/sitemap-index.xml\n`, { headers: { 'Content-Type': 'text/plain' } });
};

import type { APIRoute } from 'astro';
import { loadDirectory } from '../lib/load.mjs';
import { loadPosts } from '../lib/blog.mjs';
import tools from '../data/tools.json';

// /llms.txt (llmstxt.org format): a plain-text map of the site for AI assistants, built from the same data as
// the pages, so it never drifts. Cheap insurance, not an SEO lever (2026-10-14: AI crawlers mostly read the HTML).
// Lists: what ScannerFinder is, the main guides, countries, technologies, tools, real blog posts, policies.
export const GET: APIRoute = () => {
  const dir = loadDirectory();
  const { site, countries, devices, buildDate } = dir;
  const base = `https://${site.domain}`;
  const total = dir.listings.length;
  const link = (title: string, path: string, note = '') => `- [${title}](${base}${path})${note ? `: ${note}` : ''}`;
  const posts = loadPosts().filter((p: any) => !p.placeholder && !p.draft);
  const lines = [
    `# ${site.brand}`,
    '',
    `> ${site.brand} is an independent directory of ${total.toLocaleString('en-US')} ${site.niche.plural} in ${countries.length} countries, searchable by scanning device (ZYTO, BICOM, AO Scan, Asyra and more) and by region. Each listing shows the device the practitioner names, Google rating and review count, services such as remote sessions, and contact details taken from public records and the business's own website. Scan sessions are wellness services, not medical tests.`,
    '',
    `Published by ${site.publisher.legalName || site.publisher.name} (${site.publisher.url}). Data updated ${buildDate}. Basic listings are free; paid placements are labelled as featured, premium or best-of and never change the organic ranking, which is Google rating weighted by review count.`,
    '',
    '## Guides',
    link('What bioresonance is', '/bioresonance/', 'how the sessions work and what the evidence says'),
    link('Does bioresonance work?', '/bioresonance/does-it-work/', 'what published studies show'),
    link('Bioresonance machines', '/bioresonance-machines/', 'device types, prices and a buyer\'s guide'),
    link(`Best ${site.niche.plural} in ${buildDate.slice(0, 4)}`, '/best-practitioners/', 'top-rated practitioners per country'),
    link(`Bioresonance practitioner statistics ${buildDate.slice(0, 4)}`, '/statistics/', 'original data: which device leads in each country, remote sessions, practice types; CSV at /statistics.csv'),
    '',
    '## Countries',
    ...countries.map((c: any) => link(`${site.niche.title} in ${c.inName}`, c.path, `${c.count} listed${c.cities?.length ? `, ${c.cities.length} regions` : ''}`)),
    '',
    '## Technologies',
    ...devices.map((d: any) => link(`${d.label} practitioners`, d.path, `${d.count} listed in ${d.byCountry.length} ${d.byCountry.length === 1 ? 'country' : 'countries'}`)),
    '',
    ...(tools.length ? ['## Tools', ...tools.map((t: any) => link(t.title, t.path, t.description)), ''] : []),
    ...(posts.length ? ['## Articles', ...posts.map((p: any) => link(p.title, p.path, p.description)), ''] : []),
    '## Search and listings',
    link('Search practitioners', '/search/', 'by technology, region or town, and name'),
    link('Every country and region', '/directory/'),
    link('Claim or correct a listing', '/claim/', 'free for practitioners'),
    '',
    '## Optional',
    link('About', '/about/', 'who publishes the directory and how listings are vetted'),
    link('Affiliate disclosure', '/affiliate-disclosure/', 'how the site earns money'),
    link('Privacy policy', '/privacy/'),
    link('Terms of use', '/terms/'),
    link('Contact', '/contact/'),
    '',
  ];
  return new Response(lines.join('\n'), { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};

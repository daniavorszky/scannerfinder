import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import fs from 'node:fs';
import { loadSite, loadDirectory } from './src/lib/load.mjs';


// Launch lean (wiki/seo/launch-lean.md): thin listing pages, badge snippet pages and
// the claim/featured/legal pages are built but kept out of the sitemap. The pages
// themselves set <meta name="robots" content="noindex"> from the same data.
const site = loadSite();
const dir = loadDirectory();
const noindex = dir.noindexPaths; // Set of absolute paths like "/fl/orlando/acme-pools-orlando/"
// The resources index stays out of the sitemap until a real resource page exists.
const resources = fs.existsSync('./src/pages/resources') ? fs.readdirSync('./src/pages/resources').filter((f) => f.endsWith('.md') && !f.startsWith('_')) : [];
if (resources.length === 0) noindex.add('/resources/');
// Same for the tools index until src/data/tools.json lists a tool.
if (JSON.parse(fs.readFileSync('./src/data/tools.json', 'utf8')).length === 0) noindex.add('/tools/');
// Blog: draft and placeholder posts stay out of the sitemap, and so does /blog/ until one real post exists.
const blogDir = './src/content/blog';
const blogPosts = fs.existsSync(blogDir) ? fs.readdirSync(blogDir).filter((f) => f.endsWith('.md') && !f.startsWith('_')).map((f) => ({ slug: f.slice(0, -3), fm: fs.readFileSync(`${blogDir}/${f}`, 'utf8').split('---')[1] || '' })) : [];
const hidden = (p) => /^\s*(draft|placeholder):\s*true\s*$/m.test(p.fm);
blogPosts.filter(hidden).forEach((p) => noindex.add(`/blog/${p.slug}/`));
if (!blogPosts.some((p) => !hidden(p))) noindex.add('/blog/');
// Cloudflare Pages reads dist/_redirects. /company/ on its own goes to the directory index, and a
// /company/<state>/<city>/ address (no business) goes to that city's directory page. /directory/ is a real page.
// ScannerFinder: one pair of rules per country (04-plan.md).
fs.writeFileSync('./public/_redirects', [`/company /directory/ 301`, `/company/ /directory/ 301`,
  ...dir.countries.flatMap((c) => [`/company/${c.slug}/ ${c.path} 301`, `/company/${c.slug}/:city/ ${c.path}:city/ 301`]),
  // One-off moves of pages that were live (add here, never in public/_redirects, which this rewrites).
  `/directory/south-africa/north-west-province/north-west-province/ /directory/south-africa/north-west-province/rustenburg/ 301`,   // 2026-10-14, town fixed in data
  `/directory/romania/bucharest/bucuresti-sector-4/ /directory/romania/bucharest/bucharest/ 301`,   // 2026-10-14, Sector 4 dropped from the address
].join('\n') + '\n');

export default defineConfig({
  site: `https://${site.domain}`,
  trailingSlash: 'always',
  build: { format: 'directory' },

  integrations: [
    sitemap({
      filter: (page) => {
        const path = new URL(page).pathname;
        return !noindex.has(path);
      },
    }),
  ]
});
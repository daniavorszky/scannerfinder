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
// Cloudflare Pages reads dist/_redirects. /company/ on its own goes to the directory index, and a
// /company/<state>/<city>/ address (no business) goes to that city's directory page. /directory/ is a real page.
const co = dir.statePath.replace('/directory/', '/company/');
fs.writeFileSync('./public/_redirects', [`/company /directory/ 301`, `/company/ /directory/ 301`,
  `${co} ${dir.statePath} 301`, `${co}:city/ ${dir.statePath}:city/ 301`].join('\n') + '\n');

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
  ],
});

// Blog posts: one Markdown file per article in src/content/blog/<slug>.md (layout: src/pages/blog/).
// Frontmatter: title, description, category, tags[], author, published (YYYY-MM-DD), updated, image (optional),
// takeaways[] (Key Takeaways box), faqs[{ q, a }], draft (true = local preview only, never built for production),
// placeholder (true = built but noindex and out of the sitemap, e.g. lorem ipsum layout fillers).
const mods = import.meta.glob('../content/blog/*.md', { eager: true });

export function loadPosts() {
  return Object.entries(mods).map(([file, m]) => {
    const slug = file.split('/').pop().replace(/\.md$/, '');
    const fm = m.frontmatter || {};
    const words = (m.rawContent ? m.rawContent() : '').split(/\s+/).filter(Boolean).length;
    return {
      slug, path: `/blog/${slug}/`, Content: m.Content, headings: m.getHeadings ? m.getHeadings() : [],
      title: fm.title, description: fm.description || '', category: fm.category || 'Guides', tags: fm.tags || [],
      author: fm.author || 'ScannerFinder Editorial Team', published: String(fm.published || ''), updated: String(fm.updated || fm.published || ''),
      image: fm.image || '', takeaways: fm.takeaways || [], faqs: fm.faqs || [], draft: !!fm.draft, placeholder: !!fm.placeholder,
      readMinutes: Math.max(1, Math.round(words / 220)),
    };
  })
    .filter((p) => !p.slug.startsWith('_') && (!p.draft || import.meta.env.DEV))
    .sort((a, b) => b.published.localeCompare(a.published));
}

export function formatDate(iso) {
  const d = new Date(iso + 'T12:00:00Z');
  return isNaN(d) ? iso : d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
}

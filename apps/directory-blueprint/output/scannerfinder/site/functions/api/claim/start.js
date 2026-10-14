// POST /api/claim/start — step 1: who is claiming which listing. Sends a one-hour confirmation link.
import { json, readJson, str, isEmail, isUrl, now, esc } from '../../_lib/util.js';
import { listing, ownershipMethod, createToken } from '../../_lib/claim.js';
import { sendMail, mailHtml } from '../../_lib/mail.js';

const ROLES = new Set(['owner', 'practitioner', 'manager', 'other']);

export async function onRequestPost({ request, env }) {
  const b = await readJson(request);
  if (!b) return json({ ok: false, error: 'bad_request' }, 400);
  if (b.website_hp) return json({ ok: true }); // honeypot: pretend success
  const email = str(b.email, 254).toLowerCase(), name = str(b.name, 120), role = ROLES.has(b.role) ? b.role : 'other';
  const slug = str(b.slug, 120), l = listing(slug);
  const np = b.new_practice || null;
  if (!isEmail(email) || name.length < 2) return json({ ok: false, error: 'missing_fields' }, 400);
  if (!l && !(np && str(np.name, 160).length >= 2 && str(np.city, 120))) return json({ ok: false, error: 'pick_listing' }, 400);
  if (np && !isUrl(str(np.website, 300))) return json({ ok: false, error: 'bad_website' }, 400);

  // At most 3 confirmation emails per address per hour.
  const recent = await env.DB.prepare("SELECT count(*) AS n FROM claims WHERE email = ?1 AND updated_at > ?2")
    .bind(email, new Date(Date.now() - 3600000).toISOString()).first();
  if (recent.n >= 3) return json({ ok: false, error: 'rate_limited' }, 429);

  const method = await ownershipMethod(l, email);
  const details = JSON.stringify({
    new_practice: l ? undefined : { name: str(np.name, 160), city: str(np.city, 120), country: str(np.country, 60), website: str(np.website, 300) },
    featured_interest: b.tier ? str(b.tier, 40) : undefined,
    note: str(b.note, 1000) || undefined,
  });
  const existing = l ? await env.DB.prepare("SELECT id FROM claims WHERE listing_slug = ?1 AND email = ?2 AND status NOT IN ('rejected')").bind(slug, email).first() : null;
  const id = existing?.id || crypto.randomUUID();
  if (existing) {
    await env.DB.prepare('UPDATE claims SET name = ?2, role = ?3, details = ?4, updated_at = ?5 WHERE id = ?1').bind(id, name, role, details, now()).run();
  } else {
    await env.DB.prepare('INSERT INTO claims (id, listing_slug, status, email, name, role, verify_method, details, created_at, updated_at) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?9)')
      .bind(id, l ? slug : null, 'pending', email, name, role, method, details, now()).run();
  }

  const token = await createToken(env, id, 'magic_link', 60);
  const link = `${env.SITE_URL}/claim/verify/?t=${token}`;
  const business = l ? l.n : str(np.name, 160);
  const sent = await sendMail(env, {
    to: email,
    subject: `Confirm your ScannerFinder listing: ${business}`,
    text: `Hi ${name},\n\nConfirm your email to claim ${business} on ScannerFinder:\n${link}\n\nThe link works for one hour. If you did not ask for this, ignore this email.\n\nScannerFinder.com`,
    html: mailHtml([`Hi ${esc(name)},`, `Confirm your email to claim <b>${esc(business)}</b> on ScannerFinder. The link works for one hour.`, 'If you did not ask for this, ignore this email.'], { href: link, label: 'Confirm and continue' }),
  });
  // 424, not 5xx: Cloudflare replaces 5xx bodies from Functions with its own page, and the form needs the JSON.
  if (!sent.ok) return json({ ok: false, error: 'mail_failed' }, 424);
  return json({ ok: true, dev_link: sent.dev ? link : undefined });
}

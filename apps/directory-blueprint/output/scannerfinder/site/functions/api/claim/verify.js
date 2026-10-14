// POST /api/claim/verify {t} — swaps the one-time email link for a 30-day session cookie.
// POST, not GET: mail scanners open links in emails, and a GET would burn the token before the person clicks.
import { json, readJson, now, esc } from '../../_lib/util.js';
import { tokenClaim, createToken, sessionCookie, listing } from '../../_lib/claim.js';
import { sendMail } from '../../_lib/mail.js';

export async function onRequestPost({ request, env }) {
  const b = await readJson(request);
  const c = await tokenClaim(env, b?.t, 'magic_link');
  if (!c) return json({ ok: false, error: 'expired' }, 400);
  await env.DB.prepare('DELETE FROM sessions WHERE token_hash = ?1').bind(c.token_hash).run();
  if (c.status === 'pending') {
    const status = c.verify_method === 'manual' ? 'email_confirmed' : 'verified';
    await env.DB.prepare('UPDATE claims SET status = ?2, updated_at = ?3 WHERE id = ?1').bind(c.id, status, now()).run();
    const l = listing(c.listing_slug);
    const what = l ? `${l.n} (${l.c}, ${l.co}) ${env.SITE_URL}${l.p}` : `NEW PRACTICE ${c.details}`;
    await sendMail(env, {
      to: env.ADMIN_EMAIL,
      subject: `[ScannerFinder] Claim ${status === 'verified' ? 'verified' : 'needs a check'}: ${l ? l.n : 'new practice'}`,
      text: `${what}\nBy: ${c.name} <${c.email}> (${c.role})\nOwnership: ${c.verify_method}${status === 'email_confirmed' ? ' (call the number on Google to confirm)' : ''}\nClaim id: ${c.id}`,
    });
  }
  const session = await createToken(env, c.id, 'session', 30 * 24 * 60);
  return json({ ok: true }, 200, { 'set-cookie': sessionCookie(session, 30) });
}

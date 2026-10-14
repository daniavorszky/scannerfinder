// GET /api/claim/me — the signed-in claim, its listing as we show it, what we found on their site,
// and their latest submitted profile (to pre-fill step 2).
import { json } from '../../_lib/util.js';
import { tokenClaim, sessionFrom, listing } from '../../_lib/claim.js';

export async function onRequestGet({ request, env }) {
  const c = await tokenClaim(env, sessionFrom(request), 'session');
  if (!c) return json({ ok: false, error: 'signed_out' }, 401);
  const l = listing(c.listing_slug);
  const last = await env.DB.prepare('SELECT data, submitted_at FROM profile_public WHERE claim_id = ?1 ORDER BY version DESC LIMIT 1').bind(c.id).first();
  const { e, d, ...pub } = l || {};
  return json({
    ok: true,
    claim: { status: c.status, name: c.name, email: c.email, slug: c.listing_slug, details: JSON.parse(c.details || '{}') },
    listing: l ? pub : null,
    profile: last ? { ...JSON.parse(last.data), submitted_at: last.submitted_at } : null,
  });
}

// POST /api/claim/profile — step 2: the practitioner's corrections and the fields only they can give.
// Stored as a new version; nothing is published until the claim is approved and the site is rebuilt.
import { json, readJson, str, isUrl, now } from '../../_lib/util.js';
import { tokenClaim, sessionFrom, listing } from '../../_lib/claim.js';
import { sendMail } from '../../_lib/mail.js';

const DEVICES = ['ZYTO', 'BICOM', 'SCIO/Indigo/Eductor', 'Rayonex', 'NLS', 'Asyra/Qest4', 'AO Scan', 'TimeWaver', 'NES Health', 'MORA'];
const CURRENCIES = new Set(['USD', 'GBP', 'EUR', 'RON', 'CAD', 'AUD', 'NZD', 'ZAR', 'CHF']);
const price = (v) => { const n = Number.parseFloat(v); return Number.isFinite(n) && n > 0 && n < 100000 ? Math.round(n * 100) / 100 : null; };
const int = (v, max) => { const n = Number.parseInt(v, 10); return Number.isFinite(n) && n > 0 && n <= max ? n : null; };
const yesNo = (v) => (v === 'yes' ? true : v === 'no' ? false : null);

export async function onRequestPost({ request, env }) {
  const c = await tokenClaim(env, sessionFrom(request), 'session');
  if (!c) return json({ ok: false, error: 'signed_out' }, 401);
  const b = await readJson(request);
  if (!b) return json({ ok: false, error: 'bad_request' }, 400);
  const k = b.consents || {};
  if (!(k.wellness && k.accurate && k.terms)) return json({ ok: false, error: 'consents' }, 400);
  const urls = { website: str(b.website, 300), booking_url: str(b.booking_url, 300), certification_url: str(b.certification_url, 300) };
  if (!Object.values(urls).every(isUrl)) return json({ ok: false, error: 'bad_url' }, 400);

  const data = {
    business_name: str(b.business_name, 160), phone: str(b.phone, 40), ...urls,
    devices: (Array.isArray(b.devices) ? b.devices : []).filter((d) => DEVICES.includes(d)),
    device_other: str(b.device_other, 160), device_models: str(b.device_models, 200),
    currency: CURRENCIES.has(b.currency) ? b.currency : null,
    session_price: price(b.session_price), followup_price: price(b.followup_price), package_note: str(b.package_note, 200),
    session_minutes: int(b.session_minutes, 600),
    // Decided 2026-10-14 (Dan): prices are private by default; public only on the practitioner's explicit choice.
    price_public: b.price_visibility === 'public' ? true : b.price_visibility === 'private' ? false : null,
    remote_sessions: yesNo(b.remote_sessions), free_consultation: yesNo(b.free_consultation),
    description: str(b.description, 800), corrections: str(b.corrections, 1000),
  };
  if (data.session_price && !data.currency) return json({ ok: false, error: 'currency' }, 400);
  if ((data.session_price || data.followup_price) && data.price_public === null) return json({ ok: false, error: 'price_visibility' }, 400);
  const consents = JSON.stringify({ wellness: true, accurate: true, terms: true, marketing: !!k.marketing, at: now() });
  const v = await env.DB.prepare('SELECT coalesce(max(version), 0) + 1 AS v FROM profile_public WHERE claim_id = ?1').bind(c.id).first();
  await env.DB.prepare('INSERT INTO profile_public (claim_id, version, data, consents, submitted_at) VALUES (?1, ?2, ?3, ?4, ?5)')
    .bind(c.id, v.v, JSON.stringify(data), consents, now()).run();
  await env.DB.prepare('UPDATE claims SET updated_at = ?2 WHERE id = ?1').bind(c.id, now()).run();

  const l = listing(c.listing_slug);
  await sendMail(env, {
    to: env.ADMIN_EMAIL,
    subject: `[ScannerFinder] Profile v${v.v} to review: ${l ? l.n : data.business_name}`,
    text: `${l ? `${env.SITE_URL}${l.p}` : 'New practice'}\nClaim: ${c.id} (${c.status}, ${c.verify_method})\n\n${JSON.stringify(data, null, 2)}`,
  });
  return json({ ok: true, version: v.v });
}

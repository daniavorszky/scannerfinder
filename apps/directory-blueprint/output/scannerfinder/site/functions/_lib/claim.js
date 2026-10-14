// Claim flow helpers: listing lookup, ownership signal, sessions.
import data from '../_data/claim-data.json';
import { sha256, randomToken, inMinutes, now } from './util.js';

export const listing = (slug) => (slug && Object.prototype.hasOwnProperty.call(data, slug) ? data[slug] : null);

const FREEMAIL = /^(gmail|googlemail|yahoo|ymail|hotmail|outlook|live|msn|icloud|me|mac|aol|gmx|web|t-online|freenet|proton|protonmail|mail|yandex|zoho|bigpond|optusnet|xtra|btinternet|sky|virginmedia|shaw|telus|rogers|sympatico|comcast|verizon|att|sbcglobal|bellsouth|cox|charter|earthlink|yahoo\.co|hotmail\.co)\./i;

// How strongly the email ties the claimant to the listing: invite token > email we found on their site >
// work email on the website's own domain > nothing (manual check: phone call to the Google number).
export async function ownershipMethod(l, email) {
  if (!l) return 'manual';
  const e = email.toLowerCase();
  if (l.e.includes(await sha256(e))) return 'known_email';
  const domain = e.split('@')[1] || '';
  if (l.d && !FREEMAIL.test(domain + '.') && (domain === l.d || domain.endsWith('.' + l.d) || l.d.endsWith('.' + domain))) return 'domain_email';
  return 'manual';
}

export async function createToken(env, claimId, purpose, minutes) {
  const token = randomToken();
  await env.DB.prepare('INSERT INTO sessions (token_hash, claim_id, purpose, expires_at) VALUES (?1, ?2, ?3, ?4)')
    .bind(await sha256(token), claimId, purpose, inMinutes(minutes)).run();
  return token;
}

export async function tokenClaim(env, token, purpose) {
  if (!token || token.length > 100) return null;
  const h = await sha256(token);
  const row = await env.DB.prepare('SELECT s.token_hash, s.expires_at, c.* FROM sessions s JOIN claims c ON c.id = s.claim_id WHERE s.token_hash = ?1 AND s.purpose = ?2')
    .bind(h, purpose).first();
  if (!row || row.expires_at < now()) return null;
  return row;
}

export const SESSION_COOKIE = 'sf_claim';
export const sessionFrom = (request) => (request.headers.get('cookie') || '').split(/;\s*/).find((c) => c.startsWith(SESSION_COOKIE + '='))?.slice(SESSION_COOKIE.length + 1) || '';
export const sessionCookie = (token, days) => `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${days * 86400}`;

// Transactional email through Maileroo (notify.scannerfinder.com). Key: Pages secret MAILEROO_API_KEY.
// With MAIL_DEV=1 (local .dev.vars) nothing is sent; the message is logged instead.
export async function sendMail(env, { to, subject, text, html }) {
  if (env.MAIL_DEV === '1') { console.log(`[mail:dev] to=${to} subject=${subject}\n${text}`); return { ok: true, dev: true }; }
  if (!env.MAILEROO_API_KEY) return { ok: false, error: 'mail_not_configured' };
  let r;
  try {
    r = await fetch('https://smtp.maileroo.com/api/v2/emails', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'X-Api-Key': env.MAILEROO_API_KEY },
      body: JSON.stringify({
        from: { address: env.MAIL_FROM, display_name: 'ScannerFinder' },
        to: [{ address: to }],
        reply_to: { address: env.MAIL_REPLY_TO },
        subject, plain: text, html: html || undefined, tracking: false,
      }),
    });
  } catch (e) {
    console.log(`[mail] maileroo fetch failed: ${e && e.message}`);
    return { ok: false, error: 'maileroo_network' };
  }
  const body = await r.json().catch(() => ({}));
  const ok = r.ok && body.success !== false;
  // Logged without the key or the recipient, for `wrangler pages deployment tail`.
  if (!ok) console.log(`[mail] maileroo ${r.status}: ${body.message || JSON.stringify(body).slice(0, 300)}`);
  return { ok, error: ok ? undefined : `maileroo_${r.status}` };
}

// Minimal branded HTML around plain paragraphs; `cta` is one button.
export function mailHtml(paragraphs, cta) {
  const p = paragraphs.map((t) => `<p style="margin:0 0 14px">${t}</p>`).join('');
  const b = cta ? `<p style="margin:22px 0"><a href="${cta.href}" style="background:#0f766e;color:#fff;padding:12px 20px;border-radius:6px;text-decoration:none;font-weight:600">${cta.label}</a></p>` : '';
  return `<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;font-size:15px;line-height:1.5;color:#1f2937;max-width:560px">${p}${b}<p style="margin:24px 0 0;color:#6b7280;font-size:13px">ScannerFinder.com</p></div>`;
}

// GET /api/health → confirms the function runtime and the D1 binding work.
import { json } from '../_lib/util.js';

export async function onRequestGet({ env }) {
  try {
    const r = await env.DB.prepare("SELECT count(*) AS n FROM sqlite_master WHERE type = 'table'").first();
    return json({ ok: true, tables: r.n });
  } catch (e) {
    return json({ ok: false, error: 'db' }, 500);
  }
}

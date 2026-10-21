export async function rpc(name, body = {}) {
  const base = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_PUBLISHABLE_KEY;
  if (!base || !key) throw new Error('Database configuration missing');
  const url = new URL(`/rest/v1/rpc/${name}`, base);
  if (url.protocol !== 'https:') throw new Error('Database URL must use HTTPS');
  const result = await fetch(url.href, {
    method: 'POST',
    headers: { apikey: key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(20000)
  });
  if (!result.ok) throw new Error('Database request failed');
  return result.json();
}

export function readOnly(req, res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  if (req.method === 'GET') return true;
  res.setHeader('Allow', 'GET');
  res.setHeader('Cache-Control', 'no-store');
  res.status(405).json({ error: 'Method not allowed.' });
  return false;
}

export function unavailable(res) {
  res.setHeader('Cache-Control', 'no-store');
  return res.status(503).json({ error: 'Poetry database is temporarily unavailable.' });
}

import { rpc, readOnly, unavailable } from '../lib/supabase.js';

export default async function handler(req, res) {
  if (!readOnly(req, res)) return;
  const id = req.query?.id;
  if (typeof id !== 'string' || !/^guwendao-[a-f0-9]{12}$/.test(id)) {
    res.setHeader('Cache-Control', 'no-store');
    return res.status(400).json({ error: 'A valid poem ID is required.' });
  }
  try {
    const data = await rpc('song_ci_neighbors', { poem_id: id });
    if (!Array.isArray(data) || data.length === 0) {
      res.setHeader('Cache-Control', 'no-store');
      return res.status(404).json({ error: 'Poem not found.' });
    }
    res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    res.setHeader('Vercel-CDN-Cache-Control', 'max-age=300');
    return res.status(200).json(data);
  } catch {
    return unavailable(res);
  }
}

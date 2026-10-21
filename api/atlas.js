import { rpc, readOnly, unavailable } from '../lib/supabase.js';

export default async function handler(req, res) {
  if (!readOnly(req, res)) return;
  try {
    const data = await rpc('get_song_ci_atlas');
    // The database RPC deliberately returns no embedding vectors.
    if (!Array.isArray(data?.documents) || !Array.isArray(data?.neighbors)
        || !data?.coordinates?.tsne || !data?.coordinates?.umap) {
      throw new Error('Invalid atlas response');
    }
    res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    res.setHeader('Vercel-CDN-Cache-Control', 'max-age=300, stale-while-revalidate=600');
    return res.status(200).json(data);
  } catch {
    return unavailable(res);
  }
}

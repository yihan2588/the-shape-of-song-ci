# The shape of Song Ci / 词之形 — deployment

Live site: https://song-ci-atlas.vercel.app

The app source, data, and tooling are self-contained in this repository. Cloud
resource IDs and the existing production URL are retained across the rebrand.

- Vercel project: `song-ci-atlas` (`prj_LMWzqUdBn5q73xWuR9EevHb4s3O6`).
- Supabase project: `Song Ci Semantic Explorer` (`jjfqaqbhullbscimlnve`), US East.
- Dataset: 240 Song-era anthology entries, 96 canonical authors, from Guwendao.
- Embeddings: existing content-only Qwen3-Embedding-4B vectors, 2,560 dimensions,
  float32 and L2-normalized. No embedding-model service or API is required.

## Data flow

The browser loads `/api/atlas` on startup. A Vercel Node.js function calls
Supabase's `get_song_ci_atlas()` RPC using a publishable key stored in server
environment variables. Supabase returns poem text, source metadata, unchanged
t-SNE/UMAP coordinates, and exact global cosine top-three matches for every poem.
The browser renders those matches immediately when selecting a poem. Vercel's
CDN caches the response for five minutes, with ten minutes of stale revalidation.

`/api/neighbors?id=guwendao-…` provides a bounded single-poem lookup, also computed
in Supabase. Search remains title/text matching, as in the original explorer;
it does not generate new query embeddings.

In the hosted database, raw vectors live in `atlas_private.poems`, outside the exposed Data API
schema. Anonymous and authenticated roles have no schema/table access or writes.
The two public RPCs are intentionally read-only SECURITY DEFINER functions with
an empty search path, schema-qualified references, fixed outputs, and a statement
timeout. No service-role key is used or shipped to the browser. Supabase's advisor
flags these intentionally public definer functions and default-deny private RLS
tables; these findings do not indicate anonymous table access. Verify grants
when changing either function. At 240 rows, exact scans retain all dimensions
and need no approximate index.

## Local development

Use Node.js 24. No npm dependencies or frontend build are required.

```sh
cp .env.example .env.local
# Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in .env.local.
npm test
node tests/interactions.cjs
npm run check
npm run dev
```

The dev server listens on `http://127.0.0.1:3210` and uses the same API handlers
as Vercel. Loading failures display a bilingual retry screen.

## Database and deployment

`database/schema.sql` records the applied schema. Supabase MCP manages remote
migration history. `scripts/prepare_seed.py <scratch-directory>` prepares import
batches from the original verified corpus and vectors; it does not recompute
embeddings. Apply those batches through Supabase MCP as the database owner.

Keep `.env.local`, `.vercel`, seed batches, and vectors out of Vercel uploads. The two
required Vercel environment variables are `SUPABASE_URL` and
`SUPABASE_PUBLISHABLE_KEY`, configured for development, preview, and production.
Verify the linked owner/project with `vercel project inspect --non-interactive`
before deploying. The target project uses Vercel's existing deployment protection.

```sh
vercel env pull .env.local --yes
vercel deploy --prod
```

`scripts/verify_dataset.py <api-response.json>` checks all text/metadata and map
coordinates against the original atlas, and all 720 neighbors against exact
cosine in the original local vectors. Run it with the Python dependencies in `requirements-data.txt`. `verification.json` records the latest checks.

# Saved dataset

- `atlas.json`: reference documents, fixed 2D coordinates, exact top-three
  neighbors, and full provenance. Used by tests and import preparation.
- `corpus.json`: 240 cleaned complete-verse records before embedding.
- `corpus-manifest.json`: selection, source, cleaning, and display-label policy.
- `source/`: captured index, extracted source blocks, and cited label metadata.
- `derived/`: saved normalized vectors, exact model inputs, manifests, and
  projection outputs. Embedding weights are not included.

The float32 vector file has SHA-256
`e881ee07b467dcf6e84d358668369e4a254e8ef32c2ec8f89604ae5d91e96846`.
These files are versioned in the private app Git repository but excluded from
Vercel uploads. Runtime data comes from Supabase; the browser receives no vectors.

See [Dataset and method](../docs/DATASET.md) for reconstruction and provenance.

# Dataset and method / 数据与方法

The corpus contains **240 Song-era source articles, using 96 canonical authors**,
from [Guwendao's 宋词三百首](https://www.guwendao.net/gushi/songsan.aspx),
captured on 20 October 2026. Of the index's 293 links, 53 Tang/Five Dynasties
articles are excluded. All linked Northern/Southern Song entries are retained;
there is no poet balancing or popularity sampling. A multi-poem sequence on one
source page stays one document. For an attribution with multiple names, the first listed author is the sole
author used for display, filters, and author-style labels. The original 97
source attribution strings remain in the archived extraction; the app has 96
distinct canonical authors. This convention does not settle disputed authorship.

`data/source/raw.json` preserves the extracted source blocks, titles, authors,
URLs, and page hashes. `data/source/index.html` preserves the anthology index.
The corpus builder removes 22 explicitly reviewed prose prefaces and
parenthesized editorial variants. When two complete versions are printed, it
keeps the first. It applies NFKC and whitespace normalization while retaining
complete verse. Every displayed work links to its source.

The local model is `Qwen/Qwen3-Embedding-4B`, pinned to revision
`5cf2132abc99cad020ac570b19d031efec650f2b`. Only whitespace-normalized verse
enters the model: no title, poet, preface, style label, or anthology position.
The saved matrix is float32, L2-normalized, and has shape **240 × 2,560**.
No poem was truncated. Input hashes, model settings, source hashes, and the
embedding SHA-256 are recorded in `data/derived/embedding-manifest.json`.
Its corpus hash records the original embedding run, before author-only metadata
normalization. The model inputs, vectors, coordinates, and neighbor rankings
are unchanged by that normalization.

t-SNE uses 50 unwhitened PCA scores, perplexity 30, 1,500 iterations, PCA
initialization, and seed 42. UMAP uses all normalized dimensions, cosine
distance, 30 neighbors, minimum distance 0, and seed 42. The app displays only
these two 2D views. Archived PCA outputs document earlier length screening;
PCA is not shown in the app. Filtering highlights points without changing their
membership, coordinates, or axis ranges. Projection axes have no fixed literary
meaning.

The nearest three works are selected across the complete corpus using exact
original-space cosine similarity, excluding the selected work. Supabase stores
the full vectors and performs these comparisons. The deployed rankings were
verified against all **720** local reference neighbors.

The eight conventional author-style associations are used only for display and
filtering: 苏轼、辛弃疾 as 豪放派; 柳永、晏殊、欧阳修、秦观、周邦彦、李清照 as 婉约派.
Other author credits are unlabeled. `data/source/style-labels.json` preserves
the cited academic sources and policy. These associations are not poem-level
style assignments, and they do not enter embeddings, projection fitting, or
cluster discovery.

## Rebuild from this folder

All scripts resolve paths relative to their own location, not the current
working directory. Source-page HTML is cached in the Git-ignored
`data/source/pages/`; the captured extraction in `raw.json` is already included.

```sh
# Optional: refresh cached source pages; requires network access.
python scripts/crawl.py

# Rebuild the corpus from the included extracted source blocks.
python scripts/build_corpus.py

# Optional: recompute vectors locally using the pinned model.
python -m pip install -r requirements-embedding.txt
python scripts/embed.py --revision 5cf2132abc99cad020ac570b19d031efec650f2b
# Add --offline once the pinned model is cached. HF_HOME can point to an existing cache.

# Optional: recompute projections; otherwise use the saved coordinates.
python scripts/project.py

# Repackage the reference atlas and public provenance manifest.
python scripts/prepare_atlas.py
python scripts/prepare_seed.py /tmp/song-ci-seed
```

Model/chunk caches use `.cache/` and are excluded from Git. Refreshing source
pages or recomputing vectors/projections is a new data run; preserve the checked-in
snapshot when reproducing the published results. The ordinary app startup and
tests do not download or run the embedding model.

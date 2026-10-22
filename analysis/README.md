# Current semantic findings

The active analysis is `semantic_findings.py`. It reuses the 240 content-only
vectors and saved t-SNE/UMAP coordinates, without fitting clusters or changing
the app. Results use the app's current first-listed canonical authors.

- School comparison: 88 labeled works from eight authors; cosine silhouette,
  five nearest labeled works excluding the same author, and all 28 assignments
  of two authors to Haofang. Author-level reassignment keeps each author's works
  together; it is a small descriptive check, not evidence of a universal boundary.
- Thematic reading: five manually chosen t-SNE centers, eight nearest map points
  per center, all 28 within-window poem pairs, and a second mean excluding pairs
  by the same author. Centers, complete membership, source texts and metrics are
  saved in `results/semantic-findings.json`. Selection is post hoc.
- Baseline: every unordered corpus pair; the cross-author baseline excludes
  same-author pairs. Higher cosine is relative evidence, not a universal cutoff.
- `random8_95_interval` is a descriptive interval from 5,000 random eight-poem
  sets, not a confidence interval for the selected regions or a significance test.
- No previous cluster assignments or interpretations enter this calculation.

```sh
python -m pip install -r requirements-analysis.txt
python analysis/semantic_findings.py
python analysis/render_findings.py --lang en
python analysis/render_findings.py --lang zh
```

Rendering requires Poppler's `pdftoppm`. On macOS the renderer uses system Arial,
Georgia and Songti SC Regular (TTC index 6). Elsewhere it falls back to Helvetica
and Times for Latin text; pass a TrueType CJK font with `--cjk-font /path/font.ttf
--cjk-index 0`. The Chinese version translates headings, legends and interpretation,
while preserving names, poem quotations, metrics and uncertainty. `translations.zh.json`
is the reviewed translation catalog; both editions use the same data and figures.

The renderer writes the English/Chinese Markdown findings, figures and three-page
PDFs under `docs/`. No credentials, model calls or network access are needed.
`archive/2026-10-21/` retains the superseded cluster analysis for history; its
interpretations and original-author snapshot are not the current findings.

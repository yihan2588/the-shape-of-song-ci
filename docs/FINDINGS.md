# Semantic neighborhoods / 语义区域

The label-blind analysis supports two recurring semantic neighborhoods:
**seasonal scenes and personal longing**, and **history, ambition, and reflection**.
These are post-hoc interpretations of content-based groups, not poet-style labels.
These saved analyses use the original source-attribution snapshot. The app now
uses the first listed author for ambiguous credits; the poem texts and vectors
are unchanged. Cross-author statistics below describe that historical run.

HDBSCAN on the saved seed-42 maps (minimum cluster size 10, minimum samples 5)
assigns 81/38 poems to the two t-SNE groups, leaving 121 unassigned. UMAP assigns
98/55 to the broad groups plus a 12-poem sorrow pocket, leaving 75 unassigned.
All 97 poems assigned to broad groups in both projections agree in their grouping.

For the two broad UMAP groups, the fraction of original-space, cross-author
ten-nearest neighbors remaining in the same group is 79% and 74%. The corresponding
95% intervals from 1,000 length-stratified label permutations are 33–49% and
22–39%. In 98 seasonal/personal poems, 黄昏 occurs in 13 works versus 5 of 142
outside; in 55 historical/reflective poems, 江山 occurs in 6 versus 0 of 185 outside.
These descriptors and comparisons are exploratory and were chosen after clustering.

A finer UMAP leaf-cluster selection suggests five pockets: private sorrow;
life's course and withdrawal; historical/military ambition; parting and remembered
encounters; and intimate spring longing. Their boundaries vary across projection
seeds. Eight of the 12 sorrow-pocket works are by 李清照; its same-group neighbor
rate falls from 33% to 10% after excluding same-author neighbors. It does not
remain an independently matched cluster in three additional UMAP seed runs.

At the tested settings, HDBSCAN finds no discrete clusters in the original
cosine space. Read the maps as coherent neighborhoods within a continuum, not a
fixed literary taxonomy. The visual axes do not have fixed semantic meanings.

| Figure | English | 中文 |
| --- | --- | --- |
| Broad neighborhoods | [Image](figures/01-semantic-neighborhoods.png) | [图片](figures/01-semantic-neighborhoods-zh.png) |
| Candidate UMAP pockets | [Image](figures/02-candidate-pockets.png) | [图片](figures/02-candidate-pockets-zh.png) |
| Quantitative evidence | [Image](figures/03-original-space-evidence.png) | [图片](figures/03-original-space-evidence-zh.png) |

Saved labels, metrics, validation summaries, and original audit logs are under
`analysis/results/`. The logs preserve the historical run. To rerun the analysis:

```sh
python analysis/song_cluster_audit.py
python analysis/song_cluster_validate.py
python analysis/song_cluster_checks.py
python analysis/render_song_findings.py
python analysis/render_song_findings_zh.py
```

The analysis uses `requirements-data.txt`; rendering Chinese figures also
requires a CJK font. Font preferences in the plotting scripts can be adjusted
for the local operating system. Recomputing projections on different platforms
or library versions can change their layout.

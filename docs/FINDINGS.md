# The shape of Song Ci

[English](FINDINGS.md) · [中文](FINDINGS.zh.md)

Can semantic maps reveal how Song Ci poems relate through style, imagery and emotion? This analysis combines fixed visualizations, original-vector comparisons and close reading.

Song Ci is a traditional Chinese lyric-poetry form, originally written to tune patterns. Its two major stylistic traditions are Haofang (豪放派), known for expansive, heroic expression, and Wanyue (婉约派), known for intimate, delicate expression.

Question: If each poem becomes a natural-language embedding in a vector database, will a nonlinear 2D map naturally separate the two schools? Will poems sharing imagery or emotion gather into nearby “islands”?

Audience: readers exploring Chinese poetry through semantic search. Data: 240 anthology entries and 96 canonical authors from Guwendao, captured October 20, 2026. Complete verse alone enters Qwen3-Embedding-4B: 2,560 dimensions, L2-normalized, stored in Supabase. Titles, poets and school labels are excluded from fitting.

![01-school-separation](figures/01-school-separation-en.png)

The maps show overlapping school tendencies. Eight representative poets supply 33 Haofang and 55 Wanyue labels; 152 poems remain unlabeled. The original-vector silhouette is 0.094, reflecting substantial overlap.

School labels summarize a poet’s predominant style, and individual works often span styles: Haofang representative 苏轼 wrote the intimate, Wanyue-like elegy《江城子·乙卯正月二十日夜记梦》in memory of his wife.

Among each poem’s five nearest labeled works by other authors, 61.4% share its school. Reassigning two of the eight authors to Haofang gives a 57.1% average; 8 of 28 assignments reach or exceed the observed value.

## Where themes gather

Big idea: the map brings shared imagery and emotion into view. Frontier/history and chamber longing have the strongest similarity among the five regions examined.

![02-thematic-islands](figures/02-thematic-islands-en.png)

Each region contains the eight nearest t-SNE points to a manually selected center. Rings mark these works. The table compares their original-vector cosine similarity, including pairs by different authors.

| Region / location | Mean cosine | Other-author pairs only |
| --- | --- | --- |
| 1. Frontier & historical memory | 0.710 | 0.708 |
| 2. Life reflection | 0.621 | 0.592 |
| 3. Pastoral life | 0.651 | 0.648 |
| 4. Parting & remembrance | 0.671 | 0.672 |
| 5. Chamber longing | 0.728 | 0.707 |
| All 240 poems (pair average) | 0.624 | 0.623 |

Frontier/history, chamber longing, pastoral life and parting exceed the corpus pair average. Life reflection has a cross-author similarity of 0.592, below the 0.623 baseline, and combines a wider range of emotions.

## Read the islands

### 1. Frontier & historical memory | lower left

辛弃疾《永遇乐·京口北固亭怀古》：千古江山，英雄无觅，孙仲谋处。
张孝祥《水调歌头·和庞佑父》：湖海平生豪气，关塞如今风景，剪烛看吴钩。

Historical heroes, lost territory and martial imagery connect works by five authors.

### 2. Life reflection | bottom

苏轼《定风波·莫听穿林打叶声》：一蓑烟雨任平生。
苏轼《江城子·乙卯正月二十日夜记梦》：十年生死两茫茫，不思量，自难忘。

Resilience and bereavement sit nearby. Five of the eight works are by 苏轼, whose writing connects several emotions in this region.

### 3. Pastoral life | lower right

辛弃疾《西江月·夜行黄沙道中》：稻花香里说丰年，听取蛙声一片。
秦观《行香子·树绕村庄》：树绕村庄，水满陂塘。

Fields, villages, crops and rural sounds recur across seven authors. A Haofang poet and a Wanyue poet meet through shared imagery.

### 4. Parting & remembrance | right

柳永《雨霖铃·寒蝉凄切》：执手相看泪眼，竟无语凝噎。
欧阳修《浪淘沙·把酒祝东风》：聚散苦匆匆，此恨无穷。

Farewell, absent companions and returning seasons link these works. Remembered loss also appears in 晏殊’s nearby poem about falling flowers.

### 5. Chamber longing | upper right

李清照《一剪梅·红藕香残玉簟秋》：一种相思，两处闲愁。
唐琬《钗头凤·世情薄》：欲笺心事，独语斜阑。

Intimate longing and enclosed spaces recur. Six of eight works are by 李清照, alongside 唐琬 and 陆游; cross-author similarity is 0.707.

Conclusion: the maps show overlapping schools and recognizable thematic neighborhoods. Original-vector neighbors help readers explore these connections through close reading. Next, use independent theme labels and a second anthology to evaluate the regions selected here.

Source anthology: Guwendao, 宋词三百首. School background: Li, Li & Guan, Art Appreciation (2nd ed.), Tsinghua University Press, 2018, p. 37.

[GitHub](https://github.com/yihan2588/the-shape-of-song-ci) · [Live app](https://song-ci-atlas.vercel.app)



Reproduce: `python analysis/semantic_findings.py`, then `python analysis/render_findings.py --lang en` and `--lang zh`. Saved coordinates and vectors are reused; the app is unchanged.

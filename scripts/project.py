"""Label-blind, deterministic projections of the rebuilt anthology embeddings."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'data'
os.environ.setdefault('NUMBA_NUM_THREADS','4')
os.environ.setdefault('NUMBA_CACHE_DIR',str(ROOT.parent/'.cache/numba'))
os.environ.setdefault('OMP_NUM_THREADS','4')
import json
import numpy as np
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from threadpoolctl import threadpool_limits
from umap import UMAP


def main():
    out=ROOT/'derived'
    x=np.load(out/'embeddings.npy')
    records=json.loads((ROOT/'corpus.json').read_text())
    pca=PCA(n_components=50,svd_solver='full')
    scores=pca.fit_transform(x)
    np.save(out/'pca-scores.npy',scores)
    length=[len(''.join(r['text_simplified'].split())) for r in records]
    correlations=[float(spearmanr(scores[:,i],length).statistic) for i in range(50)]
    third=next(i for i in range(3,50) if abs(correlations[i])<.4)
    chosen=[0,2,third]
    tsne=TSNE(n_components=2,perplexity=30,max_iter=1500,init='pca',learning_rate='auto',random_state=42).fit_transform(scores)
    umap=UMAP(n_components=2,n_neighbors=30,min_dist=0,metric='cosine',random_state=42,n_jobs=1).fit_transform(x)
    coords={'tsne':tsne.tolist(),'umap':umap.tolist(),'pca':scores[:,chosen].tolist()}
    (out/'coordinates.json').write_text(json.dumps(coords))
    manifest={'seed':42,'pca_components':[i+1 for i in chosen],
      'explained_variance_ratios':pca.explained_variance_ratio_.tolist(),
      'length_correlations':correlations,'length_screen_abs_rho_threshold':.4,
      'length_measure':'Non-whitespace characters in complete stored poem content; Spearman correlation.',
      'tsne':{'perplexity':30,'max_iter':1500,'input':'50 unwhitened PCA scores','init':'pca','learning_rate':'auto'},
      'umap':{'n_neighbors':30,'min_dist':0,'metric':'cosine','input':'full L2-normalized embeddings'},
      'inputs':'Content-only vectors. No poet, school, title, anthology order, or other metadata used to fit projections.'}
    (out/'projection-manifest.json').write_text(json.dumps(manifest,indent=2))
    print('PCA components',manifest['pca_components'],'length correlations',correlations[:8],flush=True)

if __name__=='__main__':
    with threadpool_limits(limits=4):main()

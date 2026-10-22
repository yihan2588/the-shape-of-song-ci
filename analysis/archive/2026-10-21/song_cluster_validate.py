import os
os.environ['NUMBA_NUM_THREADS']='4';os.environ['NUMBA_CACHE_DIR']=os.path.join(os.path.dirname(__file__),'../.cache/numba-audit');os.environ['OMP_NUM_THREADS']='4'
import json,numpy as np,re
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
RESULTS=APP/'analysis/results'
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import HDBSCAN
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import CountVectorizer
from threadpoolctl import threadpool_limits
from umap import UMAP
R=APP/'data'
raw=json.loads((R/'corpus.json').read_text());texts=[r['text_simplified'] for r in raw]
x=np.load(R/'derived/embeddings.npy').astype(float);x/=np.linalg.norm(x,axis=1,keepdims=True);dist=cdist(x,x,'cosine');np.fill_diagonal(dist,0)
labels=dict(np.load(RESULTS/'song-cluster-labels.npz'));pc=np.load(R/'derived/pca-scores.npy')
results={}
with threadpool_limits(limits=4):
 for view in ['tsne','umap']:
  for seed in [7,21,84]:
   z=TSNE(n_components=2,perplexity=30,max_iter=1500,init='pca',learning_rate='auto',random_state=seed).fit_transform(pc) if view=='tsne' else UMAP(n_components=2,n_neighbors=30,min_dist=0,metric='cosine',random_state=seed,n_jobs=1).fit_transform(x)
   for method in ['eom','leaf']:
    key=f'{view}:m10s5:{method}';base=labels[key];lab=HDBSCAN(min_cluster_size=10,min_samples=5,cluster_selection_method=method,copy=True).fit_predict(z)
    a=sorted(map(int,set(base)-{-1}));b=sorted(map(int,set(lab)-{-1}));j=np.array([[np.sum((base==i)&(lab==k))/np.sum((base==i)|(lab==k)) for k in b] for i in a])
    match={i:0. for i in a}
    if j.size:
     ri,ci=linear_sum_assignment(-j)
     for r,c in zip(ri,ci):match[a[r]]=round(float(j[r,c]),3)
    results[f'{key}:seed{seed}']=dict(n_clusters=len(b),coverage=float((lab>=0).mean()),matched_jaccard=match)
   print('completed',view,seed,flush=True)
# Content-only enrichment and original-space neighborhoods for the seed-42 clusters.
v=CountVectorizer(analyzer='char',ngram_range=(2,3),min_df=3,binary=True);features=v.fit_transform(texts).toarray();terms=np.array(v.get_feature_names_out());han=np.array([all('\u3400'<=ch<='\u9fff' for ch in t) for t in terms]);nn=np.argsort(dist,axis=1)[:,1:11]
profiles={}
for key in ['tsne:m10s5:eom','umap:m10s5:eom','umap:m10s5:leaf']:
 lab=labels[key];profiles[key]={}
 for c in sorted(set(lab)-{-1}):
  ids=np.flatnonzero(lab==c);other=np.flatnonzero(lab!=c);freq=features[ids].sum(0);base=features[other].sum(0);delta=freq/len(ids)-base/len(other);allow=(freq>=3)&han
  order=np.flatnonzero(allow)[np.argsort(delta[allow])[-12:][::-1]]
  within=dist[np.ix_(ids,ids)];cross=dist[np.ix_(ids,other)]
  med=ids[np.argsort(within.mean(1))[:5]]
  profiles[key][str(c)]={'n':len(ids),'authors':len({raw[i]['requested_author'] for i in ids}),'length_median':float(np.median([len(re.sub(r'\W','',texts[i])) for i in ids])),
   'mean_within_cosine':float(1-within[np.triu_indices(len(ids),1)].mean()),'mean_outside_cosine':float(1-cross.mean()),
   'nn10_same_fraction':float((lab[nn[ids]]==c).mean()),'random_fraction':(len(ids)-1)/239,
   'medoids':[int(i) for i in med],'terms':[(terms[k],int(freq[k]),int(base[k])) for k in order]}
# Cross-map membership intersections.
t=labels['tsne:m10s5:eom'];u=labels['umap:m10s5:eom'];intersection={str(i):{str(j):int(np.sum((t==i)&(u==j))) for j in [-1,0,1,2]} for i in [-1,0,1]}
out={'stability':results,'profiles':profiles,'intersections':intersection}
Path(RESULTS/'song-cluster-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))

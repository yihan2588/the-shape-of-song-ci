import json,numpy as np,re
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
RESULTS=APP/'analysis/results'
from scipy.spatial.distance import cdist
from scipy.stats import rankdata
R=APP/'data'
r=json.loads((R/'corpus.json').read_text());x=np.load(R/'derived/embeddings.npy').astype(float);x/=np.linalg.norm(x,axis=1,keepdims=True)
labs=np.load(RESULTS/'song-cluster-labels.npz');d=cdist(x,x,'cosine');a=np.array([v['requested_author'] for v in r]);d[a[:,None]==a[None,:]]=np.inf;nn=np.argsort(d,axis=1)[:,:10]
length=np.array([len(re.sub(r'[^\u3400-\u9fff]','',v['text_simplified'])) for v in r]);bins=np.floor((rankdata(length,method='ordinal')-1)/24).astype(int);rng=np.random.default_rng(42)
for key in ['tsne:m10s5:eom','umap:m10s5:eom']:
 lab=labs[key];cs=sorted(set(lab)-{-1});obs={int(c):float((lab[nn[lab==c]]==c).mean()) for c in cs};null={int(c):[] for c in cs}
 for _ in range(1000):
  p=lab.copy()
  for b in np.unique(bins):
   mask=bins==b;p[mask]=rng.permutation(p[mask])
  for c in cs:null[int(c)].append(float((p[nn[p==c]]==c).mean()))
 print(key, {c:{'cross_author_nn':round(obs[c],4),'length_matched_null95':np.quantile(null[c],[.025,.975]).round(4).tolist()} for c in obs})
# Cross-map agreement among poems assigned to a broad main group in both maps.
t=labs['tsne:m10s5:eom'];u=labs['umap:m10s5:eom'];keep=(t>=0)&np.isin(u,[1,2]);print('assigned_main_both',keep.sum(),'agreement',int(np.sum((t[keep]==0)&(u[keep]==1))+np.sum((t[keep]==1)&(u[keep]==2))))
# Original-space density clustering can decline to force the continuum apart.
from sklearn.cluster import HDBSCAN
D=cdist(x,x,'cosine');np.fill_diagonal(D,0)
for m in [10,15]:
 l=HDBSCAN(min_cluster_size=m,min_samples=5,metric='precomputed',copy=True).fit_predict(D);print('original_hdbscan',m,'sizes',[int(sum(l==c)) for c in sorted(set(l)-{-1})],'unassigned',int(sum(l<0)))

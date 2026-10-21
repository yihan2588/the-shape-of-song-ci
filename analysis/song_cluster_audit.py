import os
os.environ['NUMBA_NUM_THREADS']='4'
os.environ['NUMBA_CACHE_DIR']=os.path.join(os.path.dirname(__file__),'../.cache/numba-audit')
os.environ['OMP_NUM_THREADS']='4'
import json,numpy as np
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
RESULTS=APP/'analysis/results'
from scipy.spatial.distance import cdist
from sklearn.cluster import HDBSCAN
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import CountVectorizer
from threadpoolctl import threadpool_limits
R=APP/'data'
raw=json.loads((R/'corpus.json').read_text());text=[r['text_simplified'] for r in raw]
x=np.load(R/'derived/embeddings.npy').astype(float);x/=np.linalg.norm(x,axis=1,keepdims=True)
d=cdist(x,x,'cosine');np.fill_diagonal(d,0)
coords=json.loads((R/'derived/coordinates.json').read_text());rows=[];labels={}
for name in ['tsne','umap']:
 z=np.array(coords[name])
 for m in [6,10,15,20,30]:
  for s in [3,5,10]:
   for method in ['eom','leaf']:
    lab=HDBSCAN(min_cluster_size=m,min_samples=s,cluster_selection_method=method).fit_predict(z)
    keep=lab>=0;n=len(set(lab[keep]));key=f'{name}:m{m}s{s}:{method}';labels[key]=lab
    if n>=2:
     rows.append(dict(key=key,n=n,coverage=round(float(keep.mean()),3),sil2=round(silhouette_score(z[keep],lab[keep]),3),silOrig=round(silhouette_score(d[np.ix_(keep,keep)],lab[keep],metric='precomputed'),3),sizes=np.bincount(lab[keep]).tolist()))
print('CANDIDATES')
for r in rows:
 if r['key'].startswith(('tsne:m10s5','umap:m10s5','tsne:m15s5','umap:m15s5','tsne:m6s3','umap:m6s3')):print(r)
print('BEST ORIGINAL',sorted(rows,key=lambda r:r['silOrig'],reverse=True)[:8])
vec=CountVectorizer(analyzer='char',ngram_range=(2,3),min_df=3,binary=True);a=vec.fit_transform(text).toarray();terms=np.array(vec.get_feature_names_out())
for key in ['tsne:m10s5:eom','umap:m10s5:eom','tsne:m10s5:leaf','umap:m10s5:leaf']:
 lab=labels[key];print('\nPROFILE',key)
 for c in sorted(set(lab)-{-1}):
  ids=np.flatnonzero(lab==c);other=np.flatnonzero(lab!=c)
  med=ids[np.argsort(d[np.ix_(ids,ids)].mean(1))[:5]]
  freq=a[ids].sum(0);base=a[other].sum(0)
  score=(freq/len(ids)-base/len(other));allowed=(freq>=max(3,len(ids)*.15))&np.array([all('\u3400'<=ch<='\u9fff' for ch in t) for t in terms]);order=np.argsort(np.where(allowed,score,-100))[-12:][::-1]
  print('cluster',int(c),'n',len(ids),'terms',[(terms[j],int(freq[j]),int(base[j])) for j in order]);print('MEDOIDS',[(int(i),raw[i]['title_simplified'],raw[i]['requested_author'],text[i][:80]) for i in med]);print('ALL',[(int(i),raw[i]['title_simplified'],raw[i]['requested_author']) for i in ids])
np.savez(RESULTS/'song-cluster-labels.npz',**labels)
Path(RESULTS/'song-cluster-metrics.json').write_text(json.dumps(rows,ensure_ascii=False))
if __name__=='__main__':pass

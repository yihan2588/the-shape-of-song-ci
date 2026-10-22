"""Recompute school separation and post-hoc thematic-region evidence from saved vectors."""
import json,hashlib,itertools
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent; D=R.parent/'data'
(R/'results').mkdir(exist_ok=True)
a=json.loads((D/'atlas.json').read_text());docs=a['documents'];x=np.load(D/'derived/embeddings.npy').astype(float);x/=np.linalg.norm(x,axis=1,keepdims=True)
cos=x@x.T;n=len(x);dist=1-cos;np.fill_diagonal(dist,0)
idx=np.array([i for i,d in enumerate(docs) if d['label']]);y=np.array([docs[i]['label']=='豪放派' for i in idx]);authors=np.array([docs[i]['poet'] for i in idx]);author_names=sorted(set(authors))
def silhouette(dm,y):
 v=[]
 for i in range(len(y)):
  same=y==y[i];same[i]=False
  ai=dm[i,same].mean();bi=dm[i,y!=y[i]].mean();v.append((bi-ai)/max(ai,bi))
 return float(np.mean(v))
spaces={'Original cosine':dist[np.ix_(idx,idx)]}
for view in ['tsne','umap']:
 c=np.array(a['coordinates'][view])[idx];spaces[view]=np.linalg.norm(c[:,None]-c[None,:],axis=2)
sil={k:silhouette(v,y) for k,v in spaces.items()}
# Five nearest labeled poems by other authors; hold author identity out of neighbor candidates.
dm=spaces['Original cosine'].copy();dm[authors[:,None]==authors[None,:]]=np.inf
nn=np.argsort(dm,axis=1)[:,:5]
score=lambda labels:float(np.mean(labels[nn]==labels[:,None]))
obs=score(y);perm=[]
for pair in itertools.combinations(author_names,2):perm.append(score(np.isin(authors,pair)))
# Candidate inspection windows are post-hoc locations supplied by the user, not fitted clusters.
regions=[('Frontier & historical memory',[-10,-5.5]),('Life reflection',[-1,-10]),('Pastoral life',[4.5,-7.5]),('Parting & remembrance',[7.5,1.5]),('Chamber longing',[9.5,5.5])]
co=np.array(a['coordinates']['tsne']);rng=np.random.default_rng(42);tri=np.triu_indices(8,1);random_means=[]
for _ in range(5000):
 r=rng.choice(n,8,replace=False);random_means.append(float(cos[np.ix_(r,r)][tri].mean()))
out=[]
for name,center in regions:
 ids=np.argsort(((co-center)**2).sum(1),kind='stable')[:8];m=float(cos[np.ix_(ids,ids)][tri].mean())
 cross=[cos[i,j] for i,j in itertools.combinations(ids,2) if docs[i]['poet']!=docs[j]['poet']]
 out.append(dict(name=name,center=center,indices=ids.tolist(),mean_cosine=m,cross_author_cosine=float(np.mean(cross)),authors=len(set(docs[i]['poet'] for i in ids)),poems=[docs[i] for i in ids]))
# Full-corpus pair baseline, including a separate cross-author baseline.
allcross=[cos[i,j] for i,j in itertools.combinations(range(n),2) if docs[i]['poet']!=docs[j]['poet']]
result=dict(n=n,dimensions=x.shape[1],counts={k:sum(d['label']==k for d in docs) for k in ['豪放派','婉约派',None]},silhouette=sil,cross_author_knn_same_school=obs,author_permutation=dict(assignments=len(perm),mean=float(np.mean(perm)),at_least_observed=sum(v>=obs-1e-12 for v in perm),values=perm),pair_baseline=float(cos[np.triu_indices(n,1)].mean()),cross_author_baseline=float(np.mean(allcross)),random8_95_interval=np.quantile(random_means,[.025,.975]).tolist(),regions=out,source_vector_sha256=hashlib.sha256((D/'derived/embeddings.npy').read_bytes()).hexdigest())
(R/'results/semantic-findings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='regions'},ensure_ascii=False,indent=2))
for r in out:print(r['name'],r['indices'],r['mean_cosine'],r['cross_author_cosine'],r['authors'],[(d['poet'],d['title']) for d in r['poems']])

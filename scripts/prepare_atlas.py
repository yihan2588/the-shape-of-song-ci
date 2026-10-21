"""Package the complete anthology edition and exact original-space neighbors."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'data'


def main():
    source=json.loads((RUN/'corpus.json').read_text())
    documents=[{'id':r['corpus_id'],'poet':r['requested_author'],'label':r['style_label'],
      'title':r['title_simplified'],'note':r.get('source_note',''),'tune':r['rhythmic'],'text':r['text_simplified'],'url':r['source_url']} for r in source]
    x=np.load(RUN/'derived/embeddings.npy').astype(np.float64)
    x/=np.linalg.norm(x,axis=1,keepdims=True)
    cosine=x@x.T;np.fill_diagonal(cosine,-np.inf)
    nearest=np.argsort(-cosine,axis=1,kind='stable')[:,:3]
    neighbors=[[{'index':int(j),'cosine':round(float(cosine[i,j]),8)} for j in nearest[i]] for i in range(len(x))]
    corpus=json.loads((RUN/'corpus-manifest.json').read_text())
    projection=json.loads((RUN/'derived/projection-manifest.json').read_text())
    embedding=json.loads((RUN/'derived/embedding-manifest.json').read_text())
    provenance=projection | {'model':embedding['model'],'dimensions':2560,'n_documents':len(documents),
      'normalization':'L2','neighbor_scope':f'all {len(documents)} poems; exact original-space cosine; exclude self',
      'model_revision':embedding['revision'],'corpus':corpus,
      'embeddings_sha256':hashlib.sha256((RUN/'derived/embeddings.npy').read_bytes()).hexdigest()}
    data={'documents':documents,'neighbors':neighbors,'coordinates':{k:v for k,v in json.loads((RUN/'derived/coordinates.json').read_text()).items() if k in ['tsne','umap']},'provenance':provenance}
    (RUN/'atlas.json').write_text(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
    (ROOT/'public/dataset-manifest.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
    print('Prepared',len(documents),'poems,',corpus['n_poets'],'poet credits; views:', ', '.join(data['coordinates']))

if __name__=='__main__':main()

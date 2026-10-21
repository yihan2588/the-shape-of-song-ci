"""Poetry-only corpus from the supplied Guwendao anthology, Song chapters only."""
import hashlib,json,re,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'data'
SOURCE=ROOT/'source'
LABEL_METADATA=json.loads((SOURCE/'style-labels.json').read_text())
LABELS=LABEL_METADATA['poet_labels']
# Explicitly reviewed first paragraphs that are prose prefaces, not verse.
PREFACES=set('fcb00c141925 22459da51344 a9a16104dd1b 9063e08f5bfc 16f02efc5087 2fab0ad2ae76 70ff5ccdd2f4 f08f2f570c7d 6b30455fdd3c 632c5beb84eb 406b5b4f718a 7d4dfc7f3db4 66261a47fc2b a8062138a414 1c78ac08096e b5465fbbed6f 1443f4f57a9d 098e88b62d38 79730f08af17 167bcafbfe95 cd33ded081be ddc4b7e8623a'.split())
def clean(s):
    s=unicodedata.normalize('NFKC',s)
    s=re.sub(r'\([^()]*\)','',s)
    return '\n'.join(line.strip() for line in s.splitlines() if line.strip())
def main():
    raw=json.loads((SOURCE/'raw.json').read_text());records=[];duplicates=[];seen={}
    for i,r in enumerate(raw):
        key=r['url'].split('_')[-1].split('.')[0];blocks=r['paragraph_blocks'];preface=''
        if key in PREFACES:preface=blocks[0];blocks=blocks[1:]
        if any('版本一' in b for b in blocks):
            end=next(i for i,b in enumerate(blocks) if '版本一' in b);blocks=blocks[:end+1]
        text=clean('\n'.join(blocks));identity=(r['author'],''.join(re.findall(r'[\u3400-\u9fff\U00020000-\U0003134f]',text)))
        if identity in seen:duplicates.append({'url':r['url'],'duplicate_of':seen[identity]});continue
        assert len(identity[1])>15, r['url']
        seen[identity]=r['url']
        records.append({'era':'宋词','corpus_id':f'guwendao-{key}','requested_author':r['author'],'source_author':r['author'],
         'style_label':LABELS.get(r['author']),'title_simplified':r['title'],'source_note':preface,
         'rhythmic':r['title'].split('·')[0],'text_simplified':text,'source_url':r['url'],'source_index':i,'section':r['section']})
    (ROOT/'corpus.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    old=LABEL_METADATA
    manifest={k:old[k] for k in ['poet_labels','label_sources','label_policy']}
    manifest.update(name='宋词三百首 · 古文岛宋代卷',source_url='https://www.guwendao.net/gushi/songsan.aspx',retrieved_at='2026-10-20',
      source_sha256=hashlib.sha256((SOURCE/'index.html').read_bytes()).hexdigest(),n_documents=len(records),n_poets=len({r['requested_author'] for r in records}),
      selection='All linked works in 北宋词/南宋词 chapters; 唐五代词 chapters excluded to preserve Song-only scope. Exact same-author Han-text duplicates merged.',
      normalization='Original verse only. Reviewed prose prefaces and parenthesized editorial variants removed; when multiple complete versions are printed, version one is used. NFKC + whitespace normalization; title, author, notes and labels excluded from embeddings.',
      duplicate_pages=duplicates,excluded_preface_ids=sorted(PREFACES),crawled_song_pages=len(raw),
      edition_note='Source anthology includes Tang/Five Dynasties material; only its Song chapters are included. A page containing a sequence of poems stays one document.')
    (ROOT/'corpus-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(len(records),'poems',manifest['n_poets'],'poets; duplicates',len(duplicates))
if __name__=='__main__':main()

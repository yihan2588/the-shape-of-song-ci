"""Cache the supplied anthology's Song chapters and their linked poem pages."""
import concurrent.futures,hashlib,json,re,urllib.request,time
from html import unescape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'data/source'
URL='https://www.guwendao.net/gushi/songsan.aspx'
def plain(s):
    return unescape(re.sub('<[^>]+>','',s)).strip()
def fetch(item):
    path=ROOT/'pages'/item['url'].split('/')[-1]; path.parent.mkdir(exist_ok=True)
    if not path.exists():
        req=urllib.request.Request(item['url'],headers={'User-Agent':'Mozilla/5.0'})
        for attempt in range(3):
            try:
                path.write_bytes(urllib.request.urlopen(req,timeout=30).read());break
            except Exception:
                print('Retry',item['url'],attempt+1,flush=True)
                if attempt==2:raise
                time.sleep(2+attempt*2)
    s=path.read_text()
    m=re.search(r'<div class="contson"[^>]*>(.*?)</div>',s,re.S)
    if not m:raise ValueError('No poem block: '+item['url'])
    raw=m[1]; blocks=re.findall(r'<p\b[^>]*>(.*?)</p>',raw,re.S) or [raw]
    paragraphs=[plain(re.sub(r'<br\s*/?>','\n',p)) for p in blocks]
    title=plain(re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)[1])
    src=re.search(r'<p class="source">(.*?)</p>',s,re.S)
    author=plain(re.search(r'<a[^>]*>(.*?)</a>',src[1],re.S)[1])
    return item|{'title':title,'author':author,'paragraph_blocks':paragraphs,'page_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    s=(ROOT/'index.html').read_text();items=[];seen=set();all_links=0
    for section in re.split(r'<div class="typecont"[^>]*>',s)[1:]:
        heading=re.search(r'<strong>(卷.*?)</strong>',section)
        if not heading:continue
        links=re.findall(r'<span>\s*<a href="(/shiwenv_[^"]+)"[^>]*>(.*?)</a>(.*?)</span>',section,re.S)
        all_links+=len(links)
        if '宋词' not in heading[1]:continue
        for url,title,author in links:
            if url in seen:continue
            seen.add(url);items.append({'url':'https://www.guwendao.net'+url,'section':heading[1],'index_title':plain(title)})
    print('Song links',len(items),'all links',all_links,flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        records=[]
        for i,r in enumerate(pool.map(fetch,items)):
            records.append(r)
            if i%25==0:print('Crawled',i+1,flush=True)
    (ROOT/'raw.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print('Saved',len(records),'poems',len({r['author'] for r in records}),'authors',flush=True)
if __name__=='__main__':main()

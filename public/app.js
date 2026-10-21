(() => {
  'use strict';
  const DATA = window.POETRY_DATA, docs = DATA.documents, $ = id => document.getElementById(id);
  const palette = { background: '#b0bcb3', match: '#41aa8b', selected: '#348675', neighbors: ['#064b40', '#166455', '#287e6c'] };
  const styleColors = { '豪放派': '#b76c4e', '婉约派': '#438e9b' };
  const messages = {
    en: {
      title:'The shape of Song Ci',subtitle:'Explore a poem and its closest companions.',about:'Dataset & method',language:'Language',
      sourceDoc:'240 Song-era entries from Guwendao’s Song Ci anthology, crawled 20 Oct 2026. Tang/Five Dynasties chapters are excluded; source attributions are preserved.',sourceAnthology:'Source anthology ↗',
      modelDoc:'Complete verse is embedded locally with Qwen3-Embedding-4B and L2-normalized. Titles, poets, prefaces and labels never enter the vectors. Poems remain in their original Chinese.',
      labelDoc:'Conventional style labels: Haofang — 苏轼、辛弃疾; Wanyue — 柳永、晏殊、欧阳修、秦观、周邦彦、李清照. Other poets are unlabeled. These are author associations, not labels for every poem.',
      viewDoc:'t-SNE and UMAP show semantic neighborhoods. All points stay fixed when filtering. Neighbors use exact cosine in the original vectors stored in Supabase, across the full dataset.',provenance:'Full settings & sources ↗',
      find:'Find a poem',done:'Done',poetSearch:'Search poets',poetPlaceholder:'e.g. 苏轼',poet:'Poet',allPoets:'All poets',matchedPoets:'All matching poets',style:'Poet style',allStyles:'All styles',unlabeled:'Unlabeled',bold:'Haofang',gentle:'Wanyue',query:'Title or poem text',queryPlaceholder:'赤壁怀古 / 十年生死…',clear:'Clear',results:'Matching poems',noResults:'No matches. Try another name or phrase.',view:'View',color:'Color',neutral:'Neutral',reset:'Reset view',map:'Poem map',mapDescription:'Interactive poem map. Click a point to read it and find its three nearest poems.',selected:'Selected',nearestLegend:'1–3 nearest',matchesLegend:'Matches',reading:'Selected poem and nearest poems',readTitle:'Start with a poem',readHelp:'Click a point or choose a search result. Read it here alongside its three nearest poems.',clearSelection:'Deselect',poemText:'Complete poem',readSource:'Read source ↗',nearest:'Three nearest poems',cosine:'Cosine similarity · entire dataset',outside:'Outside current filters',selectPoem:'Read this poem',
      count:(n,total)=>`${n} ${n===1?'match':'matches'} / ${total}`,dataset:(n,p)=>`${n} Song Ci poems`,status:(n,total)=>`${n} of ${total} highlighted · drag to pan, scroll to zoom.`,selectedStatus:'Diamond = selected · darker 1–3 = nearest poems.'
    },
    zh: {
      title:'词之形',subtitle:'读一首词，发现与它意境相近的作品。',about:'数据与方法',language:'界面语言',
      sourceDoc:'选自古文岛《宋词三百首》的宋代篇目，共240篇，采集于2026年10月20日。不含唐五代卷，作者归属沿用原站标注。',sourceAnthology:'查看选集原文 ↗',
      modelDoc:'使用本地 Qwen3-Embedding-4B 模型编码完整词作正文，并进行 L2 归一化。标题、作者、小序和流派标签均不参与编码。词作保留中文原文。',
      labelDoc:'仅为公认的代表词人标注流派：豪放派——苏轼、辛弃疾；婉约派——柳永、晏殊、欧阳修、秦观、周邦彦、李清照。其余暂不标注。词人的流派归属不代表其每首作品的风格。',
      viewDoc:'t-SNE 和 UMAP 用于展示语义邻近关系。筛选只改变高亮，不移动散点。相近词作由 Supabase 按原始向量的余弦相似度，从全部作品中选取。',provenance:'查看完整参数与来源 ↗',
      find:'查找词作',done:'完成',poetSearch:'输入词人姓名',poetPlaceholder:'例如：苏轼',poet:'选择词人',allPoets:'全部词人',matchedPoets:'全部匹配词人',style:'词人流派',allStyles:'全部流派',unlabeled:'未标注',bold:'豪放派',gentle:'婉约派',query:'搜索标题或正文',queryPlaceholder:'赤壁怀古 / 十年生死…',clear:'清除',results:'匹配的词作',noResults:'未找到匹配作品，请换个姓名或词句。',view:'视图',color:'配色',neutral:'单色',reset:'重置视图',map:'词作分布图',mapDescription:'点击散点，阅读词作及与它最相近的三篇作品。',selected:'当前词作',nearestLegend:'最相近的三篇',matchesLegend:'筛选结果',reading:'当前词作与相近作品',readTitle:'从一首词开始',readHelp:'点击图中散点或选择搜索结果，即可在此阅读原文与最相近的三篇作品。',clearSelection:'取消选择',poemText:'词作全文',readSource:'查看原文 ↗',nearest:'最相近的三篇',cosine:'按余弦相似度排序 · 全部作品',outside:'不在当前筛选范围内',selectPoem:'阅读这首词',
      count:(n,total)=>`匹配 ${n} / ${total} 篇`,dataset:(n,p)=>`${n} 篇宋词`,status:(n,total)=>`高亮 ${n} / ${total} 篇 · 拖动平移，滚轮缩放。`,selectedStatus:'菱形为当前词作，深色数字 1–3 为最相近的作品。'
    }
  };
  let lang='en';
  try { const saved=window.localStorage.getItem('song-ci-language'); if(messages[saved])lang=saved; } catch (_) { /* Storage can be disabled in private/offline contexts. */ }
  let selected=null, matching=[], matches=new Set(), view='tsne', filtering=false;
  const t=key=>messages[lang][key];
  const normalize=s=>String(s||'').normalize('NFKC').toLowerCase().replace(/\s+/g,'');
  const searchable=docs.map(d=>normalize([d.title,d.tune,d.note,d.text].join(' ')));
  const poets=[...new Set(docs.map(d=>d.poet))].sort((a,b)=>a.localeCompare(b,'zh'));
  const opening=d=>d.text.split(/[。！？\n]/)[0].slice(0,20);
  const pieceName=d=>d.title||d.tune;
  const labelName=label=>label==='豪放派'?t('bold'):label==='婉约派'?t('gentle'):t('unlabeled');
  const option=(value,text)=>{const e=document.createElement('option');e.value=value;e.textContent=text;return e;};
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  // Fit nothing in the browser. Bounds and membership always use the entire corpus.
  const bounds=Object.fromEntries(['tsne','umap'].map(key=>[key,[0,1].map(axis=>{const values=DATA.coordinates[key].map(r=>r[axis]);const lo=Math.min(...values),hi=Math.max(...values),pad=(hi-lo||1)*.07;return [lo-pad,hi+pad];})]));
  function rebuildPoets() {
    const value=$('poet').value,q=normalize($('poet-search').value);
    const available=poets.filter(p=>normalize(p).includes(q));
    $('poet').replaceChildren(option('',t(q?'matchedPoets':'allPoets')),...available.map(p=>option(p,p)));
    $('poet').value=available.includes(value)?value:'';
  }
  function renderResults() {
    $('pieces').replaceChildren(...matching.map(i=>option(String(i),`${pieceName(docs[i])} · ${docs[i].poet}`)));
    $('pieces').value=selected===null?'':String(selected);
    $('match-count').textContent=t('count')(matching.length,docs.length);
    $('empty').hidden=matching.length!==0;
  }
  function applyFilters(event) {
    const poet=$('poet').value,poetQuery=normalize($('poet-search').value),label=$('school').value,q=normalize($('query').value);
    filtering=Boolean(poet||poetQuery||label||q);
    matching=docs.map((_,i)=>i).filter(i=>(!poet||docs[i].poet===poet)&&(!poetQuery||normalize(docs[i].poet).includes(poetQuery))
      &&(!label||(label==='__unlabeled'?!docs[i].label:docs[i].label===label))&&(!q||searchable[i].includes(q)));
    matches=new Set(matching);
    if(selected!==null&&!matches.has(selected))selected=null;
    if(q&&event?.target===$('query'))selected=matching[0]??null;
    renderResults();renderReading();renderPlot();
  }
  function neighbors(){return selected===null?[]:DATA.neighbors[selected];}
  function closeFilters(){document.body.classList.remove('filters-open');$('open-filters').setAttribute('aria-expanded','false');}
  function selectPiece(i){
    if(!Number.isInteger(i)||i<0||i>=docs.length)return;
    selected=i;$('pieces').value=String(i);closeFilters();renderReading();renderPlot();
  }
  function renderReading(){
    $('reading-empty').hidden=selected!==null;$('reading-content').hidden=selected===null;$('clear-selection').disabled=selected===null;
    if(selected===null){$('neighbors').replaceChildren();return;}
    const d=docs[selected];$('selected-title').textContent=pieceName(d);
    $('selected-meta').textContent=`${d.poet} · ${labelName(d.label)}${matches.has(selected)?'':` · ${t('outside')}`}`;
    $('selected-text').textContent=d.text;$('source-link').href=d.url;
    const fragment=document.createDocumentFragment();
    neighbors().forEach((n,k)=>{
      const poem=docs[n.index],el=document.createElement('button');el.type='button';el.className='neighbor';el.style.borderLeftColor=palette.neighbors[k];
      el.setAttribute('aria-label',`${t('selectPoem')}: ${pieceName(poem)} · ${poem.poet}`);
      el.innerHTML=`<span class="neighbor-title"><strong>${k+1}. ${esc(pieceName(poem))}</strong><span class="score" style="color:${palette.neighbors[k]}">${n.cosine.toFixed(4)}</span></span><span class="meta">${esc(poem.poet)} · ${esc(labelName(poem.label))}${matches.has(n.index)?'':` · ${t('outside')}`}</span><span class="excerpt" lang="zh">${esc(poem.text.slice(0,60))}${poem.text.length>60?'…':''}</span>`;
      el.addEventListener('click',()=>selectPiece(n.index));fragment.append(el);
    });$('neighbors').replaceChildren(fragment);
  }
  function renderPlot(){
    const rank=new Map(neighbors().map((n,k)=>[n.index,k])),coords=DATA.coordinates[view],styles=$('color').value==='style';
    const colors=docs.map((d,i)=>i===selected?palette.selected:rank.has(i)?palette.neighbors[rank.get(i)]
      :filtering?(matches.has(i)?palette.match:palette.background):styles?(styleColors[d.label]||palette.background):palette.background);
    const trace={type:'scatter',mode:'markers+text',name:t('map'),x:coords.map(r=>r[0]),y:coords.map(r=>r[1]),customdata:docs.map((_,i)=>i),
      text:docs.map((_,i)=>i===selected?t('selected'):rank.has(i)?String(rank.get(i)+1):''),textposition:'top center',textfont:{color:'#164c40',size:11},
      hovertext:docs.map(d=>`${esc(pieceName(d))} · ${esc(d.poet)}<br>${esc(opening(d))}<br>${esc(labelName(d.label))}`),hovertemplate:'%{hovertext}<extra></extra>',
      marker:{color:colors,size:docs.map((_,i)=>i===selected?14:rank.has(i)?12:filtering&&matches.has(i)?8:5),opacity:1,symbol:docs.map((_,i)=>i===selected?'diamond':'circle'),line:{width:0}}};
    const axis=dimension=>({range:bounds[view][dimension],autorange:false,gridcolor:'#e1e3d9',zeroline:false,tickfont:{size:10},title:{text:`${view==='tsne'?'t-SNE':'UMAP'} ${dimension+1}`,font:{size:10}}});
    Plotly.react('plot',[trace],{paper_bgcolor:'#faf8f2',plot_bgcolor:'#faf8f2',font:{family:'system-ui',color:'#26332f'},margin:{l:35,r:10,t:22,b:35},showlegend:false,uirevision:view,dragmode:'pan',xaxis:axis(0),yaxis:axis(1)},
      {responsive:true,displayModeBar:false,scrollZoom:true});
    $('plot-status').textContent=selected===null?t('status')(matching.length,docs.length):t('selectedStatus');
  }
  function setLanguage(value){
    if(!messages[value])return;lang=value;document.documentElement.lang=lang==='zh'?'zh-Hans':'en';document.title=lang==='zh'?'词之形':'The shape of Song Ci';$('language').value=lang;
    try{window.localStorage.setItem('song-ci-language',lang);}catch(_){}
    document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.getAttribute('data-i18n'));});
    document.querySelectorAll('[data-placeholder]').forEach(el=>{el.placeholder=t(el.getAttribute('data-placeholder'));});
    document.querySelectorAll('[data-aria]').forEach(el=>{el.setAttribute('aria-label',t(el.getAttribute('data-aria')));});
    $('pieces').setAttribute('aria-label',t('results'));
    $('dataset-count').textContent=t('dataset')(docs.length,poets.length);
    const school=$('school').value,color=$('color').value;
    rebuildPoets();$('school').replaceChildren(option('',t('allStyles')),option('豪放派',t('bold')),option('婉约派',t('gentle')),option('__unlabeled',t('unlabeled')));$('school').value=school;
    $('color').replaceChildren(option('style',t('style')),option('neutral',t('neutral')));$('color').value=color||'style';
    renderResults();renderReading();renderPlot();
  }
  $('poet-search').addEventListener('input',e=>{rebuildPoets();applyFilters(e);});
  $('poet').addEventListener('change',applyFilters);$('school').addEventListener('change',applyFilters);$('query').addEventListener('input',applyFilters);
  $('color').addEventListener('change',renderPlot);$('language').addEventListener('change',()=>setLanguage($('language').value));
  $('view').addEventListener('change',()=>{view=$('view').value;renderPlot();});
  $('pieces').addEventListener('change',()=>{if($('pieces').value!=='')selectPiece(Number($('pieces').value));});
  $('clear').addEventListener('click',()=>{$('poet-search').value='';$('poet').value='';$('school').value='';$('query').value='';rebuildPoets();applyFilters();});
  $('clear-selection').addEventListener('click',()=>{selected=null;renderResults();renderReading();renderPlot();});
  $('open-filters').addEventListener('click',()=>{const open=document.body.classList.toggle('filters-open');$('open-filters').setAttribute('aria-expanded',String(open));if(open)$('poet-search').focus();});
  $('close-filters').addEventListener('click',closeFilters);
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeFilters();});
  $('reset-view').addEventListener('click',()=>Plotly.relayout('plot',{'xaxis.range':bounds[view][0],'yaxis.range':bounds[view][1]}));
  matching=docs.map((_,i)=>i);matches=new Set(matching);setLanguage(lang);
  $('plot').on('plotly_click',e=>{const i=e.points?.[0]?.customdata;if(Number.isInteger(i))selectPiece(i);});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(()=>{if($('plot').getBoundingClientRect().width>0)Plotly.Plots.resize($('plot'));}).observe($('plot'));
})();

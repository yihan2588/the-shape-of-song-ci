// Run the real controller with a minimal DOM and a Plotly recorder.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(){this.value='';this.children=[];this.style={};this.events={};this.attrs={};this.hidden=false;}
 append(x){this.children.push(x);} replaceChildren(...xs){this.children=xs.flatMap(x=>x.isFragment?x.children:[x]);}
 addEventListener(k,fn){this.events[k]=fn;} setAttribute(k,v){this.attrs[k]=v;} getAttribute(k){return this.attrs[k];} focus(){} on(k,fn){this.events[k]=fn;}
}
const ids=new Map(),el=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};let latest,resets=0;
const classes=new Set(),storage=new Map();
const ctx={window:{localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)}},document:{documentElement:{},body:{classList:{remove:k=>classes.delete(k),toggle:k=>{if(classes.has(k)){classes.delete(k);return false;}classes.add(k);return true;}}},getElementById:el,createElement:()=>new Element(),createDocumentFragment:()=>Object.assign(new Element(),{isFragment:true}),querySelectorAll:()=>[],addEventListener:()=>{}},Plotly:{react:(id,traces,layout)=>{latest={traces,layout};},relayout:()=>resets++}};
vm.createContext(ctx);vm.runInContext('window.POETRY_DATA='+fs.readFileSync(require('node:path').join(__dirname,'../data/atlas.json'),'utf8'),ctx);vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'../public/app.js'),'utf8'),ctx);
const docs=ctx.window.POETRY_DATA.documents,N=docs.length;
const geometry=()=>JSON.stringify({x:latest.traces[0].x,y:latest.traces[0].y,xaxis:latest.layout.xaxis,yaxis:latest.layout.yaxis,uirevision:latest.layout.uirevision});
function change(id,value,event='change'){el(id).value=value;el(id).events[event]({target:el(id)});}
const clear=()=>el('clear').events.click();
const checkFull=()=>{assert.equal(latest.traces.length,1);assert.equal(latest.traces[0].type,'scatter');assert.equal(latest.traces[0].customdata.length,N);assert(!latest.layout.scene);};
assert.deepEqual(Object.keys(ctx.window.POETRY_DATA.coordinates).sort(),['tsne','umap']);
for(const view of ['tsne','umap']){
 clear();change('view',view);const before=geometry();
 change('poet-search','苏','input');checkFull();assert.equal(geometry(),before);assert.equal(el('poet').children.length,2);assert.equal(el('poet').children[1].value,'苏轼');
 assert.equal(el('pieces').children.length,docs.filter(d=>d.poet==='苏轼').length);
 change('poet','苏轼');change('query','十年生死','input');checkFull();assert.equal(geometry(),before);assert.equal(el('pieces').children.length,1);assert.equal(el('neighbors').children.length,3);
 for(const color of ['#348675','#064b40','#166455','#287e6c'])assert(latest.traces[0].marker.color.includes(color));
 const selectedTitle=el('selected-title').textContent;
 change('language','zh');assert.equal(ctx.document.documentElement.lang,'zh-Hans');assert.equal(ctx.document.title,'词之形');assert.match(el('match-count').textContent,/匹配/);assert.equal(el('selected-title').textContent,selectedTitle);assert.equal(el('poet').value,'苏轼');assert.equal(geometry(),before);assert.equal(el('neighbors').children.length,3);assert.match(el('neighbors').children[0].innerHTML,/阅读|未标注|豪放派|婉约派|不在当前/);
 change('language','en');assert.equal(ctx.document.documentElement.lang,'en');assert.equal(ctx.document.title,'The shape of Song Ci');assert.equal(el('selected-title').textContent,selectedTitle);assert.equal(geometry(),before);
 // Typing a different author clears an incompatible dropdown choice.
 change('poet-search','李清照','input');assert.equal(el('poet').value,'');change('query','','input');assert.equal(el('pieces').children.length,docs.filter(d=>d.poet==='李清照').length);checkFull();assert.equal(geometry(),before);
 change('poet-search','NO_SUCH_POET','input');assert.equal(el('poet').children.length,1);assert.equal(el('pieces').children.length,0);checkFull();assert.equal(geometry(),before);
 clear();change('school','__unlabeled');assert(el('pieces').children.length>0);checkFull();assert.equal(geometry(),before);
 // Point and neighbor-card clicks work, even outside the filters.
 change('poet','苏轼');el('plot').events.plotly_click({points:[{customdata:0}]});assert.equal(el('neighbors').children.length,3);el('neighbors').children[0].events.click();assert.equal(el('neighbors').children.length,3);assert.equal(geometry(),before);
 el('reset-view').events.click();checkFull();
}
assert.equal(resets,2);assert.equal(storage.get('song-ci-language'),'en');
console.log('PASS: searchable poet dropdown; two 2D views only; fixed maps; global neighbors; point/card selection; bilingual state and language persistence.');

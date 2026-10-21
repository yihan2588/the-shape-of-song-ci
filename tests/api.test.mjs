import test from 'node:test';
import assert from 'node:assert/strict';
import atlas from '../api/atlas.js';
import neighbors from '../api/neighbors.js';

function response() {
  return {
    headers: {}, statusCode: 200,
    setHeader(k,v) { this.headers[k]=v; },
    status(code) { this.statusCode=code; return this; },
    json(body) { this.body=body; return this; }
  };
}
test('GET atlas reads the database and never returns raw vectors', async () => {
  process.env.SUPABASE_URL='https://example.supabase.co';
  process.env.SUPABASE_PUBLISHABLE_KEY='publishable-test';
  const original=globalThis.fetch;
  globalThis.fetch=async (url, options) => {
    assert.equal(url,'https://example.supabase.co/rest/v1/rpc/get_song_ci_atlas');
    assert.equal(options.method,'POST');
    assert.equal(options.headers.apikey,'publishable-test');
    return {ok:true,json:async()=>({documents:[{id:'test'}],neighbors:[[]],coordinates:{tsne:[[0,0]],umap:[[1,1]]},provenance:{}})};
  };
  try {
    const res=response(); await atlas({method:'GET'},res);
    assert.equal(res.statusCode,200);
    assert.equal(res.body.documents[0].id,'test');
    assert.match(res.headers['Vercel-CDN-Cache-Control'],/max-age/);
    assert(!JSON.stringify(res.body).includes('embedding'));
  } finally { globalThis.fetch=original; }
});
test('unsupported methods and malformed poem IDs do not reach Supabase', async () => {
  for (const handler of [atlas,neighbors]) {
    const res=response(); await handler({method:'POST',query:{}},res);
    assert.equal(res.statusCode,405);
    assert.equal(res.headers.Allow,'GET');
  }
  for (const id of ['',"' OR true --",['one','two']]) {
    const res=response(); await neighbors({method:'GET',query:{id}},res);
    assert.equal(res.statusCode,400);
  }
});
test('missing database configuration fails closed without leaking credentials', async () => {
  const saved=process.env.SUPABASE_URL;delete process.env.SUPABASE_URL;
  try {
    const res=response(); await atlas({method:'GET'},res);
    assert.equal(res.statusCode,503);
    assert.deepEqual(res.body,{error:'Poetry database is temporarily unavailable.'});
    assert.equal(res.headers['Cache-Control'],'no-store');
  } finally { process.env.SUPABASE_URL=saved; }
});
test('nearest-poem API passes a bounded poem ID to the exact database RPC', async () => {
  const original=globalThis.fetch;
  globalThis.fetch=async (url,options)=>{
    assert(url.endsWith('/rpc/song_ci_neighbors'));
    assert.deepEqual(JSON.parse(options.body),{poem_id:'guwendao-e997157ee4aa'});
    return {ok:true,json:async()=>[{index:74,cosine:.8}]};
  };
  try {
    const res=response(); await neighbors({method:'GET',query:{id:'guwendao-e997157ee4aa'}},res);
    assert.equal(res.body[0].index,74);
  } finally {globalThis.fetch=original;}
});

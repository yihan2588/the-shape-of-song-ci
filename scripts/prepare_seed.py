"""Prepare deterministic import SQL from the verified local corpus and vectors.

Writes to a caller-provided scratch directory, never to the deployed web assets.
Apply batches with Supabase MCP execute_sql under the database owner role.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('output', type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
source = root / 'data/atlas.json'
data = json.loads(source.read_text())
vector_path = root / 'data/derived/embeddings.npy'
vectors = np.load(vector_path)
assert vectors.shape == (len(data['documents']), 2560)
assert np.isfinite(vectors).all()
assert np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)

def quote(value):
    return "'" + value.replace("'", "''") + "'"

def js(value):
    return quote(json.dumps(value, ensure_ascii=False, separators=(',', ':'))) + '::jsonb'

rows = []
for i, doc in enumerate(data['documents']):
    vector = '[' + ','.join(format(float(v), '.9g') for v in vectors[i]) + ']'
    rows.append(f"({i},{quote(doc['id'])},{js(doc)},{js(data['coordinates']['tsne'][i])},{js(data['coordinates']['umap'][i])},{quote(vector)}::extensions.vector(2560))")
for batch, start in enumerate(range(0, len(rows), 8)):
    sql = 'insert into atlas_private.poems (position,id,document,tsne,umap,embedding) values\n'
    sql += ',\n'.join(rows[start:start+8])
    sql += '\non conflict (position) do update set id=excluded.id, document=excluded.document, tsne=excluded.tsne, umap=excluded.umap, embedding=excluded.embedding;\n'
    (args.output / f'batch-{batch:03}.sql').write_text(sql)
meta = "insert into atlas_private.datasets (id,provenance,expected_count) values ('guwendao-v3',"
meta += js(data['provenance']) + f",{len(rows)}) on conflict (id) do update set provenance=excluded.provenance,expected_count=excluded.expected_count;\n"
(args.output / 'metadata.sql').write_text(meta)
(args.output / 'audit.json').write_text(json.dumps({'documents':len(rows),'dimensions':2560,'embedding_sha256':hashlib.sha256(vector_path.read_bytes()).hexdigest(),'batches':(len(rows)+7)//8},indent=2))
print((args.output / 'audit.json').read_text())

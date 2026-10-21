"""Compare an API payload with the source atlas and exact local cosine results."""
import argparse, json
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('payload', type=Path)
parser.add_argument('--report', type=Path)
args = parser.parse_args()
expected = json.loads((root / 'data/atlas.json').read_text())
actual = json.loads(args.payload.read_text())
for key in ['documents', 'coordinates', 'provenance']:
    assert actual[key] == expected[key], f'{key} changed'
vectors = np.load(root / 'data/derived/embeddings.npy').astype(np.float64)
vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
cosine = vectors @ vectors.T
np.fill_diagonal(cosine, -np.inf)
largest_error = 0
for i, neighbors in enumerate(actual['neighbors']):
    ordered = np.argsort(-cosine[i], kind='stable')[:3].tolist()
    assert [n['index'] for n in neighbors] == ordered, f'Wrong ranking for poem {i}'
    assert [n['index'] for n in neighbors] == [n['index'] for n in expected['neighbors'][i]]
    for n in neighbors:
        largest_error = max(largest_error, abs(n['cosine'] - cosine[i, n['index']]))
assert largest_error < 1e-6, largest_error
assert all('embedding' not in doc for doc in actual['documents'])
report = {'poems':len(actual['documents']),'authors':len({d['poet'] for d in actual['documents']}),
          'dimensions':vectors.shape[1],'exact_neighbor_rankings_verified':len(actual['documents'])*3,
          'max_cosine_error':largest_error,'documents_unchanged':True,'coordinates_unchanged':True,
          'provenance_unchanged':True,'raw_vectors_in_payload':False}
print(json.dumps(report, indent=2))
if args.report:
    args.report.write_text(json.dumps(report, indent=2)+'\n')

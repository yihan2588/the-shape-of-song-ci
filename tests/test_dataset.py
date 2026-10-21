"""Integrity checks for the bundled, standalone application dataset."""
import hashlib
import json
import unittest
from pathlib import Path
import numpy as np

APP = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = json.loads((APP/'data/atlas.json').read_text())
        cls.corpus = json.loads((APP/'data/corpus.json').read_text())
        cls.vectors = np.load(APP/'data/derived/embeddings.npy')

    def test_snapshot_and_content_only_alignment(self):
        self.assertEqual(len(self.corpus), 240)
        self.assertEqual(len({d['poet'] for d in self.atlas['documents']}), 97)
        for record, document in zip(self.corpus, self.atlas['documents']):
            self.assertEqual(record['corpus_id'], document['id'])
            self.assertEqual(record['text_simplified'], document['text'])
        inputs = [json.loads(line) for line in (APP/'data/derived/embedding-inputs.jsonl').read_text().splitlines()]
        self.assertEqual(len(inputs), 240)
        for record, item in zip(self.corpus, inputs):
            self.assertEqual(set(item), {'doc_id', 'content'})
            self.assertEqual(item['content'], ' '.join(record['text_simplified'].split()))

    def test_vector_integrity_and_exact_neighbors(self):
        self.assertEqual(self.vectors.shape, (240,2560))
        self.assertTrue(np.isfinite(self.vectors).all())
        self.assertTrue(np.allclose(np.linalg.norm(self.vectors,axis=1),1,atol=1e-5))
        manifest = json.loads((APP/'data/derived/embedding-manifest.json').read_text())
        self.assertEqual(hashlib.sha256((APP/'data/derived/embeddings.npy').read_bytes()).hexdigest(), manifest['embeddings_sha256'])
        x = self.vectors.astype(np.float64)
        x /= np.linalg.norm(x,axis=1,keepdims=True)
        cosine = x@x.T
        np.fill_diagonal(cosine,-np.inf)
        for i, neighbors in enumerate(self.atlas['neighbors']):
            self.assertEqual([n['index'] for n in neighbors], np.argsort(-cosine[i],kind='stable')[:3].tolist())
            for n in neighbors:
                self.assertAlmostEqual(n['cosine'],cosine[i,n['index']],places=7)

    def test_only_two_fixed_views_and_consistent_provenance(self):
        self.assertEqual(set(self.atlas['coordinates']),{'tsne','umap'})
        for coordinates in self.atlas['coordinates'].values():
            self.assertEqual(np.array(coordinates).shape,(240,2))
            self.assertTrue(np.isfinite(coordinates).all())
        self.assertEqual(self.atlas['provenance'],json.loads((APP/'public/dataset-manifest.json').read_text()))


if __name__ == '__main__':
    unittest.main()

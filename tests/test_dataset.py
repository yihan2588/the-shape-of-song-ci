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
        self.assertEqual(len({d['poet'] for d in self.atlas['documents']}), 96)
        for record, document in zip(self.corpus, self.atlas['documents']):
            self.assertEqual(record['corpus_id'], document['id'])
            self.assertEqual(record['text_simplified'], document['text'])
        inputs = [json.loads(line) for line in (APP/'data/derived/embedding-inputs.jsonl').read_text().splitlines()]
        self.assertEqual(len(inputs), 240)
        for record, item in zip(self.corpus, inputs):
            self.assertEqual(set(item), {'doc_id', 'content'})
            self.assertEqual(item['content'], ' '.join(record['text_simplified'].split()))

    def test_first_listed_author_is_canonical(self):
        raw = json.loads((APP/'data/source/raw.json').read_text())
        expected = {r['url']: r['author'].replace('／','/').split('/')[0].strip() for r in raw}
        for record, doc in zip(self.corpus, self.atlas['documents']):
            self.assertEqual(doc['poet'],expected[doc['url']])
            self.assertEqual(record['requested_author'],doc['poet'])
            self.assertEqual(record['source_author'],doc['poet'])
            self.assertNotIn('/',doc['poet'])
        self.assertEqual(next(d for d in self.atlas['documents'] if d['id']=='guwendao-b827b3f18b38')['poet'],'冯延巳')
        self.assertEqual(next(d for d in self.atlas['documents'] if d['id']=='guwendao-c616fab1b377')['poet'],'欧阳修')
        self.assertEqual(next(d for d in self.atlas['documents'] if d['id']=='guwendao-c616fab1b377')['label'],'婉约派')

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

    def test_endpoint_imagery_evidence(self):
        evidence = json.loads((APP/'data/axis-imagery.json').read_text())
        self.assertEqual(evidence['poems'],len(self.atlas['documents']))
        expected = [['万里','千古','白发'],['黄昏','相思','落花']]
        public = json.loads((APP/'public/axis-imagery.js').read_text().split('window.SONG_CI_IMAGERY = ')[1].strip().removesuffix(';'))
        for view, result in evidence['views'].items():
            self.assertEqual([r['words'] for r in result['regions']],expected)
            self.assertGreater(result['direction'][0],0)
            self.assertEqual(result['horizons_at_top'],view=='umap')
            by_id = {d['id']:d['text'] for d in self.atlas['documents']}
            for i, region in enumerate(result['regions']):
                self.assertEqual(len(region['poem_ids']),60)
                self.assertEqual(public[view]['ends'][i]['counts'],region['evidence'][1]['counts'])
                opposite = result['regions'][1-i]['poem_ids']
                for term in region['evidence'][1]['counts']:
                    self.assertEqual(term['poems'],sum(term['bigram'] in by_id[id] for id in region['poem_ids']))
                    self.assertEqual(term['opposite_poems'],sum(term['bigram'] in by_id[id] for id in opposite))
                for sensitivity in region['evidence']:
                    for term in sensitivity['counts']:
                        self.assertEqual(len(term['bigram']),2)
                        self.assertGreater(term['poems'],term['opposite_poems'])
                        self.assertGreater(term['per_1000_han'],term['opposite_per_1000_han'])

    def test_only_two_fixed_views_and_consistent_provenance(self):
        self.assertEqual(set(self.atlas['coordinates']),{'tsne','umap'})
        for coordinates in self.atlas['coordinates'].values():
            self.assertEqual(np.array(coordinates).shape,(240,2))
            self.assertTrue(np.isfinite(coordinates).all())
        self.assertEqual(self.atlas['provenance'],json.loads((APP/'public/dataset-manifest.json').read_text()))


if __name__ == '__main__':
    unittest.main()

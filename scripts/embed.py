"""Local, content-only whole-poem embeddings. No metadata or instruction prefix."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')


def content_only(record):
    # Whitespace normalization only; keep punctuation and every content paragraph.
    return ' '.join(record['text_simplified'].split())


def main():
    import numpy as np
    import torch
    from huggingface_hub import HfApi, snapshot_download
    from sentence_transformers import SentenceTransformer
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='Qwen/Qwen3-Embedding-4B')
    parser.add_argument('--revision', default=None)
    parser.add_argument('--batch-size', type=int, default=4)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--corpus', type=Path, default=ROOT / 'data/corpus.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/derived')
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    corpus_file = args.corpus
    records = [r for r in json.loads(corpus_file.read_text()) if r['era'] == '宋词']
    texts = [content_only(r) for r in records]
    assert records and all(texts)
    payload = '\n'.join(json.dumps({'doc_id': r['corpus_id'], 'content': t}, ensure_ascii=False)
                        for r, t in zip(records, texts)) + '\n'
    payload_hash = hashlib.sha256(payload.encode()).hexdigest()
    revision = args.revision
    if not args.offline:
        revision = HfApi().model_info(args.model, revision=revision).sha
    assert revision, 'Offline mode requires --revision with the recorded commit.'
    print(f'Downloading/loading {args.model} at {revision}', flush=True)
    model_dir = snapshot_download(args.model, revision=revision, local_files_only=args.offline,
                                  allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model', '*.vocab', '*.merges'])
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    dtype = torch.float16 if device == 'mps' else torch.float32
    print(f'Device {device}; dtype {dtype}', flush=True)
    started = time.time()
    torch.set_num_threads(6)
    model = SentenceTransformer(model_dir, device=device, trust_remote_code=False,
                                model_kwargs={'torch_dtype': dtype, 'attn_implementation': 'sdpa'})
    lengths = [len(model.tokenizer(t, truncation=False)['input_ids']) for t in texts]
    assert max(lengths) <= model.max_seq_length, 'Refusing to truncate a poem.'
    print(f'{len(texts)} poems; max tokens={max(lengths)}; limit={model.max_seq_length}', flush=True)
    (out / 'embedding-inputs.jsonl').write_text(payload)
    metadata = [{k: r[k] for k in ['corpus_id', 'requested_author', 'style_label', 'title_simplified', 'rhythmic']}
                | {'content': t, 'token_count': n, 'content_sha256': hashlib.sha256(t.encode()).hexdigest()}
                for r, t, n in zip(records, texts, lengths)]
    (out / 'documents.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    # Chunk checkpointing: interrupted runs resume without repeating completed chunks.
    identity = {'model': args.model, 'revision': revision, 'input_sha256': payload_hash,
                'normalization': 'L2', 'prompt': '', 'dtype': str(dtype), 'device': device}
    chunks = ROOT / '.cache' / 'chunks'
    chunks.mkdir(parents=True, exist_ok=True)
    cache_id = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    vectors = []
    for start in range(0, len(texts), 32):
        target = chunks / f'{cache_id}-{start:04d}.npy'
        if target.exists():
            vector = np.load(target)
        else:
            vector = model.encode(texts[start:start+32], batch_size=args.batch_size,
                                  normalize_embeddings=True, convert_to_numpy=True,
                                  prompt='', show_progress_bar=False).astype(np.float32)
            np.save(target, vector)
        vectors.append(vector)
        print(f'Embedded {min(start+32,len(texts))}/{len(texts)} ({time.time()-started:.1f}s)', flush=True)
    vectors = np.concatenate(vectors)
    assert vectors.shape[0] == len(texts) and np.isfinite(vectors).all()
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=2e-3)
    # Re-normalize in float32 to remove half-precision normalization error.
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    repeat = model.encode(texts[:2], batch_size=2, normalize_embeddings=True,
                          convert_to_numpy=True, prompt='', show_progress_bar=False).astype(np.float32)
    repeat /= np.linalg.norm(repeat, axis=1, keepdims=True)
    repeat_cosines = np.sum(vectors[:2] * repeat, axis=1)
    assert np.all(repeat_cosines > .999), 'Unexpected batch-dependent embedding inconsistency.'
    np.save(out / 'embeddings.npy', vectors)
    manifest = identity | {'shape': list(vectors.shape), 'max_tokens': max(lengths),
                           'model_max_seq_length': model.max_seq_length, 'truncated_poems': 0,
                           'unique_content_count': len(set(texts)), 'seconds': time.time()-started,
                           'corpus_sha256': hashlib.sha256(corpus_file.read_bytes()).hexdigest(),
                           'platform': platform.platform(), 'torch': torch.__version__,
                           'repeat_inference_cosines': repeat_cosines.tolist(),
                           'embeddings_sha256': hashlib.sha256((out/'embeddings.npy').read_bytes()).hexdigest()}
    (out / 'embedding-manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == '__main__':
    main()

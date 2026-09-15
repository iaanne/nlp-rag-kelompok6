"""Step 1 — Ingest standar.

Perbaikan vs notebook lama:
- Notebook lama index 86 QA (question+answer) sebagai 86 dokumen.
- Di sini 86 QA di-group by chunk_id -> 37 passage CHUNK.
  Ini retrieval level passage yang benar untuk RAG (bukan QA-pair lookup).
- Embedding EKSPLISIT via sentence-transformers (bukan default implisit Chroma).
- Metadata kaya + persist lokal ./chroma_db (bukan /content ephemeral).
- Tanpa data baru: hanya olah ulang 86 baris yang sama.
"""
import json
from collections import defaultdict
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from .config import CHROMA_DIR, COLLECTION, DATA_PATH, EMB_MODEL


def load_qa_rows(path: Path = DATA_PATH):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    return rows


def build_chunk_passages(rows):
    """Group QA -> 1 passage per chunk_id. Return list dict."""
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["chunk_id"]].append(r)
    passages = []
    for chunk_id, qs in sorted(grouped.items()):
        text = "\n\n".join(f"Q: {q['question']}\nA: {q['answer']}" for q in qs)
        passages.append({
            "id": chunk_id.replace("EWS.v5.CHUNK", "EWS.v5.PASSAGE"),
            "chunk_id": chunk_id,
            "document": text,
            "metadata": {
                "chunk_id": chunk_id,
                "n_qa": len(qs),
                "source": "Emergency War Surgery v5 (PUBLIC_DOMAIN)",
                "hf_dataset": "Paxrad/EWS_v5_USONLY_final",
            },
        })
    return passages


def ingest(rebuild: bool = False):
    rows = load_qa_rows()
    passages = build_chunk_passages(rows)
    print(f"rows={len(rows)} -> passages={len(passages)}")

    model = SentenceTransformer(EMB_MODEL)
    ids = [p["id"] for p in passages]
    docs = [p["document"] for p in passages]
    metas = [p["metadata"] for p in passages]
    embs = model.encode(docs, normalize_embeddings=True, show_progress_bar=False).tolist()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if rebuild:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
    col = client.get_or_create_collection(COLLECTION)
    if col.count() == 0 or rebuild:
        col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embs)
    print(f"collection={COLLECTION} count={col.count()} emb={EMB_MODEL}")
    assert col.count() == 37, f"expected 37 passages, got {col.count()}"
    return col


if __name__ == "__main__":
    ingest(rebuild=True)

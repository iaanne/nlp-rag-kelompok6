#!/usr/bin/env python3
import json
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION = "ews_medical_qa"
JSONL_PATH = Path(__file__).parent / "EWS_v5_USONLY_final" / "EWS_v5_USONLY_final_QA.jsonl"
DIM = 384
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    client = QdrantClient(url="http://localhost:6333")

    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
    )
    print(f"[+] Created collection: {COLLECTION}")

    model = SentenceTransformer(MODEL_NAME)
    print(f"[+] Loaded model: {MODEL_NAME}")

    points = []
    for idx, line in enumerate(JSONL_PATH.open()):
        record = json.loads(line.strip())
        q = record["question"]
        a = record["answer"]
        chunk_id = record.get("chunk_id", "")
        text = f"Q: {q}\nA: {a}"
        vec = model.encode(text).tolist()
        points.append(PointStruct(
            id=idx,
            vector=vec,
            payload={"question": q, "answer": a, "chunk_id": chunk_id},
        ))

    client.upsert(collection_name=COLLECTION, points=points)
    print(f"[+] Ingested {len(points)} records")


if __name__ == "__main__":
    main()

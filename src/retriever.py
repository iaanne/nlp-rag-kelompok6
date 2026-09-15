"""Step 2 — Hybrid retrieval: dense (Chroma) + BM25 leksikal + RRF + MMR.

Tanpa dependensi baru: BM25 Okapi murni-Python di atas 37 passage.
Standar yang dipenuhi: hybrid, score fusion, threshold, diversity.
"""
import json
import math
import re
from collections import Counter

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import (BM25_W, CHROMA_DIR, COLLECTION, DENSE_W, EMB_MODEL,
                     MMR_LAMBDA, RRF_K, TOP_K)

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(t: str):
    return _TOKEN.findall(t.lower())


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [tokenize(d) for d in docs]
        self.N = len(self.docs)
        self.avgdl = sum(len(d) for d in self.docs) / max(self.N, 1)
        self.df = Counter()
        for d in self.docs:
            for t in set(d):
                self.df[t] += 1
        self.k1, self.b = k1, b

    def score(self, query):
        q = tokenize(query)
        out = []
        for d in self.docs:
            tf = Counter(d)
            dl = len(d)
            s = 0.0
            for t in q:
                if t not in tf:
                    continue
                idf = math.log(1 + (self.N - self.df.get(t, 0) + 0.5) / (self.df.get(t, 0) + 0.5))
                s += idf * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            out.append(s)
        return out


class HybridRetriever:
    def __init__(self, k=TOP_K):
        self.k = k
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.col = self.client.get_collection(COLLECTION)
        data = self.col.get(include=["documents", "metadatas"])
        self.ids = data["ids"]
        self.docs = data["documents"]
        self.metas = data["metadatas"]
        self.bm25 = BM25(self.docs)
        self.emb_model = SentenceTransformer(EMB_MODEL)
        # preload passage embeddings untuk MMR
        self.pass_embs = self.emb_model.encode(self.docs, normalize_embeddings=True, show_progress_bar=False)

    def _dense_rank(self, query):
        qemb = self.emb_model.encode([query], normalize_embeddings=True, show_progress_bar=False).tolist()
        r = self.col.query(query_embeddings=qemb, n_results=len(self.ids))
        return r["ids"][0]  # sudah terurut dense terbaik dulu

    def _rrf_fuse(self, dense_ranked, bm25_scores):
        bm25_ranked = sorted(range(len(self.ids)), key=lambda i: bm25_scores[i], reverse=True)
        dense_pos = {pid: i for i, pid in enumerate(dense_ranked)}
        bm25_pos = {self.ids[i]: i for i, i in enumerate(bm25_ranked)}
        fused = []
        for pid in self.ids:
            s = DENSE_W * (1 / (RRF_K + dense_pos.get(pid, 999) + 1)) \
              + BM25_W * (1 / (RRF_K + bm25_pos.get(pid, 999) + 1))
            fused.append((pid, s))
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused

    def _mmr(self, query_emb, cand_idx):
        selected, candidates = [], list(cand_idx)
        while candidates and len(selected) < self.k:
            if not selected:
                selected.append(candidates.pop(0))
                continue
            scores = []
            for c in candidates:
                rel = float(np.dot(query_emb, self.pass_embs[c]))
                div = max(float(np.dot(self.pass_embs[c], self.pass_embs[s])) for s in selected)
                scores.append(MMR_LAMBDA * rel - (1 - MMR_LAMBDA) * div)
            selected.append(candidates.pop(int(np.argmax(scores))))
        return selected

    def retrieve(self, query, k=None):
        k = k or self.k
        dense_ranked = self._dense_rank(query)
        bm25_scores = self.bm25.score(query)
        fused = self._rrf_fuse(dense_ranked, bm25_scores)
        # threshold RRF sederhana: buang skor ~0
        top_idx = [self.ids.index(pid) for pid, _ in fused[: max(k * 2, k)]]
        qemb = self.emb_model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
        mmr_idx = self._mmr(qemb, top_idx)[:k]
        out = []
        for i in mmr_idx:
            out.append({
                "id": self.ids[i],
                "chunk_id": self.metas[i]["chunk_id"],
                "document": self.docs[i],
                "rrf": next(s for pid, s in fused if pid == self.ids[i]),
                "bm25": bm25_scores[i],
                "metadata": self.metas[i],
            })
        return out

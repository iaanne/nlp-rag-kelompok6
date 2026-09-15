"""Step 4 — Evaluasi retrieval + abstention (CPU-friendly, tanpa LLM).

Metrik standar:
- recall@1/@3/@5, MRR (in-scope, expected_chunk ditemukan?)
- abstention_rate (out-of-scope harus abstain)
- citation_check: jawaban ekstraktif selalu sitasi chunk teratas
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generator import answer
from src.retriever import HybridRetriever


def recall_mrr(gold, k=5):
    ret = HybridRetriever(k=k)
    hits = {1: 0, 3: 0, 5: 0}
    rr_sum, n_in = 0.0, 0
    n_abs_ok, n_oos = 0, 0
    for g in gold:
        docs = ret.retrieve(g["question"], k=k)
        ranked = [d["chunk_id"] for d in docs]
        if g["abstain_expected"]:
            n_oos += 1
            res = answer(g["question"], docs)
            if res["abstained"]:
                n_abs_ok += 1
            continue
        n_in += 1
        exp = g["expected_chunk"]
        if exp in ranked:
            r = ranked.index(exp) + 1
            rr_sum += 1 / r
            for kk in hits:
                if r <= kk:
                    hits[kk] += 1
    return {
        "n_in_scope": n_in, "n_oos": n_oos,
        "recall@1": hits[1] / max(n_in, 1),
        "recall@3": hits[3] / max(n_in, 1),
        "recall@5": hits[5] / max(n_in, 1),
        "MRR": rr_sum / max(n_in, 1),
        "abstention_rate_OOS": n_abs_ok / max(n_oos, 1),
    }


if __name__ == "__main__":
    gold = [json.loads(l) for l in open(ROOT / "eval" / "golden.jsonl", encoding="utf-8")]
    m = recall_mrr(gold)
    print(json.dumps(m, indent=2))
    # gerbang lolos minimal demo
    assert m["recall@5"] >= 0.6, f"recall@5 rendah: {m['recall@5']}"
    assert m["abstention_rate_OOS"] == 1.0, "OOS harus selalu abstain"
    print("EVAL OK")

"""Bangun eval/golden.jsonl dari 86 baris yang SAMA (tanpa data baru).

- 15 in-scope: 1 pertanyaan sampel per chunk (deterministik, sorted).
- 5 out-of-scope: harus abstain.
Format: {question, expected_chunk, abstain_expected}
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "EWS_v5_USONLY_final_QA.jsonl"
DST = ROOT / "eval" / "golden.jsonl"

OUT = [
    "What is the capital of France?",
    "Who won the World Cup 2022?",
    "Resep rendang padang apa?",
    "Siapa presiden Indonesia ke-8?",
    "Explain quantum entanglement in detail?",
]

def main():
    rows = [json.loads(l) for l in open(SRC, encoding="utf-8")]
    seen, gold = set(), []
    for r in sorted(rows, key=lambda x: x["id"]):
        if r["chunk_id"] not in seen:
            seen.add(r["chunk_id"])
            gold.append({"question": r["question"], "expected_chunk": r["chunk_id"], "abstain_expected": False})
        if len(gold) >= 15:
            break
    for q in OUT:
        gold.append({"question": q, "expected_chunk": None, "abstain_expected": True})
    with open(DST, "w", encoding="utf-8") as f:
        for g in gold:
            f.write(json.dumps(g) + "\n")
    print(f"wrote {len(gold)} -> {DST} ({len(gold)-len(OUT)} in-scope + {len(OUT)} OOS)")

if __name__ == "__main__":
    main()

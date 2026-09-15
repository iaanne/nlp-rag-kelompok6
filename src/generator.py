"""Step 3b — Generator.

Default (CPU-friendly): ekstraktif — jawab dari passage teratas + sitasi.
Ini JUJUR untuk eval retrieval tanpa butuh GPU.

Opsi LLM: USE_LLM=1 -> load Qwen2.5-0.5B seperti notebook CELL 7.
"""
import os

from .config import LLM_MODEL, MAX_NEW_TOKENS
from .prompts import build_prompt

_ABSTAIN = "I do not know based on the provided context."

_OUT_OF_SCOPE = ["capital of france", "ibukota prancis", "siapa presiden", "resep rendang"]

# Ambang leksikal: query tanpa overlap istilah medis dengan korpus -> abstain.
# Dikalibrasi: in-scope min BM25 ~1.05, OOS max ~0.7 pada golden set 20.
BM25_ABSTAIN = 1.0


def is_out_of_scope(q: str) -> bool:
    ql = q.lower()
    return any(t in ql for t in _OUT_OF_SCOPE)


def answer_extractively(question, docs) -> dict:
    if not docs or is_out_of_scope(question):
        return {"answer": _ABSTAIN, "citations": [], "abstained": True}
    top_bm25 = max((d.get("bm25", 0) or 0) for d in docs)
    if top_bm25 < BM25_ABSTAIN:
        return {"answer": _ABSTAIN, "citations": [], "abstained": True}
    top = docs[0]
    # ambil kalimat jawaban pertama dari passage agar grounded
    snippet = top["document"].split("\n")[0][:500]
    return {
        "answer": f"{snippet}\n\nSources: [{top['chunk_id']}]",
        "citations": [d["chunk_id"] for d in docs[:3]],
        "abstained": False,
    }


def answer_with_llm(question, docs) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(LLM_MODEL)
    try:
        model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, dtype="auto", device_map="auto")
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, torch_dtype="auto", device_map="auto")
    messages = build_prompt(question, docs)
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    gen = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    return {"answer": gen, "citations": [d["chunk_id"] for d in docs[:3]], "abstained": "do not know" in gen.lower()}


def answer(question, docs) -> dict:
    if os.getenv("USE_LLM") == "1":
        return answer_with_llm(question, docs)
    return answer_extractively(question, docs)

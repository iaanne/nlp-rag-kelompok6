"""Step 3a — Prompt berversi. Satu tempat, bisa di-audit."""
from .config import PROMPT_VERSION

SYSTEM_V1 = (
    "You are a field triage assistant. Answer ONLY using the context below. "
    "Cite sources as [chunk_id]. If the answer is not in the context, say you do not know. "
    "This is for education, not clinical advice."
)

def build_prompt(question, docs, version=PROMPT_VERSION):
    assert version == "v1", f"unknown prompt {version}"
    ctx = "\n\n".join(f"[{d['chunk_id']}] {d['document'][:1500]}" for d in docs)
    messages = [
        {"role": "system", "content": SYSTEM_V1},
        {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {question}"},
    ]
    return messages

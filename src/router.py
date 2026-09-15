"""Step 3c — Router: /check (angka vital) vs RAG (tanya konsep)."""
import re

from .ews import ews
from .generator import answer
from .retriever import HybridRetriever

_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def parse_check(cmd: str) -> dict:
    kv = {k.upper(): v for k, v in re.findall(r"(\w+)\s*=\s*([\w./]+)", cmd)}
    v = {"HR": 70, "SYS": 120, "RR": 16, "SPO2": 98, "T": 36.8, "AVPU": "A", "O2": "air"}
    if "HR" in kv: v["HR"] = float(kv["HR"])
    if "SYS" in kv: v["SYS"] = float(kv["SYS"])
    if "BP" in kv: v["SYS"] = float(kv["BP"].split("/")[0])
    if "RR" in kv: v["RR"] = float(kv["RR"])
    if "SPO2" in kv: v["SPO2"] = float(kv["SPO2"])
    if "T" in kv: v["T"] = float(kv["T"])
    if "TEMP" in kv: v["T"] = float(kv["TEMP"])
    if "AVPU" in kv: v["AVPU"] = kv["AVPU"]
    if "GCS" in kv: v["GCS"] = int(float(kv["GCS"]))
    if "O2" in kv: v["O2"] = kv["O2"]
    return v


def route(text: str) -> dict:
    if text.strip().lower().startswith("/check"):
        total, band, parts, advice = ews(parse_check(text))
        return {"type": "ews", "total": total, "band": band, "parts": parts, "advice": advice}
    docs = get_retriever().retrieve(text)
    res = answer(text, docs)
    res["type"] = "rag"
    res["docs"] = [{"chunk_id": d["chunk_id"], "rrf": d["rrf"]} for d in docs]
    return res

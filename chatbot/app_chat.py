"""Chatbot RAG EWS (Streamlit chat, tanpa n8n).

Jalankan dari root repo: streamlit run chatbot/app_chat.py
Fitur: riwayat chat, sitasi [chunk_id], abstain OOS, /check kalkulator EWS.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st

from src.router import route

st.set_page_config(page_title="Chatbot RAG EWS", page_icon="💬")
st.title("💬 Chatbot RAG EWS (edukasi, bukan alat klinis)")

if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "assistant",
         "content": "Halo! Tanya konsep EWS atau ketik `/check HR=.. SYS=.. RR=.. SPO2=.. T=.. AVPU=.. O2=..` untuk skor."}
    ]

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("citations"):
            st.caption("Rujukan: " + ", ".join(f"[{c}]" for c in m["citations"]))
        if m.get("docs") is not None:
            with st.expander("Detail retrieval"):
                st.json(m["docs"])

q = st.chat_input("Tulis pertanyaan / perintah /check ...")
if q:
    st.session_state.history.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.write(q)
    res = route(q)
    if res["type"] == "ews":
        content = f"EWS={res['total']} [{res['band']}] — {res['advice']}\n\n" + \
                  "\n".join(f"{k}: {s}" for k, s in res["parts"].items())
        msg = {"role": "assistant", "content": content}
    else:
        msg = {"role": "assistant", "content": res["answer"],
               "citations": res.get("citations", []), "docs": res.get("docs", [])}
    st.session_state.history.append(msg)
    with st.chat_message("assistant"):
        st.write(msg["content"])
        if msg.get("citations"):
            st.caption("Rujukan: " + ", ".join(f"[{c}]" for c in msg["citations"]))
        if msg.get("docs") is not None:
            with st.expander("Detail retrieval"):
                st.json(msg["docs"])

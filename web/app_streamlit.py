"""Web demo form (Streamlit). Panel jawaban + rujukan + skor EWS.

Jalankan dari root repo: streamlit run web/app_streamlit.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st

from src.router import route

st.title("RAG EWS — demo (edukasi, bukan alat klinis)")
q = st.text_input("Tanya konsep atau /check HR=.. SYS=.. RR=.. SPO2=.. T=.. AVPU=.. O2=..",
                  "Which chapter discusses the Glasgow Coma Scale?")
if st.button("Kirim") and q:
    res = route(q)
    if res["type"] == "ews":
        st.metric("EWS", f"{res['total']} [{res['band']}]")
        st.json(res["parts"])
        st.info(res["advice"])
    else:
        st.write(res["answer"])
        st.caption("Rujukan: " + ", ".join(f"[{c}]" for c in res["citations"]))
        with st.expander("Detail retrieval"):
            st.json(res["docs"])

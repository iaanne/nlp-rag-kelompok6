# RAG EWS Kelompok 6 — Tanya Jawab Emergency War Surgery + Kalkulator Skor

Chatbot RAG (tanpa n8n) di atas 86 QA Emergency War Surgery (EWS v5, public domain)
dengan retrieval hybrid, sitasi `[chunk_id]`, penolakan pertanyaan di luar konteks,
dan kalkulator skor EWS rule-based. Demo edukasi, **bukan alat medis klinis**.

## Arsitektur

```text
pertanyaan ──> router ──┬── /check angka vital ──> kalkulator EWS (rule-based NEWS2)
                        └── tanya konsep ──> hybrid retrieval ──> jawab + sitasi
                                                   dense Chroma + BM25 --RRF--> MMR top-5
```

* **Data:** `data/EWS_v5_USONLY_final_QA.jsonl` — 86 QA dari `Paxrad/EWS_v5_USONLY_final`
  (HF mirror + GitHub mirror, file yang sama). Di-ingest ulang jadi **37 passage**
  per `chunk_id`, embedding eksplisit `sentence-transformers/all-MiniLM-L6-v2`,
  tersimpan di `./chroma_db` (diabaikan git).
* **Retrieval:** hybrid dense + BM25 Okapi (murni-Python) + fusi RRF + MMR,
  abstain ganda (keyword + ambang BM25 `1.0`).
* **Generasi default:** ekstraktif + sitasi (CPU-friendly). Opsi LLM
  `Qwen/Qwen2.5-0.5B-Instruct` via `USE_LLM=1` (butuh VRAM/GPU).
* **Output 2 cabang:** `web/` (form demo) dan `chatbot/` (chat terminal + chat web).

## Struktur

```text
data/        86 QA EWS (86 baris, 37 chunk unik)
src/         config, ingest, retriever, prompts, generator, router, ews
eval/        golden 20 (15 in-scope + 5 OOS) + skrip evaluasi recall/MRR/abstain
web/         demo form Streamlit
chatbot/     chat terminal (chat_cli) + chat web Streamlit (app_chat)
notebooks/   notebook awal (arsip; pipeline utama sudah pindah ke src/)
```

## Instalasi (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Cara pakai, berurutan

```powershell
# 0. Aktifkan venv (setiap terminal baru)
.\.venv\Scripts\Activate.ps1

# 1. Ingest: 86 QA -> 37 passage. Harus keluar: rows=86 -> passages=37, count=37
python -m src.ingest

# 2. Bangun golden set eval (dari 86 baris yang sama, tanpa data baru)
python -m eval.build_golden

# 3. Evaluasi. Harus keluar EVAL OK:
#    recall@1 0.87, recall@3 1.0, recall@5 1.0, MRR 0.93, abstention OOS 1.0
python -m eval.evaluate

# 4a. Chatbot terminal
python -m chatbot.chat_cli
# contoh di dalam CLI:
#   Which chapter discusses the Glasgow Coma Scale?   -> [CHUNK0002]
#   What is the capital of France?                   -> abstain
#   /check HR=125 SYS=88 RR=29 SPO2=90 T=39.5 AVPU=V O2=oxygen -> EWS=18 [HIGH]

# 4b. Chatbot web (chat bubble + history + rujukan)
streamlit run chatbot/app_chat.py

# 4c. Web demo form (input + tombol)
streamlit run web/app_streamlit.py

# 5. LLM generatif (opsional, berat). Default ekstraktif agar jalan di CPU.
$env:USE_LLM = "1"
python -m chatbot.chat_cli
```

Format `/check`: `/check HR=.. SYS=.. RR=.. SPO2=.. T=.. AVPU=.. O2=..`
(alias: `BP=120/80` untuk sistolik, `GCS=..` pengganti `AVPU`, `TEMP=` pengganti `T`).

## Checklist uji (hasil terakhir, lolos semua)

| # | Perintah | Harapan | Hasil |
|---|----------|---------|-------|
| 1 | `python -m src.ingest` | `rows=86 -> passages=37`, `count=37` | OK |
| 2 | `python -m eval.build_golden` | `wrote 20 (15 + 5 OOS)` | OK |
| 3 | `python -m eval.evaluate` | `EVAL OK`, recall@5 1.0, abstain 1.0 | OK |
| 4 | `route(GCS)` | jawab + `[EWS.v5.CHUNK0002]` | OK |
| 5 | `route(capital of France)` | `I do not know...`, abstained | OK |
| 6 | `route(/check gawat)` | `EWS=18 [HIGH]` | OK |
| 7 | `chat_cli` piped 3 baris | RAG + EWS + exit 0 | OK |
| 8 | `py_compile` semua `.py` | no error | OK |
| 9 | `streamlit run chatbot/app_chat.py` / `web/app_streamlit.py` | terbuka, chat + form jalan | OK |

## Batas yang diketahui

* Jawaban default ekstraktif (bukan paragraf LLM) agar deterministik di CPU.
* Ambang abstain BM25 `1.0` dikalibrasi pada golden 20 — kalibrasi ulang jika korpus berubah.
* Notebook `notebooks/` arsip; sumber kebenaran pipeline = `src/`.
* LLM 0.5B terlalu kecil untuk nasihat medis nyata — proyek ini edukasi RAG, bukan pengganti dokter.

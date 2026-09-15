"""Konfigurasi tunggal RAG EWS. Ubah di sini, bukan di tiap file."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "EWS_v5_USONLY_final_QA.jsonl"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION = "ews_v5_chunks"

# Embedding eksplisit, ringan untuk CPU. Ganti ke BAAI/bge-m3 jika ada GPU.
EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Retrieval
TOP_K = 5
RRF_K = 60
DENSE_W = 0.7
BM25_W = 0.3
MIN_SCORE = 0.0  # threshold RRF; naikkan jika terlalu banyak false positive
MMR_LAMBDA = 0.7

# Generation
PROMPT_VERSION = "v1"
LLM_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_NEW_TOKENS = 256

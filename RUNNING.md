# RAG System - Quick Start

## Status Service

| Service | Port | Status |
|---------|------|--------|
| Qdrant | 6333 | ✅ Running |
| Flask API | 5677 | ✅ Running |
| Frontend | 8081 | ✅ Running |
| n8n | 5678 | ✅ Running (workflow perlu import manual via UI) |

## Test Endpoint
```bash
curl -X POST http://localhost:5677/webhook/rag-chat \
  -H "Content-Type: application/json" \
  -d '{"query":"How to treat hemorrhage in the field?"}'
```

## Akses UI
Buka browser: **http://localhost:8081**

## Restart Semua Service
```bash
# Qdrant (Docker)
docker start qdrant

# API server
cd /home/thufail/Documents/nlp
python3 api_server.py

# Frontend
cd /home/thufail/Documents/nlp/html
python3 -m http.server 8081
```

## Ingest Ulang Data
```bash
cd /home/thufail/Documents/nlp
python3 ingest.py
```

## Catatan
- Response masih "SIMULATED" — connect OpenAI/Ollama untuk jawaban LLM
- n8n workflow JSON tersedia di `n8n_rag_workflow.json` untuk import manual via UI

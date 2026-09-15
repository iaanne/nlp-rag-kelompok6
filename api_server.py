#!/usr/bin/env python3
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)

COLLECTION = "ews_medical_qa"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 8

model = SentenceTransformer(MODEL_NAME)
client = QdrantClient(url="http://localhost:6333")

print(f"[+] Model: {MODEL_NAME}")


# Keywords untuk boost relevance
KEYWORDS = {
    "perdarahan": ["hemorrhage", "bleeding", "blood loss", "hemorrhagic"],
    "pendarahan": ["hemorrhage", "bleeding", "blood loss"],
    "darah": ["blood", "hemorrhage", "transfusion"],
    "crush": ["crush syndrome", "rhabdomyolysis", "crush injury"],
    "luka bakar": ["burn", "thermal injury", "burn injury"],
    "pneumothorax": ["pneumothorax", "tension pneumothorax"],
    "trauma": ["trauma", "injury", "injuries"],
    "resusitasi": ["resuscitation", "fluid", "IV"],
    "cairan": ["IV fluid", "crystalloid", "colloid"],
    "syok": ["shock", "hypovolemic", "hemorrhagic shock"],
}


def calculate_relevance_score(question, query):
    """Calculate keyword matching score."""
    q_lower = question.lower()
    score = 0

    for kw_list in KEYWORDS.values():
        for kw in kw_list:
            if kw in q_lower:
                score += 1

    # Boost exact matches
    query_words = query.lower().split()
    for word in query_words:
        if len(word) > 3 and word in q_lower:
            score += 2

    return score


@app.route("/webhook/rag-chat", methods=["POST"])
def rag_chat():
    body = request.get_json() or {}
    query = body.get("query", "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400

    # Semantic search
    q_vec = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION,
        query=q_vec,
        limit=TOP_K,
        with_payload=True,
    ).points

    if not results:
        return jsonify({
            "answer": "Maaf, tidak ada informasi yang cocok dalam database.",
            "context_used": 0
        })

    # Score and rank results
    scored_results = []
    for r in results:
        q = r.payload.get("question", "")
        a = r.payload.get("answer", "")
        if q and a:
            score = calculate_relevance_score(q, query)
            scored_results.append((score, q, a))

    # Sort by score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # Filter: take only results with score > 0, max 5
    relevant = [(s, q, a) for s, q, a in scored_results if s > 0][:5]

    # If no keyword matches, take top 3 semantic results
    if not relevant:
        relevant = scored_results[:3]

    # Build natural response
    if len(relevant) == 1:
        answer = f"**📚 Ditemukan 1 dokumen yang relevan:**\n\n"
        answer += f"**{relevant[0][1]}**\n{relevant[0][2]}\n"
    else:
        answer = f"**📚 Ditemukan {len(relevant)} dokumen yang relevan:**\n\n"
        for i, (score, q, a) in enumerate(relevant, 1):
            # Clean up question format
            clean_q = q
            # Remove common prefixes (order matters - longest first)
            clean_q = re.sub(r'^What should be done\s*', '', clean_q, flags=re.IGNORECASE)
            clean_q = re.sub(r'^What is the\s*', '', clean_q, flags=re.IGNORECASE)
            clean_q = re.sub(r'^What are the\s*', '', clean_q, flags=re.IGNORECASE)
            clean_q = re.sub(r'^What should be\s*', '', clean_q, flags=re.IGNORECASE)
            clean_q = re.sub(r'^How to\s*', '', clean_q, flags=re.IGNORECASE)
            clean_q = re.sub(r'^Which is the\s*', '', clean_q, flags=re.IGNORECASE)
            clean_q = re.sub(r'^Which are the\s*', '', clean_q, flags=re.IGNORECASE)

            # Capitalize first letter
            clean_q = clean_q.strip()
            if clean_q:
                clean_q = clean_q[0].upper() + clean_q[1:]

            answer += f"**{i}. {clean_q}**\n{a}\n\n"

    return jsonify({
        "answer": answer,
        "context_used": len(relevant)
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/stats", methods=["GET"])
def stats():
    try:
        info = client.get_collection(COLLECTION)
        return jsonify({
            "points_count": info.points_count,
            "status": info.status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=False, use_reloader=False, threaded=True)

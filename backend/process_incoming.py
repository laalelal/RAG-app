import os
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from load_chunks import load_chunks   # file you created in step 2

# ---------------- CONFIG ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- UTILS ----------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_context(question, top_k=3):
    chunks = load_chunks()
    q_embedding = embedding_model.encode(question)

    scored = []
    for c in chunks:
        score = cosine_similarity(q_embedding, c["embedding"])
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]

# ---------------- MAIN RAG FUNCTION ----------------
def get_answer(question):
    if not GROQ_API_KEY:
        return " GROQ_API_KEY is not set"

    # 🔍 Retrieve relevant video chunks
    contexts = retrieve_context(question)

    if not contexts:
        return " Answer not found in provided videos."

    #  Build context text with timestamps
    context_text = "\n\n".join(
        [f"[{c['start']}s - {c['end']}s] {c['text']}" for c in contexts]
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a video-based teaching assistant. "
                    "Answer ONLY from the provided context. "
                    "If the answer is not present, say 'Not covered in the video.' "
                    "Always include timestamp."
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{context_text}

Question:
{question}

Answer with exact timestamp.
"""
            }
        ],
        "temperature": 0.2
    }

    res = requests.post(GROQ_URL, headers=headers, json=payload)

    if res.status_code != 200:
        return f"Groq API Error {res.status_code}: {res.text}"

    return res.json()["choices"][0]["message"]["content"]

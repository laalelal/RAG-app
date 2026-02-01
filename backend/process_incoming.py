import json
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ABSOLUTE SAFE PATH (works on Render + local)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "jsons")

def load_all_chunks():
    chunks = []

    if not os.path.exists(JSON_DIR):
        return []

    for file in os.listdir(JSON_DIR):
        if file.endswith(".json"):
            with open(os.path.join(JSON_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                # Your JSON structure has "chunks"
                if "chunks" in data:
                    chunks.extend(data["chunks"])

    return chunks


def simple_retrieval(question, top_k=5):
    chunks = load_all_chunks()
    if not chunks:
        return []

    q = question.lower()
    scored = []

    for c in chunks:
        text = c.get("text", "").lower()
        score = sum(1 for w in q.split() if w in text)
        if score > 0:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def get_answer(question):
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not set"

    contexts = simple_retrieval(question)

    if not contexts:
        return "❌ Not covered in the video."

    context_text = "\n".join(
        [f"[{c['start']}s - {c['end']}s] {c['text']}" for c in contexts]
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a video-based teaching assistant. "
                    "Answer ONLY from the given context. "
                    "Always include timestamps."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion:\n{question}"
            }
        ],
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post(GROQ_URL, headers=headers, json=payload)

    if res.status_code != 200:
        return f"Groq API Error {res.status_code}: {res.text}"

    return res.json()["choices"][0]["message"]["content"]

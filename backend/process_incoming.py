import json
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

JSON_DIR = "jsons"   # folder with your transcript jsons

def load_all_chunks():
    chunks = []
    for file in os.listdir(JSON_DIR):
        if file.endswith(".json"):
            with open(os.path.join(JSON_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                chunks.extend(data)
    return chunks

def simple_retrieval(question, top_k=5):
    chunks = load_all_chunks()
    question_lower = question.lower()

    scored = []
    for c in chunks:
        text = c["text"].lower()
        score = sum(1 for word in question_lower.split() if word in text)
        if score > 0:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]

def get_answer(question):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not set"

    contexts = simple_retrieval(question)

    if not contexts:
        return " Not found in video content."

    context_text = "\n\n".join(
        [f"[{c['start']}s - {c['end']}s] {c['text']}" for c in contexts]
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a video-based teaching assistant. "
                    "Answer ONLY from the provided context. "
                    "If not found, say 'Not covered in the video'. "
                    "Always mention timestamp."
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{context_text}

Question:
{question}
"""
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


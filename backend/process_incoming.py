import json
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

BASE_DIR = os.path.dirname(__file__)
JSON_DIR = os.path.join(BASE_DIR, "jsons")

def load_all_chunks():
    chunks = []
    for file in os.listdir(JSON_DIR):
        if file.endswith(".json"):
            with open(os.path.join(JSON_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    chunks.append({
                        "text": item["text"],
                        "start": item["start"],
                        "end": item["end"],
                        "source": file.replace(".mp3.json", "")
                    })
    return chunks


def retrieve_chunks(question, top_k=5):
    question_words = set(question.lower().split())
    chunks = load_all_chunks()

    scored = []
    for c in chunks:
        text_words = set(c["text"].lower().split())
        score = len(question_words & text_words)
        if score > 0:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def get_answer(question):
    if not GROQ_API_KEY:
        return " GROQ_API_KEY not set"

    matches = retrieve_chunks(question)

    if not matches:
        return " This topic is not covered in the uploaded videos."

    context = "\n".join(
        f"[{m['source']} | {m['start']}s–{m['end']}s] {m['text']}"
        for m in matches
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a video-based tutor. "
                    "Answer ONLY from the provided transcript context. "
                    "Always include timestamps and video name."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ],
        "temperature": 0.2,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post(GROQ_URL, headers=headers, json=payload)

    if res.status_code != 200:
        return f"Groq API Error {res.status_code}: {res.text}"

    return res.json()["choices"][0]["message"]["content"]

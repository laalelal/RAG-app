import json
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "jsons")


def sec_to_mmss(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def load_all_chunks():
    chunks = []

    for file in os.listdir(JSON_DIR):
        if file.endswith(".json"):
            video_name = file.replace(".mp3.json", "").replace("_", " ")

            with open(os.path.join(JSON_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                if "chunks" in data:
                    for c in data["chunks"]:
                        c["video"] = video_name   #  attach video name
                        chunks.append(c)

    return chunks


def simple_retrieval(question, top_k=5):
    chunks = load_all_chunks()
    q = question.lower()

    scored = []
    for c in chunks:
        score = sum(1 for w in q.split() if w in c["text"].lower())
        if score > 0:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def get_answer(question):
    if not GROQ_API_KEY:
        return " GROQ_API_KEY not set"

    contexts = simple_retrieval(question)

    if not contexts:
        return " Not covered in the video content."

    formatted_context = []
    for c in contexts:
        start = sec_to_mmss(c["start"])
        end = sec_to_mmss(c["end"])
        formatted_context.append(
            f"Video: {c['video']} | Time: {start}–{end}\n{c['text']}"
        )

    context_text = "\n\n".join(formatted_context)

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a video-based teaching assistant. "
                    "Answer ONLY from the given context. "
                    "Always include video name and timestamps. "
                    "If not found, say: Not covered in the video."
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

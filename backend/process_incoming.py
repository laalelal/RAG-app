import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_answer(question):
    if not GROQ_API_KEY:
        return " GROQ_API_KEY is not set"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }

    res = requests.post(GROQ_URL, headers=headers, json=payload)

    if res.status_code != 200:
        return f"Groq API Error {res.status_code}: {res.text}"

    return res.json()["choices"][0]["message"]["content"]

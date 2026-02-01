import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

CHUNKS = []

def load_chunks():
    global CHUNKS
    if CHUNKS:
        return CHUNKS

    for file in os.listdir("jsons"):
        if file.endswith(".json"):
            with open(os.path.join("jsons", file), "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    embedding = model.encode(item["text"])
                    CHUNKS.append({
                        "text": item["text"],
                        "start": item["start"],
                        "end": item["end"],
                        "embedding": embedding
                    })
    return CHUNKS

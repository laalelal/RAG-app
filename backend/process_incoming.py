import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import requests

# ---------- helpers ----------
def seconds_to_mmss(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


def create_embedding(text_list):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3", "input": text_list}
    )
    return r.json()["embeddings"]


def inference(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )
    return r.json()["response"]


# ---------- load data (loaded ONCE) ----------
df = joblib.load("embeddings.joblib")


# ---------- MAIN FUNCTION FOR BACKEND ----------
def get_answer(incoming_query):

    question_embedding = create_embedding([incoming_query])[0]

    similarities = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding]
    ).flatten()

    top_results = 5
    max_indx = similarities.argsort()[::-1][:top_results]
    new_df = df.loc[max_indx]

    prompt = f"""
You are an instructor for a Data Structure and Algorithm course.

-------------------- COURSE CONTENT --------------------
{new_df[["title","number","start","end","text"]].to_json(orient="records")}
--------------------------------------------------------

User question:
"{incoming_query}"

FORMAT YOUR ANSWER LIKE THIS (EXACTLY):
"The topic is explained in Video <number> (<title>) starting at <start_time> seconds."
"""

    _ = inference(prompt)  # optional LLM grounding

    best_row = new_df.iloc[0]
    start_time_mmss = seconds_to_mmss(best_row["start"])

    final_answer = (
        f"The topic is explained in Video {best_row['number']} "
        f"({best_row['title']}) starting at {start_time_mmss}."
    )

    return final_answer

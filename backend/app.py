

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.process_incoming import get_answer



app = Flask(__name__)
CORS(app)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"answer": "⚠️ Please ask a valid question."})

    try:
        answer = get_answer(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f" Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from process_incoming import get_answer

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
        return jsonify({"answer": f"Error: {str(e)}"})

#  THIS PART IS VERY IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render gives PORT
    app.run(host="0.0.0.0", port=port)

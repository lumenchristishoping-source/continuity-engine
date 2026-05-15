from flask import Flask, request, jsonify, render_template
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import save_message, load_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary
from ai import call_ai

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    current_topics = detect_topics(user_input)
    current_emotion = detect_emotion(user_input)

    save_message("user", user_input)

    context = get_context(
        current_topics=current_topics,
        current_emotion=current_emotion,
        raw_input=user_input
    )

    memory = load_memory()
    summary = generate_summary(memory)

    context_items = []
    for msg in context:
        context_items.append({
            "role": msg["role"],
            "importance": msg.get("importance", 1),
            "emotion": msg.get("emotion", "neutral"),
            "topics": msg.get("topics", []),
            "timestamp": msg.get("timestamp", ""),
            "content": msg["content"]
        })

    try:
        ai_response = call_ai(user_input, context, summary)
    except Exception as e:
        ai_response = f"[AI error: {e}]"

    save_message("assistant", ai_response)

    summary_lines = [
        line.strip().lstrip("•").strip()
        for line in summary.split("\n")
        if line.strip()
    ]

    return jsonify({
        "response": ai_response,
        "context": context_items,
        "summary": summary_lines,
        "emotion": current_emotion,
        "topics": current_topics
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

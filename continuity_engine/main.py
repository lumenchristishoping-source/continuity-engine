from memory import save_message, load_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary
from ai import call_ai


def display_context(context):
    print("\n┌─ RETRIEVED CONTEXT " + "─" * 40)
    if not context:
        print("│  (no relevant context yet)")
    for msg in context:
        role      = msg["role"].upper()
        importance = msg.get("importance", 1)
        topics    = ", ".join(msg.get("topics", [])) or "—"
        emotion   = msg.get("emotion", "neutral")
        timestamp = msg.get("timestamp", "unknown")
        content   = msg["content"]
        print(f"│  [{role}] importance:{importance} | emotion:{emotion} | topics:{topics}")
        print(f"│  {timestamp}")
        print(f"│  \"{content}\"")
        print("│")
    print("└" + "─" * 60)


def display_summary():
    memory = load_memory()
    summary = generate_summary(memory)
    print("\n┌─ CONTINUITY SUMMARY " + "─" * 39)
    print(summary)
    print("└" + "─" * 60)


def build_prompt(context, user_input):
    lines = []
    for msg in context:
        importance = msg.get("importance", 1)
        topics     = ", ".join(msg.get("topics", [])) or "none"
        emotion    = msg.get("emotion", "neutral")
        timestamp  = msg.get("timestamp", "")
        lines.append(
            f"{msg['role']} [importance:{importance} | emotion:{emotion} | topics:{topics} | {timestamp}]: {msg['content']}"
        )

    context_str = "\n".join(lines)

    return f"""You are a continuity-based AI with persistent temporal memory.

Each message carries: importance (1-10), detected emotion, topics, and a timestamp.
Prioritize high-importance and emotionally relevant memories in your response.

--- MEMORY CONTEXT ---
{context_str}
----------------------

User just said: {user_input}

Respond naturally while considering the full temporal context above.
"""


while True:
    user_input = input("\nYou: ").strip()
    if not user_input:
        continue

    current_topics  = detect_topics(user_input)
    current_emotion = detect_emotion(user_input)

    save_message("user", user_input)

    context = get_context(current_topics=current_topics, current_emotion=current_emotion, raw_input=user_input)

    display_context(context)

    memory = load_memory()
    summary = generate_summary(memory)

    try:
        ai_response = call_ai(user_input, context, summary)
    except Exception as e:
        ai_response = f"[AI error: {e}]"

    save_message("assistant", ai_response)

    print(f"\nAI: {ai_response}")

    display_summary()

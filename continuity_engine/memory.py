import json
import os
from datetime import datetime
from importance import calculate_importance
from topics import detect_topics
from emotions import detect_emotion

FILE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")


def load_memory():
    if not os.path.exists(FILE_NAME):
        return []

    with open(FILE_NAME, "r") as f:
        return json.load(f)


def save_memory(memory):
    with open(FILE_NAME, "w") as f:
        json.dump(memory, f, indent=2)


def save_message(role, content):
    memory = load_memory()

    importance = calculate_importance(content, memory_history=memory)
    topics = detect_topics(content)
    emotion = detect_emotion(content)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    memory.append({
        "role": role,
        "content": content,
        "importance": importance,
        "topics": topics,
        "emotion": emotion,
        "timestamp": timestamp
    })

    save_memory(memory)

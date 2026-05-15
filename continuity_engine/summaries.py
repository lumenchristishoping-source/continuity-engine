from patterns import analyze_patterns


def generate_summary(memory):
    if not memory:
        return "No conversation history yet."

    patterns = analyze_patterns(memory)
    topic_counts = patterns["topic_counts"]
    recurring_topics = patterns["recurring_topics"]
    emotional_spikes = patterns["emotional_spikes"]
    dominant_emotion = patterns["dominant_emotion"]

    parts = []

    if recurring_topics:
        parts.append(f"Recurring topics: {', '.join(recurring_topics)}")

    if emotional_spikes:
        spikes = [f"{emotion} around {topic}" for topic, emotion in emotional_spikes.items()]
        parts.append(f"Emotional patterns: {', '.join(spikes)}")

    if dominant_emotion:
        parts.append(f"Overall emotional tone: {dominant_emotion}")

    if topic_counts:
        top = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_names = [f"{t} ({c}x)" for t, c in top]
        parts.append(f"Most discussed: {', '.join(top_names)}")

    if not parts:
        return "Not enough data to generate a summary yet."

    return "\n".join(f"  • {p}" for p in parts)

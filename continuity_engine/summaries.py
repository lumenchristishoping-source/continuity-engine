from patterns import analyze_patterns
from behaviour import analyze_behaviour


def generate_summary(memory):
    if not memory:
        return "No conversation history yet."

    patterns         = analyze_patterns(memory)
    topic_counts     = patterns["topic_counts"]
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
        top      = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_names = [f"{t} ({c}x)" for t, c in top]
        parts.append(f"Most discussed: {', '.join(top_names)}")

    # ── Behaviour insights (non-critical — skip silently on error) ───────────
    try:
        beh = analyze_behaviour(memory)

        if beh["breakthrough_count"] >= 2:
            parts.append(
                f"Breakthrough pattern: {beh['breakthrough_count']}x "
                f"negative → positive emotional shift detected"
            )

        if beh["peak_time"]:
            parts.append(f"Peak engagement: {beh['peak_time']} (highest avg importance)")

        if beh["strong_associations"]:
            assoc = [
                f"{topic} → {emo}"
                for topic, emo in list(beh["strong_associations"].items())[:2]
            ]
            parts.append(f"Strong associations: {', '.join(assoc)}")

        if beh["behaviour_shift"]:
            s = beh["behaviour_shift"]
            parts.append(f"Emotional shift detected: {s['from']} → {s['to']} over time")

        if beh["unresolved_threads"]:
            parts.append(
                f"Unresolved threads: {', '.join(beh['unresolved_threads'][:3])}"
            )

        if beh["recurrence_streaks"]:
            parts.append(
                f"Deep focus topics: {', '.join(beh['recurrence_streaks'])}"
            )

    except Exception:
        pass

    if not parts:
        return "Not enough data to generate a summary yet."

    return "\n".join(f"  • {p}" for p in parts)

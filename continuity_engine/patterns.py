def analyze_patterns(memory):
    topic_counts = {}
    emotion_topic_map = {}
    emotion_counts = {}

    for msg in memory:
        topics = msg.get("topics", [])
        emotion = msg.get("emotion", "neutral")

        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

            if topic not in emotion_topic_map:
                emotion_topic_map[topic] = []
            if emotion != "neutral":
                emotion_topic_map[topic].append(emotion)

        if emotion != "neutral":
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    recurring_topics = [t for t, count in topic_counts.items() if count >= 3]

    emotional_spikes = {}
    for topic, emotions in emotion_topic_map.items():
        if emotions:
            most_common = max(set(emotions), key=emotions.count)
            emotional_spikes[topic] = most_common

    dominant_emotion = None
    if emotion_counts:
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)

    return {
        "topic_counts": topic_counts,
        "recurring_topics": recurring_topics,
        "emotional_spikes": emotional_spikes,
        "emotion_counts": emotion_counts,
        "dominant_emotion": dominant_emotion,
    }

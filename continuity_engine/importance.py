def calculate_importance(message, memory_history=None):
    score = 1
    message_lower = message.lower()
    words = message_lower.split()

    # --- 1. Emotional intensity ---
    high_emotion = [
        "devastated", "terrified", "furious", "ecstatic", "heartbroken",
        "overwhelmed", "desperate", "hopeless", "euphoric", "panic"
    ]
    medium_emotion = [
        "anxious", "scared", "excited", "frustrated", "worried", "stressed",
        "proud", "sad", "angry", "nervous", "happy", "lonely", "stuck"
    ]
    light_emotion = [
        "feel", "feeling", "felt", "upset", "glad", "fine", "okay", "meh"
    ]

    if any(w in message_lower for w in high_emotion):
        score += 3
    elif any(w in message_lower for w in medium_emotion):
        score += 2
    elif any(w in message_lower for w in light_emotion):
        score += 1

    # --- 2. User emphasis phrases ---
    emphasis_phrases = [
        "this matters to me", "i really care", "i care about this",
        "i can't stop thinking", "i cannot stop thinking",
        "this is important", "really important", "deeply",
        "means a lot", "i need this", "i have to", "i must"
    ]
    if any(phrase in message_lower for phrase in emphasis_phrases):
        score += 2

    # --- 3. Identity relevance ---
    identity_words = [
        "goal", "dream", "purpose", "ambition", "vision", "mission",
        "fear", "value", "belief", "who i am", "my life", "my future",
        "i want to become", "i want to be", "i struggle", "i always",
        "career", "calling", "passion"
    ]
    identity_hits = sum(1 for w in identity_words if w in message_lower)
    if identity_hits >= 3:
        score += 2
    elif identity_hits >= 1:
        score += 1

    # --- 4. Narrative depth ---
    word_count = len(words)
    personal_markers = ["i ", "my ", "me ", "i've", "i'm", "i'd", "i'll", "myself"]
    personal_count = sum(1 for m in personal_markers if m in message_lower)

    if word_count >= 30 and personal_count >= 3:
        score += 2
    elif word_count >= 15 and personal_count >= 2:
        score += 1

    # --- 5. Low-effort penalty ---
    casual_words = ["ok", "okay", "lol", "lmao", "haha", "nice", "cool",
                    "yeah", "yep", "nope", "sure", "thx", "thanks", "bye"]
    if word_count <= 4 and any(w in words for w in casual_words):
        return 1

    # --- 6. Topic recurrence bonus ---
    if memory_history:
        from topics import detect_topics
        current_topics = set(detect_topics(message))
        if current_topics:
            topic_counts = {}
            for past_msg in memory_history:
                for t in past_msg.get("topics", []):
                    topic_counts[t] = topic_counts.get(t, 0) + 1
            max_recurrence = max(
                (topic_counts.get(t, 0) for t in current_topics), default=0
            )
            if max_recurrence >= 5:
                score += 2
            elif max_recurrence >= 3:
                score += 1

    if score < 1:
        score = 1
    if score > 10:
        score = 10

    return score

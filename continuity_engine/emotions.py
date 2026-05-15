def detect_emotion(message):
    message_lower = message.lower()

    emotion_keywords = {
        "stress": [
            "stressed", "stress", "overwhelmed", "pressure", "burned out",
            "too much", "can't handle", "cannot handle", "exhausted", "drained",
            "don't know if", "not sure if", "is it even worth", "worth it anymore",
            "giving up", "idk man", "i don't know man", "so tired", "no energy"
        ],
        "excitement": [
            "excited", "amazing", "can't wait", "thrilled", "pumped",
            "stoked", "love this", "this is great", "so good", "incredible",
            "figured out", "i figured", "just cracked", "breakthrough", "it works",
            "finally", "eureka", "got it", "nailed it", "this is it",
            "core feature", "it clicked", "makes sense now", "i think i found"
        ],
        "sadness": [
            "sad", "depressed", "unhappy", "disappointed", "down",
            "crying", "heartbroken", "hopeless", "defeated", "empty",
            "nobody cares", "what's the point", "doesn't matter"
        ],
        "fear": [
            "scared", "afraid", "terrified", "fear", "worried",
            "nervous", "panic", "anxious", "dread", "uncertain",
            "what if it fails", "what if nobody", "what if i can't"
        ],
        "motivation": [
            "motivated", "inspired", "ready", "determined", "focused",
            "let's go", "i will", "i'm going to", "i can do", "committed",
            "i want to build", "i'm building", "i want to create", "let's do this",
            "starting", "i decided", "going for it"
        ],
        "frustration": [
            "frustrated", "annoyed", "angry", "fed up", "ugh",
            "hate this", "stuck again", "not working", "so annoying", "impossible",
            "why won't it", "keeps breaking", "doesn't work", "still broken",
            "i give up", "this is stupid"
        ],
        "doubt": [
            "idk", "idk man", "not sure", "maybe", "i don't know",
            "is it worth", "worth building", "should i even", "does it matter",
            "who would use this", "is anyone going to", "what's the point"
        ],
        "pride": [
            "proud", "i did it", "i built", "i made", "look at this",
            "it's working", "shipped", "launched", "i finished", "completed",
            "i actually did", "can you believe i"
        ],
        "curiosity": [
            "what if", "i wonder", "how does", "why does", "could we",
            "what would happen", "i've been thinking", "interesting idea",
            "what do you think about", "is it possible"
        ]
    }

    # Multi-word phrase check first (order matters — more specific wins)
    phrase_emotions = {
        "don't know if this is even worth": "doubt",
        "is it even worth building": "doubt",
        "not sure if sarvix": "doubt",
        "i think i just figured": "excitement",
        "just figured out": "excitement",
        "i give up": "frustration",
        "burned out": "stress",
        "idk man": "doubt",
        "what's the point": "doubt",
    }

    for phrase, emotion in phrase_emotions.items():
        if phrase in message_lower:
            return emotion

    # Single keyword fallback
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                return emotion

    return "neutral"


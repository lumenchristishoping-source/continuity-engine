def detect_topics(message):
    message_lower = message.lower()
    topics = []

    topic_keywords = {
        "AI": [
            "ai", "model", "memory", "neural", "machine learning", "gpt", "llm",
            "chatbot", "openrouter", "mistral", "claude", "gemini", "openai",
            "temporal", "context", "continuity", "embedding", "prompt", "inference"
        ],
        "coding": [
            "code", "coding", "programming", "function", "bug", "script",
            "developer", "python", "javascript", "replit", "github", "api",
            "json", "database", "deploy", "error", "debug", "import", "class",
            "module", "library", "pip", "terminal", "shell", "main.py"
        ],
        "project": [
            "build", "project", "app", "startup", "product", "feature",
            "launch", "ship", "sarvix", "continuity engine", "this thing",
            "the app", "what i'm building", "my app", "my startup", "my product"
        ],
        "future": [
            "future", "someday", "one day", "long-term", "vision",
            "eventually", "plan", "where i see", "in 5 years", "goals",
            "what i want to become", "where this is going"
        ],
        "emotions": [
            "feel", "feeling", "happy", "sad", "excited", "proud",
            "hopeful", "lost", "confused", "emotional", "mood"
        ],
        "stress": [
            "stuck", "anxious", "stress", "overwhelmed", "frustrated",
            "scared", "worried", "pressure", "burnout", "burned out",
            "drained", "exhausted", "idk man", "not sure anymore"
        ],
        "launch": [
            "launch", "release", "ship", "deploy", "go live",
            "publish", "announce", "beta", "mvp", "first users"
        ],
        "learning": [
            "learn", "learning", "study", "understand", "research",
            "read", "practice", "improve", "how does", "figured out",
            "just learned", "i now understand"
        ],
        "music": [
            "music", "song", "track", "beat", "lyrics", "suno",
            "deejd", "phonk", "anime", "opening", "release", "freecords",
            "brazilian", "portuguese", "naruto", "aot", "demon slayer"
        ],
        "money": [
            "money", "revenue", "monetize", "paid", "subscription",
            "pricing", "income", "profit", "investor", "funding", "broke"
        ],
        "health": [
            "tired", "sleep", "rest", "sick", "health", "eating",
            "exercise", "doctor", "mental health", "anxiety", "depression"
        ],
        "people": [
            "friend", "family", "someone", "people", "team", "user",
            "they said", "he said", "she said", "my mom", "my dad",
            "relationship", "alone", "lonely"
        ]
    }

    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                topics.append(topic)
                break

    return topics


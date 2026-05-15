from memory import load_memory

MAX_RESULTS = 10

IDENTITY_SIGNALS = [
    "i feel", "i'm", "i am", "i want", "i need", "i think", "i keep",
    "i've", "i have", "i can't", "i cannot", "i don't", "i do",
    "my goal", "my dream", "my project", "my future", "my life",
    "what should i", "help me", "stuck", "struggling", "anxious",
    "motivated", "scared", "worried", "frustrated", "excited",
    "purpose", "career", "ambition", "identity", "who am i"
]


def detect_intent(raw_input):
    lowered = raw_input.lower().strip()
    words = lowered.split()

    for signal in IDENTITY_SIGNALS:
        if signal in lowered:
            return "IDENTITY"

    # First-person pronouns signal self-directed query
    if any(w in ["i", "me", "my", "myself"] for w in words):
        return "IDENTITY"

    return "SESSION"


def _score(msg, index, total, current_topic_set, raw_lower, last_two_keys):
    score = 0

    content_lower = msg["content"].lower()
    importance = msg.get("importance", 1)
    msg_topics = set(msg.get("topics", []))
    key = (msg["role"], msg["content"])

    # Exact text match → +40
    if raw_lower and raw_lower in content_lower:
        score += 40

    # Topic overlap → +0 to +25
    if current_topic_set:
        overlap = len(current_topic_set & msg_topics)
        max_possible = len(current_topic_set)
        score += round((overlap / max_possible) * 25)

    # Importance (1–10) × 3 → +3 to +30
    score += importance * 3

    # Recency → +0 to +15 (newest = 15)
    if total > 1:
        score += round((index / (total - 1)) * 15)
    else:
        score += 15

    # Last 2 messages continuity boost → +10
    if key in last_two_keys:
        score += 10

    return score


def _dedupe_and_trim(scored, limit):
    seen = set()
    result = []
    for entry in scored:
        key = (entry[2]["role"], entry[2]["content"])
        if key not in seen:
            seen.add(key)
            result.append(entry)
        if len(result) >= limit:
            break
    return result


def _ensure_mandatory(top, deduped, raw_lower, last_two_keys):
    top_keys = {(m["role"], m["content"]) for _, _, m in top}

    # Guarantee at least 1 exact match
    if raw_lower:
        has_exact = any(raw_lower in m["content"].lower() for _, _, m in top)
        if not has_exact:
            for s, i, msg in deduped:
                if raw_lower in msg["content"].lower():
                    if len(top) >= MAX_RESULTS:
                        top[-1] = (s, i, msg)
                    else:
                        top.append((s, i, msg))
                    top_keys.add((msg["role"], msg["content"]))
                    break

    # Guarantee last 2 messages
    for s, i, msg in deduped:
        key = (msg["role"], msg["content"])
        if key in last_two_keys and key not in top_keys:
            if len(top) >= MAX_RESULTS:
                top[-1] = (s, i, msg)
            else:
                top.append((s, i, msg))
            top_keys.add(key)

    return top


def get_context(current_topics=None, current_emotion=None, raw_input=""):
    memory = load_memory()

    if not memory:
        return []

    current_topic_set = set(current_topics) if current_topics else set()
    raw_lower = raw_input.lower().strip()
    total = len(memory)
    last_two_keys = {(m["role"], m["content"]) for m in memory[-2:]}

    intent = detect_intent(raw_input)

    scored = []
    for i, msg in enumerate(memory):
        msg_topics = set(msg.get("topics", []))
        has_exact = raw_lower and raw_lower in msg["content"].lower()
        has_topic = bool(current_topic_set & msg_topics)
        key = (msg["role"], msg["content"])
        is_last_two = key in last_two_keys

        if intent == "SESSION":
            # Hard filter: only exact matches, topic overlaps, or last 2
            if not (has_exact or has_topic or is_last_two):
                continue

        s = _score(msg, i, total, current_topic_set, raw_lower, last_two_keys)
        scored.append((s, i, msg))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    deduped = _dedupe_and_trim(scored, MAX_RESULTS * 2)
    top = deduped[:MAX_RESULTS]
    top = _ensure_mandatory(top, deduped, raw_lower, last_two_keys)
    top.sort(key=lambda x: (x[0], x[1]), reverse=True)

    return [msg for _, _, msg in top[:MAX_RESULTS]]

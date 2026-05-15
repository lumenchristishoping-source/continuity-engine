from memory import load_memory

# Always include this many most-recent messages no matter what
RECENT_WINDOW = 15
# Additional older messages pulled by relevance scoring
EXTRA_SCORED  = 8


def _score(msg, index, total, current_topic_set, raw_lower):
    score = 0
    content_lower = msg["content"].lower()
    importance    = msg.get("importance", 1)
    msg_topics    = set(msg.get("topics", []))

    # Exact substring match in message content → big boost
    if raw_lower and raw_lower in content_lower:
        score += 40

    # Topic overlap
    if current_topic_set:
        overlap = len(current_topic_set & msg_topics)
        score  += round((overlap / len(current_topic_set)) * 25)

    # Importance × 3
    score += importance * 3

    # Recency within the older pool (0–10)
    if total > 1:
        score += round((index / (total - 1)) * 10)
    else:
        score += 10

    return score


def get_context(current_topics=None, current_emotion=None, raw_input=""):
    memory = load_memory()
    if not memory:
        return []

    current_topic_set = set(current_topics) if current_topics else set()
    raw_lower         = raw_input.lower().strip()
    total             = len(memory)

    # ── 1. Always include the most recent messages ──────────────────────────
    recent_cutoff = max(0, total - RECENT_WINDOW)
    recent_msgs   = memory[recent_cutoff:]          # chronological order
    recent_keys   = {(m["role"], m["content"]) for m in recent_msgs}

    # ── 2. Score older messages for relevance ───────────────────────────────
    older_msgs = memory[:recent_cutoff]
    scored     = []
    for i, msg in enumerate(older_msgs):
        s = _score(msg, i, len(older_msgs), current_topic_set, raw_lower)
        if s > 0:                                   # skip irrelevant old msgs
            scored.append((s, i, msg))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # Deduplicate and pick top extras
    extras = []
    seen   = set(recent_keys)
    for _, _, msg in scored:
        key = (msg["role"], msg["content"])
        if key not in seen:
            seen.add(key)
            extras.append(msg)
        if len(extras) >= EXTRA_SCORED:
            break

    # ── 3. Merge and sort chronologically so the AI reads them in order ─────
    # Assign original index for sorting
    index_map = {id(m): i for i, m in enumerate(memory)}

    combined = extras + recent_msgs
    combined.sort(key=lambda m: index_map.get(id(m), 0))

    return combined

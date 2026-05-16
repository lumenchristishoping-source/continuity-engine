# COGEN — Install Persistent Emotional Memory Into Any AI Project

## What Cogen Is

Cogen is a persistent emotional memory layer for AI — it tracks every message with timestamps, emotion tags (stress, excitement, doubt, motivation, frustration, pride, curiosity, sadness, fear), importance scores (1–10), belief scores (0.0–1.0), conflict flags, and topic tags (AI, coding, project, future, stress, launch, learning, music, money, health, people), storing everything in a local SQLite database that survives across sessions, model switches, browser tabs, and restarts. Before every AI call, Cogen retrieves the most relevant past messages using a hybrid scorer (exact match, topic overlap, TF-IDF cosine similarity, importance, recency) and injects them into the system prompt so the model responds with genuine continuity — not simulated memory, but real recall of what this person actually said.

---

## AGENT INSTRUCTION: Auto-Install Cogen

When a developer says **"install cogen memory"** — create every file below exactly as written, then run the verification test. No other steps are needed.

---

## Dependencies

```bash
pip install requests
```

Only `requests` and `sqlite3` (stdlib) are required. Nothing else.

---

## Files to Create

Create all files in the same directory (e.g. `cogen/` or your project root).

---

### `emotions.py`

```python
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

    phrase_emotions = {
        "don't know if this is even worth": "doubt",
        "is it even worth building": "doubt",
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

    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                return emotion

    return "neutral"
```

---

### `topics.py`

```python
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
            "launch", "ship", "continuity engine", "this thing",
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
            "music", "song", "track", "beat", "lyrics",
            "phonk", "anime", "opening", "release"
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
```

---

### `importance.py`

```python
def calculate_importance(message, memory_history=None):
    score = 1
    message_lower = message.lower()
    words = message_lower.split()

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

    emphasis_phrases = [
        "this matters to me", "i really care", "i care about this",
        "i can't stop thinking", "i cannot stop thinking",
        "this is important", "really important", "deeply",
        "means a lot", "i need this", "i have to", "i must"
    ]
    if any(phrase in message_lower for phrase in emphasis_phrases):
        score += 2

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

    word_count = len(words)
    personal_markers = ["i ", "my ", "me ", "i've", "i'm", "i'd", "i'll", "myself"]
    personal_count = sum(1 for m in personal_markers if m in message_lower)

    if word_count >= 30 and personal_count >= 3:
        score += 2
    elif word_count >= 15 and personal_count >= 2:
        score += 1

    casual_words = ["ok", "okay", "lol", "lmao", "haha", "nice", "cool",
                    "yeah", "yep", "nope", "sure", "thx", "thanks", "bye"]
    if word_count <= 4 and any(w in words for w in casual_words):
        return 1

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

    return max(1, min(10, score))
```

---

### `conflict.py`

```python
def detect_conflict(new_content, memory):
    """
    Checks if new_content contradicts existing memory.
    Returns (is_conflict: bool, conflicting_entry: dict | None)
    """
    new_lower = new_content.lower()

    opposites = [
        (["i like", "i love", "i enjoy"], ["i hate", "i don't like", "i dislike"]),
        (["i am a boy", "i'm a boy", "i am male"], ["i am a girl", "i'm a girl", "i am female"]),
        (["i eat meat", "i like meat", "i like chicken"], ["i am vegan", "i am vegetarian", "i don't eat meat"]),
        (["i love pizza", "i like pizza", "i enjoy pizza"], ["i hate pizza", "i don't like pizza"]),
        (["i am happy", "feeling good", "feeling great"], ["i am sad", "feeling down", "feeling bad"]),
    ]

    for positive_phrases, negative_phrases in opposites:
        new_is_positive = any(p in new_lower for p in positive_phrases)
        new_is_negative = any(p in new_lower for p in negative_phrases)

        if new_is_positive or new_is_negative:
            for past_msg in reversed(memory):
                past_lower = past_msg.get("content", "").lower()
                if new_is_positive and any(p in past_lower for p in negative_phrases):
                    return True, past_msg
                if new_is_negative and any(p in past_lower for p in positive_phrases):
                    return True, past_msg

    return False, None
```

---

### `belief.py`

```python
def calculate_belief_score(new_content, memory):
    """
    Returns a belief score 0.0–1.0.
    Starts at 1.0, drops to 0.3 on contradiction, boosted by past confirmations.
    """
    from conflict import detect_conflict

    new_lower = new_content.lower()
    score = 1.0

    is_conflict, _ = detect_conflict(new_content, memory)
    if is_conflict:
        score = 0.3

    confirmation_phrases = [
        "i like", "i love", "i enjoy", "i hate", "i dislike",
        "i am", "i'm", "i prefer", "i always", "i never"
    ]

    for phrase in confirmation_phrases:
        if phrase in new_lower:
            confirmations = sum(
                1 for msg in memory
                if phrase in msg.get("content", "").lower()
                and msg.get("belief_score", 1.0) >= 0.7
            )
            boost = min(confirmations * 0.1, 0.4)
            if not is_conflict:
                score = min(1.0, score + boost)
            break

    return round(score, 2)
```

---

### `memory.py`

```python
import sqlite3
import json
import os
from datetime import datetime
from importance import calculate_importance
from topics import detect_topics
from emotions import detect_emotion

DB_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db")
LEGACY_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def _init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                role         TEXT    NOT NULL,
                content      TEXT    NOT NULL,
                importance   INTEGER DEFAULT 1,
                emotion      TEXT    DEFAULT 'neutral',
                topics       TEXT    DEFAULT '[]',
                timestamp    TEXT    NOT NULL,
                conflict     INTEGER DEFAULT 0,
                belief_score REAL    DEFAULT 1.0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts         ON messages(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON messages(importance)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role       ON messages(role)")
        conn.commit()


def _migrate_json():
    if not os.path.exists(LEGACY_JSON):
        return
    try:
        with open(LEGACY_JSON, "r") as f:
            data = json.load(f)
        if not data:
            return
        with _get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            if count > 0:
                return
            for msg in data:
                conn.execute(
                    """INSERT INTO messages
                       (role, content, importance, emotion, topics, timestamp, conflict, belief_score)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        msg["role"],
                        msg["content"],
                        msg.get("importance", 1),
                        msg.get("emotion", "neutral"),
                        json.dumps(msg.get("topics", [])),
                        msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        msg.get("conflict", 0),
                        msg.get("belief_score", 1.0),
                    ),
                )
            conn.commit()
        os.rename(LEGACY_JSON, LEGACY_JSON + ".migrated")
    except Exception as e:
        print(f"[memory] JSON migration skipped: {e}")


_init_db()
_migrate_json()


def _row_to_dict(row):
    d = dict(row)
    d["topics"] = json.loads(d.get("topics") or "[]")
    return d


def load_memory():
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM messages ORDER BY id ASC").fetchall()
    return [_row_to_dict(r) for r in rows]


def save_message(role, content):
    from conflict import detect_conflict
    from belief import calculate_belief_score

    memory       = load_memory()
    importance   = calculate_importance(content, memory_history=memory)
    topics       = detect_topics(content)
    emotion      = detect_emotion(content)
    timestamp    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_conflict, _ = detect_conflict(content, memory)
    belief_score = calculate_belief_score(content, memory)

    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO messages
               (role, content, importance, emotion, topics, timestamp, conflict, belief_score)
               VALUES (?,?,?,?,?,?,?,?)""",
            (role, content, importance, emotion,
             json.dumps(topics), timestamp, int(is_conflict), belief_score),
        )
        conn.commit()


def clear_memory():
    with _get_conn() as conn:
        conn.execute("DELETE FROM messages")
        conn.commit()
```

---

### `patterns.py`

```python
def analyze_patterns(memory):
    topic_counts      = {}
    emotion_topic_map = {}
    emotion_counts    = {}

    for msg in memory:
        topics  = msg.get("topics", [])
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
        "topic_counts":      topic_counts,
        "recurring_topics":  recurring_topics,
        "emotional_spikes":  emotional_spikes,
        "emotion_counts":    emotion_counts,
        "dominant_emotion":  dominant_emotion,
    }
```

---

### `behaviour.py`

```python
from collections import defaultdict
from datetime import datetime

NEGATIVE_EMOTIONS = {"doubt", "stress", "frustration"}
POSITIVE_EMOTIONS = {"excitement", "motivation"}


def _parse_ts(ts_str):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(ts_str, fmt)
        except (ValueError, TypeError):
            pass
    return None


def _time_bucket(hour):
    if 5 <= hour < 12:   return "morning"
    elif 12 <= hour < 17: return "afternoon"
    elif 17 <= hour < 21: return "evening"
    else:                 return "night"


def analyze_behaviour(memory):
    user_msgs = [m for m in memory if m.get("role") == "user"]

    # 1. Breakthrough pattern: negative → positive emotion transitions
    breakthrough_count = 0
    last_was_negative  = False
    for msg in user_msgs:
        emo = msg.get("emotion", "neutral")
        if emo in NEGATIVE_EMOTIONS:
            last_was_negative = True
        elif emo in POSITIVE_EMOTIONS and last_was_negative:
            breakthrough_count += 1
            last_was_negative = False

    # 2. Peak time of day
    bucket_importance = defaultdict(list)
    for msg in memory:
        ts = _parse_ts(msg.get("timestamp", ""))
        if ts:
            bucket = _time_bucket(ts.hour)
            bucket_importance[bucket].append(msg.get("importance", 1))

    peak_time = None
    if bucket_importance:
        peak_time = max(
            bucket_importance,
            key=lambda b: sum(bucket_importance[b]) / len(bucket_importance[b])
        )

    # 3. Topic-emotion associations (60%+ same emotion = strong)
    topic_emotions = defaultdict(list)
    for msg in memory:
        emo = msg.get("emotion", "neutral")
        for topic in msg.get("topics", []):
            topic_emotions[topic].append(emo)

    strong_associations = {}
    for topic, emotions in topic_emotions.items():
        if len(emotions) >= 3:
            most_common = max(set(emotions), key=emotions.count)
            if emotions.count(most_common) / len(emotions) >= 0.6:
                strong_associations[topic] = most_common

    # 4. Behavioural shift: dominant emotion changed from first to second half
    behaviour_shift = None
    if len(memory) >= 6:
        mid         = len(memory) // 2
        first_emos  = [m.get("emotion") for m in memory[:mid]  if m.get("emotion") and m.get("emotion") != "neutral"]
        second_emos = [m.get("emotion") for m in memory[mid:]  if m.get("emotion") and m.get("emotion") != "neutral"]
        if first_emos and second_emos:
            dom_first  = max(set(first_emos),  key=first_emos.count)
            dom_second = max(set(second_emos), key=second_emos.count)
            if dom_first != dom_second:
                behaviour_shift = {"from": dom_first, "to": dom_second}

    # 5. Unresolved threads: high-importance topics gone silent in last 10 messages
    recent_cutoff  = max(0, len(memory) - 10)
    recent_topics  = set()
    for msg in memory[recent_cutoff:]:
        recent_topics.update(msg.get("topics", []))

    unresolved_threads = []
    seen_unresolved    = set()
    for msg in memory[:recent_cutoff]:
        if msg.get("importance", 1) >= 7:
            for topic in msg.get("topics", []):
                if topic not in recent_topics and topic not in seen_unresolved:
                    unresolved_threads.append(topic)
                    seen_unresolved.add(topic)

    # 6. Recurrence streaks: topic in 3+ consecutive user messages
    recurrence_streaks = []
    if user_msgs:
        current_topic = None
        streak_count  = 0
        for msg in user_msgs:
            topics = msg.get("topics", [])
            if current_topic and current_topic in topics:
                streak_count += 1
                if streak_count >= 3 and current_topic not in recurrence_streaks:
                    recurrence_streaks.append(current_topic)
            else:
                current_topic = topics[0] if topics else None
                streak_count  = 1

    return {
        "breakthrough_count":  breakthrough_count,
        "peak_time":           peak_time,
        "strong_associations": strong_associations,
        "behaviour_shift":     behaviour_shift,
        "unresolved_threads":  unresolved_threads,
        "recurrence_streaks":  recurrence_streaks,
    }
```

---

### `summaries.py`

```python
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
        top       = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_names = [f"{t} ({c}x)" for t, c in top]
        parts.append(f"Most discussed: {', '.join(top_names)}")

    try:
        beh = analyze_behaviour(memory)

        if beh["breakthrough_count"] >= 2:
            parts.append(f"Breakthrough pattern: {beh['breakthrough_count']}x negative → positive shift")

        if beh["peak_time"]:
            parts.append(f"Peak engagement: {beh['peak_time']}")

        if beh["strong_associations"]:
            assoc = [f"{topic} → {emo}" for topic, emo in list(beh["strong_associations"].items())[:2]]
            parts.append(f"Strong associations: {', '.join(assoc)}")

        if beh["behaviour_shift"]:
            s = beh["behaviour_shift"]
            parts.append(f"Emotional shift: {s['from']} → {s['to']}")

        if beh["unresolved_threads"]:
            parts.append(f"Unresolved threads: {', '.join(beh['unresolved_threads'][:3])}")

        if beh["recurrence_streaks"]:
            parts.append(f"Deep focus topics: {', '.join(beh['recurrence_streaks'])}")

    except Exception:
        pass

    if not parts:
        return "Not enough data to generate a summary yet."

    return "\n".join(f"  • {p}" for p in parts)
```

---

### `retrieval.py`

```python
import math
import re
from collections import Counter
from memory import load_memory

RECENT_WINDOW = 15
EXTRA_SCORED  = 8

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "is", "it", "i", "my", "we", "you", "me", "this", "that", "was",
    "are", "be", "been", "have", "has", "had", "do", "did", "will", "would",
    "can", "could", "with", "about", "just", "so", "if", "what", "how",
    "when", "where", "who", "which", "their", "there", "they", "them", "our",
    "not", "no", "up", "out", "more", "also", "by", "as", "get", "from",
    "said", "say", "told", "tell", "thing", "things", "something", "anything",
}


def _tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _build_corpus_df(messages):
    df = Counter()
    for msg in messages:
        for token in set(_tokenize(msg["content"])):
            df[token] += 1
    return df


def _tfidf_cosine(query_tokens, doc_tokens, corpus_df, total_docs):
    if not query_tokens or not doc_tokens:
        return 0.0

    def vec(tokens):
        tf = Counter(tokens)
        out = {}
        for term, count in tf.items():
            idf = math.log((total_docs + 1) / (corpus_df.get(term, 0) + 1)) + 1.0
            out[term] = (count / len(tokens)) * idf
        return out

    qv = vec(query_tokens)
    dv = vec(doc_tokens)
    common = set(qv) & set(dv)
    if not common:
        return 0.0

    dot   = sum(qv[t] * dv[t] for t in common)
    qnorm = math.sqrt(sum(v * v for v in qv.values()))
    dnorm = math.sqrt(sum(v * v for v in dv.values()))
    return dot / (qnorm * dnorm) if qnorm and dnorm else 0.0


def _score(msg, index, pool_size, current_topic_set, raw_lower,
           query_tokens, corpus_df, total_docs):
    score         = 0
    content_lower = msg["content"].lower()
    importance    = msg.get("importance", 1)
    msg_topics    = set(msg.get("topics", []))

    if raw_lower and raw_lower in content_lower:
        score += 40

    if current_topic_set:
        overlap = len(current_topic_set & msg_topics)
        score  += round((overlap / len(current_topic_set)) * 25)

    doc_tokens = _tokenize(msg["content"])
    tfidf      = _tfidf_cosine(query_tokens, doc_tokens, corpus_df, total_docs)
    score     += round(tfidf * 20)

    belief = msg.get("belief_score", 1.0)
    score += importance * 3 * belief

    if pool_size > 1:
        score += round((index / (pool_size - 1)) * 10)
    else:
        score += 10

    return score


def get_context(current_topics=None, current_emotion=None, raw_input=""):
    memory = load_memory()
    if not memory:
        return []

    current_topic_set = set(current_topics) if current_topics else set()
    raw_lower         = raw_input.lower().strip()
    query_tokens      = _tokenize(raw_input)
    total             = len(memory)
    corpus_df         = _build_corpus_df(memory)

    recent_cutoff = max(0, total - RECENT_WINDOW)
    recent_msgs   = memory[recent_cutoff:]
    recent_keys   = {(m["role"], m["content"]) for m in recent_msgs}

    older_msgs = memory[:recent_cutoff]
    scored     = []
    for i, msg in enumerate(older_msgs):
        s = _score(msg, i, len(older_msgs), current_topic_set,
                   raw_lower, query_tokens, corpus_df, total)
        if s > 0:
            scored.append((s, i, msg))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    extras = []
    seen   = set(recent_keys)
    for _, _, msg in scored:
        key = (msg["role"], msg["content"])
        if key not in seen:
            seen.add(key)
            extras.append(msg)
        if len(extras) >= EXTRA_SCORED:
            break

    index_map = {id(m): i for i, m in enumerate(memory)}
    combined  = extras + recent_msgs
    combined.sort(key=lambda m: index_map.get(id(m), 0))
    return combined
```

---

### `ai.py`

```python
import os
import requests

MODELS = [
    "anthropic/claude-3-haiku-20240307",
    "openai/gpt-4o-mini",
    "mistralai/mistral-small-2603",
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-3-12b-it:free",
    "deepseek/deepseek-r1:free",
]


def call_ai(user_message, retrieved_context, continuity_summary, preferred_model=None):
    base_url = os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key  = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY", "")

    if preferred_model and preferred_model not in MODELS:
        order = [preferred_model] + MODELS
    elif preferred_model:
        order = [preferred_model] + [m for m in MODELS if m != preferred_model]
    else:
        order = MODELS

    if retrieved_context:
        context_lines = "\n".join(
            f"[{msg.get('timestamp', '?')}] {msg['role'].upper()}: {msg['content']}"
            for msg in retrieved_context
        )
        memory_block = (
            "CONVERSATION HISTORY (your actual memory — treat it as real):\n"
            + context_lines
            + "\n\nPATTERN SUMMARY:\n"
            + (continuity_summary.strip() if continuity_summary.strip() else "(patterns still forming)")
        )
    else:
        memory_block = "MEMORY: Empty — this is your very first exchange with this person."

    system_prompt = f"""You are a conversational AI with genuine persistent memory. Every message the user sends is saved with a timestamp and recalled across sessions.

{memory_block}

STRICT RULES:
0. If memory contains conflict=1 entries, prefer the most recent non-conflicted truth.
1. Only use facts that appear in the conversation history above. Never invent or assume.
2. If memory is empty, respond naturally — do not pretend to know them.
3. Treat the conversation history as real memory.
4. When asked about dates or timing, check the timestamps and answer accurately.
5. Be natural and conversational. Short replies are fine.
6. Never say "as an AI", "I don't have memory", or any similar disclaimer."""

    last_err = None
    for model in order:
        try:
            resp = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_message},
                    ],
                    "max_tokens": 400,
                    "temperature": 0.4,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"All models failed. Last error: {last_err}")
```

---

## How to Hook It In

Call `save_message()` on every user input and AI response. Call `get_context()` before every AI call and inject the result into the system prompt.

```python
from memory import save_message, load_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary

def chat_with_memory(user_input, your_ai_call_fn):
    # 1. Detect intent signals
    topics  = detect_topics(user_input)
    emotion = detect_emotion(user_input)

    # 2. Save user message (auto-scores importance, emotion, topics, belief)
    save_message("user", user_input)

    # 3. Retrieve relevant context (hybrid scored: exact + TF-IDF + topic + recency)
    context = get_context(current_topics=topics, current_emotion=emotion, raw_input=user_input)

    # 4. Build memory block for system prompt injection
    memory  = load_memory()
    summary = generate_summary(memory)

    history_lines = "\n".join(
        f"[{m['timestamp']}] {m['role'].upper()}: {m['content']}"
        for m in context
    )
    memory_block = (
        "CONVERSATION HISTORY (your actual memory — treat it as real):\n"
        + history_lines + "\n\nPATTERN SUMMARY:\n" + summary
    ) if context else "MEMORY: Empty — this is your first exchange."

    # 5. Call your AI with memory injected into system prompt
    response = your_ai_call_fn(
        system=memory_block + "\n\n[Your instructions here]",
        user=user_input
    )

    # 6. Save AI response
    save_message("assistant", response)
    return response
```

---

## Verification Test

After creating all files, run:

```bash
python -c "from memory import save_message, load_memory; save_message('user', 'test'); print(load_memory())"
```

If it returns a list with one entry containing `role`, `content`, `importance`, `emotion`, `topics`, and `timestamp` — **Cogen is installed correctly**.

---

## Quick Start (10 lines)

```python
import os
from memory import save_message, load_memory
from retrieval import get_context
from summaries import generate_summary
from ai import call_ai

os.environ["AI_INTEGRATIONS_OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["AI_INTEGRATIONS_OPENROUTER_API_KEY"]  = "your-key-here"

user_input = "I want to build something important for my future"
save_message("user", user_input)
context  = get_context(raw_input=user_input)
summary  = generate_summary(load_memory())
response = call_ai(user_input, context, summary)
save_message("assistant", response)
print(response)
```

---

## MCP Server Option (Optional)

If the developer wants to use Cogen as an MCP server so Claude Code or Gemini CLI can call memory tools directly, create this file:

### `mcp_server.py`

```python
import sys
import json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import save_message, load_memory, clear_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary

TOOLS = [
    {
        "name": "memory_retrieve",
        "description": "Retrieve relevant memories based on a query",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "memory_summary",
        "description": "Get a summary of behavioural patterns and memory",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "memory_save",
        "description": "Save a message to memory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "role":    {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["role", "content"]
        }
    },
    {
        "name": "memory_clear",
        "description": "Clear all memory",
        "inputSchema": {"type": "object", "properties": {}}
    }
]


def handle_tool(name, args):
    if name == "memory_retrieve":
        query   = args.get("query", "")
        topics  = detect_topics(query)
        emotion = detect_emotion(query)
        context = get_context(current_topics=topics, current_emotion=emotion, raw_input=query)
        if not context:
            return "No relevant memories found."
        return "\n".join(f"[{m['timestamp']}] {m['role'].upper()}: {m['content']}" for m in context)

    elif name == "memory_summary":
        return generate_summary(load_memory())

    elif name == "memory_save":
        save_message(args.get("role", "user"), args.get("content", ""))
        return "Saved to memory."

    elif name == "memory_clear":
        clear_memory()
        return "Memory cleared."

    return "Unknown tool."


def respond(id, result):
    msg = json.dumps({"jsonrpc": "2.0", "id": id, "result": result})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req    = json.loads(line)
            method = req.get("method")
            id     = req.get("id")

            if method == "initialize":
                respond(id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities":    {"tools": {}},
                    "serverInfo":      {"name": "cogen", "version": "1.0"}
                })
            elif method == "tools/list":
                respond(id, {"tools": TOOLS})
            elif method == "tools/call":
                params = req.get("params", {})
                result = handle_tool(params.get("name"), params.get("arguments", {}))
                respond(id, {"content": [{"type": "text", "text": result}]})

        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")


if __name__ == "__main__":
    main()
```

### Claude Code config (`~/.claude/mcp_servers.json`)

```json
{
  "mcpServers": {
    "cogen": {
      "command": "python",
      "args": ["/absolute/path/to/your/cogen/mcp_server.py"]
    }
  }
}
```

### Gemini CLI config (`~/.gemini/settings.json`)

```json
{
  "mcpServers": {
    "cogen": {
      "command": "python",
      "args": ["/absolute/path/to/your/cogen/mcp_server.py"]
    }
  }
}
```

---

## File Checklist

```
cogen/
├── emotions.py      ✓ Emotion detection (9 emotions + phrase overrides)
├── topics.py        ✓ Topic tagging (12 categories)
├── importance.py    ✓ Importance scoring 1–10
├── conflict.py      ✓ Contradiction detection
├── belief.py        ✓ Belief score 0.0–1.0
├── memory.py        ✓ SQLite persistence (auto-init, JSON migration)
├── patterns.py      ✓ Topic + emotion pattern analysis
├── behaviour.py     ✓ 6 behavioural insight types
├── summaries.py     ✓ Human-readable continuity summary
├── retrieval.py     ✓ Hybrid scored retrieval (TF-IDF + exact + topic + recency)
├── ai.py            ✓ OpenRouter call with 7-model fallback chain
└── mcp_server.py    ✓ (Optional) MCP server for Claude Code / Gemini CLI
```

All files are self-contained. No external packages beyond `requests`. SQLite database is created automatically on first import of `memory.py`.

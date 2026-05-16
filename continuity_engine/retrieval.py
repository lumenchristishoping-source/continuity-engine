import math
import re
from collections import Counter
from memory import load_memory

# Always include this many most-recent messages no matter what
RECENT_WINDOW = 15
# Additional older messages pulled by relevance scoring
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


# ── TF-IDF helpers (stdlib only — no external deps) ──────────────────────────

def _tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def _build_corpus_df(messages):
    """Document-frequency table: how many messages each token appears in."""
    df = Counter()
    for msg in messages:
        for token in set(_tokenize(msg["content"])):
            df[token] += 1
    return df


def _tfidf_cosine(query_tokens, doc_tokens, corpus_df, total_docs):
    """
    Cosine similarity between query and document using TF-IDF weights.
    Handles queries like 'that thing we discussed' that have no exact topic match.
    Returns a value in [0, 1].
    """
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


# ── Per-message scoring ───────────────────────────────────────────────────────

def _score(msg, index, pool_size, current_topic_set, raw_lower,
           query_tokens, corpus_df, total_docs):
    score         = 0
    content_lower = msg["content"].lower()
    importance    = msg.get("importance", 1)
    msg_topics    = set(msg.get("topics", []))

    # ── Exact substring match in content → strongest signal (+40) ────────────
    if raw_lower and raw_lower in content_lower:
        score += 40

    # ── Topic tag overlap (0–25) ──────────────────────────────────────────────
    if current_topic_set:
        overlap = len(current_topic_set & msg_topics)
        score  += round((overlap / len(current_topic_set)) * 25)

    # ── TF-IDF semantic similarity (0–20) ─────────────────────────────────────
    # Catches "that thing we discussed" style queries with no topic match
    doc_tokens = _tokenize(msg["content"])
    tfidf      = _tfidf_cosine(query_tokens, doc_tokens, corpus_df, total_docs)
    score     += round(tfidf * 20)

    # ── Importance weight (3–30) ──────────────────────────────────────────────
    score += importance * 3

    # ── Relative recency within the older pool (0–10) ─────────────────────────
    if pool_size > 1:
        score += round((index / (pool_size - 1)) * 10)
    else:
        score += 10

    return score


# ── Public API ────────────────────────────────────────────────────────────────

def get_context(current_topics=None, current_emotion=None, raw_input=""):
    memory = load_memory()
    if not memory:
        return []

    current_topic_set = set(current_topics) if current_topics else set()
    raw_lower         = raw_input.lower().strip()
    query_tokens      = _tokenize(raw_input)
    total             = len(memory)

    corpus_df  = _build_corpus_df(memory)

    # ── 1. Always include the most recent messages ────────────────────────────
    recent_cutoff = max(0, total - RECENT_WINDOW)
    recent_msgs   = memory[recent_cutoff:]
    recent_keys   = {(m["role"], m["content"]) for m in recent_msgs}

    # ── 2. Score older messages for relevance ─────────────────────────────────
    older_msgs = memory[:recent_cutoff]
    scored     = []
    for i, msg in enumerate(older_msgs):
        s = _score(
            msg, i, len(older_msgs), current_topic_set, raw_lower,
            query_tokens, corpus_df, total
        )
        if s > 0:
            scored.append((s, i, msg))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # ── 3. Pick top unique extras ─────────────────────────────────────────────
    extras = []
    seen   = set(recent_keys)
    for _, _, msg in scored:
        key = (msg["role"], msg["content"])
        if key not in seen:
            seen.add(key)
            extras.append(msg)
        if len(extras) >= EXTRA_SCORED:
            break

    # ── 4. Merge and sort chronologically ────────────────────────────────────
    index_map = {id(m): i for i, m in enumerate(memory)}
    combined  = extras + recent_msgs
    combined.sort(key=lambda m: index_map.get(id(m), 0))

    return combined

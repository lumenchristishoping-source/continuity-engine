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
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def analyze_behaviour(memory):
    user_msgs = [m for m in memory if m.get("role") == "user"]
    all_msgs  = memory

    # ── 1. Emotional arc — breakthrough pattern ──────────────────────────────
    # Count negative → positive emotion transitions
    breakthrough_count = 0
    last_was_negative  = False
    for msg in user_msgs:
        emo = msg.get("emotion", "neutral")
        if emo in NEGATIVE_EMOTIONS:
            last_was_negative = True
        elif emo in POSITIVE_EMOTIONS and last_was_negative:
            breakthrough_count += 1
            last_was_negative = False

    # ── 2. Time of day patterns ───────────────────────────────────────────────
    bucket_importance = defaultdict(list)
    for msg in all_msgs:
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

    # ── 3. Topic-emotion associations ─────────────────────────────────────────
    topic_emotions = defaultdict(list)
    for msg in all_msgs:
        emo = msg.get("emotion", "neutral")
        for topic in msg.get("topics", []):
            topic_emotions[topic].append(emo)

    strong_associations = {}
    for topic, emotions in topic_emotions.items():
        if len(emotions) >= 3:
            most_common = max(set(emotions), key=emotions.count)
            if emotions.count(most_common) / len(emotions) >= 0.6:
                strong_associations[topic] = most_common

    # ── 4. Behavioural shift ──────────────────────────────────────────────────
    # Compare dominant emotion in first half vs second half of conversation
    behaviour_shift = None
    if len(all_msgs) >= 6:
        mid          = len(all_msgs) // 2
        first_emos   = [m.get("emotion") for m in all_msgs[:mid]
                        if m.get("emotion") and m.get("emotion") != "neutral"]
        second_emos  = [m.get("emotion") for m in all_msgs[mid:]
                        if m.get("emotion") and m.get("emotion") != "neutral"]
        if first_emos and second_emos:
            dom_first  = max(set(first_emos),  key=first_emos.count)
            dom_second = max(set(second_emos), key=second_emos.count)
            if dom_first != dom_second:
                behaviour_shift = {"from": dom_first, "to": dom_second}

    # ── 5. Unresolved threads ─────────────────────────────────────────────────
    # High-importance topics that went silent in last 10 messages
    recent_cutoff   = max(0, len(all_msgs) - 10)
    recent_topics   = set()
    for msg in all_msgs[recent_cutoff:]:
        recent_topics.update(msg.get("topics", []))

    unresolved_threads = []
    seen_unresolved    = set()
    for msg in all_msgs[:recent_cutoff]:
        if msg.get("importance", 1) >= 7:
            for topic in msg.get("topics", []):
                if topic not in recent_topics and topic not in seen_unresolved:
                    unresolved_threads.append(topic)
                    seen_unresolved.add(topic)

    # ── 6. Recurrence streaks ─────────────────────────────────────────────────
    # Topics that appeared in 3+ consecutive user messages
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

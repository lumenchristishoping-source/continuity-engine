def calculate_belief_score(new_content, memory):
    """
    Returns a belief score 0.0-1.0 for the new message.
    - Starts at 1.0
    - Drops to 0.3 if it contradicts existing memory
    - Boosted by 0.1 for each past confirmation of same thing
    """
    from conflict import detect_conflict

    new_lower = new_content.lower()
    score = 1.0

    # Check contradiction
    is_conflict, _ = detect_conflict(new_content, memory)
    if is_conflict:
        score = 0.3

    # Boost for repeated mentions of same thing
    confirmation_phrases = [
        "i like", "i love", "i enjoy", "i hate", "i dislike",
        "i am", "i'm", "i prefer", "i always", "i never"
    ]

    for phrase in confirmation_phrases:
        if phrase in new_lower:
            # Count how many past messages said similar thing
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

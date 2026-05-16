def detect_conflict(new_content, memory):
    """
    Checks if new message contradicts existing memory.
    Returns (is_conflict, conflicting_entry) or (False, None)
    """
    new_lower = new_content.lower()

    # Contradiction pairs — if you said X before and now say opposite
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

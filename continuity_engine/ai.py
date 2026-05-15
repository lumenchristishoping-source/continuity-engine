import os
import requests


def call_ai(user_message, retrieved_context, continuity_summary):
    base_url = os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key  = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY", "")

    has_memory = bool(retrieved_context)

    if has_memory:
        context_lines = "\n".join(
            f"[{msg.get('timestamp', 'unknown time')}] {msg['role']}: {msg['content']}"
            for msg in retrieved_context
        )
        memory_block = f"""WHAT I ACTUALLY KNOW ABOUT THIS USER (from saved conversation history):
{context_lines}

PATTERN SUMMARY:
{continuity_summary if continuity_summary.strip() else "(no patterns identified yet)"}"""
    else:
        memory_block = "MEMORY: Empty. This is the first conversation. I know absolutely nothing about this user yet."

    system_prompt = f"""You are a conversational AI with a persistent memory system. Every message the user sends is saved with a timestamp and recalled in future conversations.

{memory_block}

ABSOLUTE RULES — violating any of these is not allowed:
1. NEVER invent, assume, or guess anything about the user. If it is not in the memory above, you do not know it.
2. If memory is empty or has no relevant information, respond only to what the user just said — nothing more.
3. NEVER roleplay a history you don't have. Do not say things like "you've been doing X" or "I remember when you..." unless that exact information is in the memory block above.
4. When the user asks about dates, times, or "when did I say X" — use the timestamps from the memory block to answer accurately.
5. Be direct and conversational. No theatrical, dramatic, or emotional flourishes.
6. Do not say "as an AI" or "I don't have memory". Simply respond based on what you actually know.
7. If asked "who am I?" and memory is empty — say: "I don't know you yet. Tell me something about yourself and I'll remember it."
8. As conversations accumulate, naturally use what was shared before without announcing that you're using memory."""

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-small-2603",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            "max_tokens": 350,
            "temperature": 0.5
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

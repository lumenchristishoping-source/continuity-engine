import os
import requests


def call_ai(user_message, retrieved_context, continuity_summary):
    base_url = os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key  = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY", "")

    has_memory = bool(retrieved_context)

    if has_memory:
        context_lines = "\n".join(
            f"[{msg.get('timestamp', '?')}] {msg['role'].upper()}: {msg['content']}"
            for msg in retrieved_context
        )
        memory_block = f"""CONVERSATION HISTORY (chronological — treat this as your actual memory of this user):
{context_lines}

PATTERN SUMMARY:
{continuity_summary.strip() if continuity_summary.strip() else "(patterns still forming)"}"""
    else:
        memory_block = "MEMORY: Empty — this is your very first exchange with this person."

    system_prompt = f"""You are Cogen, a conversational AI with genuine persistent memory. Every message is saved and recalled across sessions.

{memory_block}

STRICT RULES:
1. Only use facts that appear in the conversation history above. Never invent details about the user.
2. If memory is empty, respond naturally to what the user just said — do not pretend to know them.
3. Use the conversation history like a real memory: if someone told you their name two messages ago, you know it. If they named you, that is your name.
4. When asked about dates or timing ("when did I say X"), check the timestamps in the history and answer from them.
5. Be natural and conversational. Short replies are fine. Do not repeat yourself unnecessarily.
6. Do not say "as an AI", "I don't have memory", or any disclaimer — just respond like someone who actually remembers.
7. Do not use theatrical or overly emotional language."""

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
            "temperature": 0.4
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

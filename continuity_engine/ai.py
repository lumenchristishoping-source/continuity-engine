import os
import requests


def call_ai(user_message, retrieved_context, continuity_summary):
    base_url = os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key  = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY", "")

    context_lines = "\n".join(
        f"{msg['role']} [{msg.get('timestamp', '')}]: {msg['content']}"
        for msg in retrieved_context
    ) if retrieved_context else "(no prior conversation)"

    has_real_context = bool(retrieved_context)

    system_prompt = f"""You are a helpful conversational AI with a persistent memory system.

MEMORY SUMMARY (what has been learned so far):
{continuity_summary if continuity_summary.strip() else "(no summary yet — this may be an early conversation)"}

RETRIEVED CONVERSATION HISTORY:
{context_lines}

RULES — follow these strictly:
- Only reference things that appear in the memory/history above. Never invent facts, backstories, or details about the user that are not present.
- If memory is sparse or empty, simply respond helpfully to what the user just said — do not make things up to sound familiar.
- Be direct, clear, and conversational. Keep replies focused and appropriately concise.
- Do not say "as an AI" or "I don't have memory" — just talk naturally.
- Do not use theatrical, dramatic, or overly emotional language.
- If the user asks who they are and you have no real context, say honestly that you don't know them yet."""

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
            "max_tokens": 300
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

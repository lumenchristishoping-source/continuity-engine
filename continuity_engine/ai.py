import os
import requests


def call_ai(user_message, retrieved_context, continuity_summary):
    base_url = os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY", "")

    context_lines = "\n".join(
        f"{msg['role']} [importance:{msg.get('importance',1)} | emotion:{msg.get('emotion','neutral')} | {msg.get('timestamp','')}]: {msg['content']}"
        for msg in retrieved_context
    )

    system_prompt = f"""You are an AI with genuine temporal memory of this user.

CONTINUITY SUMMARY:
{continuity_summary}

RETRIEVED CONTEXT:
{context_lines}

Rules:
- Never say "as an AI" or "I don't have memory"
- Don't explicitly mention you have memory — just USE it naturally
- If patterns show stress, acknowledge it subtly
- If there's a breakthrough after struggle, recognize it
- Respond like someone who actually knows this person over time"""

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
                {"role": "user", "content": user_message}
            ]
        },
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

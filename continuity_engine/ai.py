import os
import requests


MODELS = [
    "anthropic/claude-3-haiku-20240307",
    "openai/gpt-4o-mini",
]

MODEL_LABELS = {
    "anthropic/claude-3-haiku-20240307": "Claude 3 Haiku",
    "openai/gpt-4o-mini":               "GPT-4o mini",
    "mistralai/mistral-small-2603":      "Mistral Small",
}


def call_ai(user_message, retrieved_context, continuity_summary, preferred_model=None):
    base_url = os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key  = os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY", "")

    # Build ordered model list: user-chosen first, then fallbacks
    if preferred_model and preferred_model not in MODELS:
        order = [preferred_model] + MODELS
    elif preferred_model:
        order = [preferred_model] + [m for m in MODELS if m != preferred_model]
    else:
        order = MODELS

    has_memory = bool(retrieved_context)

    if has_memory:
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

    system_prompt = f"""You are Cogen, a conversational AI with genuine persistent memory. Every message the user sends is saved with a timestamp and recalled across sessions.

{memory_block}

STRICT RULES — never break these:
1. Only use facts that appear in the conversation history above. Never invent or assume anything about the user.
2. If memory is empty, respond naturally to what the user just said — do not pretend to know them.
3. Treat the conversation history as real memory: if the user told you their name, you know it; if they named you, that is your name.
4. When asked about dates or timing, check the timestamps in the history and answer from them accurately.
5. Be natural and conversational. Keep replies focused. Short replies are fine.
6. Never say "as an AI", "I don't have memory", or any similar disclaimer.
7. No theatrical, dramatic, or overly emotional language."""

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

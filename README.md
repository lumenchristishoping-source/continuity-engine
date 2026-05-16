# Continuity Engine

A persistent memory layer for AI models. Every message is tagged with importance (1–10),
detected emotion, topic tags, and a timestamp. A scored retrieval system surfaces the
most relevant past messages — not just recent ones — so any AI responds as if it
genuinely knows you across all sessions.

> "New chat" is a UI concept. Memory is session-agnostic.

---

## What it does

- Stores every message in a local **SQLite database** with metadata
- Retrieves relevant history using a **multi-factor scoring model** (TF-IDF cosine similarity + topic overlap + importance weighting + recency)
- Injects a formatted **memory block + pattern summary** into the AI system prompt
- Tracks **6 deep behavioural patterns** over time: breakthroughs, peak engagement time, topic-emotion associations, emotional shifts, unresolved threads, and recurrence streaks
- Works with **any OpenRouter-compatible model** (Claude, GPT, Mistral, etc.)
- Zero external ML dependencies — pure Python, fast, inspectable

---

## Quick start

```bash
# Clone
git clone https://github.com/your-username/continuity-engine.git
cd continuity-engine

# Install dependencies
pip install requests flask

# Set your OpenRouter credentials
export AI_INTEGRATIONS_OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
export AI_INTEGRATIONS_OPENROUTER_API_KEY="sk-or-your-key-here"

# Run interactive CLI
cd continuity_engine
python main.py
```

Memory is stored automatically in `continuity_engine/memory.db`.
No setup required. The database is created on first run.

---

## File structure

```
continuity_engine/
├── memory.py        — SQLite persistence (save_message, load_memory, clear_memory)
├── retrieval.py     — Scored context retrieval (TF-IDF + topic + importance + recency)
├── summaries.py     — Continuity summary generator (patterns + behaviour insights)
├── behaviour.py     — Deep behavioural analysis (6 pattern types)
├── patterns.py      — Recurring topic and emotion pattern analysis
├── ai.py            — OpenRouter API call with model fallback chain
├── emotions.py      — Keyword-based emotion detection
├── importance.py    — Message importance scoring (1–10)
├── topics.py        — Topic tag detection
├── main.py          — CLI entry point (interactive loop)
└── SKILL.md         — Integration protocol (inject into any AI system)
```

---

## Integrating into your own AI app

See `continuity_engine/SKILL.md` for the full integration protocol.

The short version — wrap your AI call like this:

```python
from continuity_engine.memory import save_message, load_memory
from continuity_engine.retrieval import get_context
from continuity_engine.summaries import generate_summary

def chat_with_memory(user_input, your_model_fn):
    save_message("user", user_input)
    context = get_context(raw_input=user_input)
    summary = generate_summary(load_memory())

    history = "\n".join(
        f"[{m['timestamp']}] {m['role'].upper()}: {m['content']}"
        for m in context
    )
    system = f"CONVERSATION HISTORY:\n{history}\n\nPATTERN SUMMARY:\n{summary}"

    response = your_model_fn(system=system, user=user_input)
    save_message("assistant", response)
    return response
```

---

## Retrieval scoring model

```
score = 0
if exact_substring_match in content:   score += 40
topic_overlap_ratio × 25:              score += 0–25
tfidf_cosine_similarity × 20:          score += 0–20   ← handles vague queries
importance (1–10) × 3:                 score += 3–30
relative_recency_in_older_pool × 10:   score += 0–10
```

Always included: last **15** messages  
Scored extras from older history: up to **8**

---

## Models supported

Default model chain (tries in order, falls back automatically):

1. `anthropic/claude-3-haiku-20240307`
2. `openai/gpt-4o-mini`

Any OpenRouter model ID can be passed as `preferred_model` to `call_ai()`.

---

## Environment variables

| Variable                               | Description                          |
|----------------------------------------|--------------------------------------|
| `AI_INTEGRATIONS_OPENROUTER_BASE_URL`  | OpenRouter-compatible API base URL   |
| `AI_INTEGRATIONS_OPENROUTER_API_KEY`   | Your API key                         |

On Replit these are auto-provisioned. Anywhere else, export them manually.

---

## Behaviour patterns

`behaviour.py` → `analyze_behaviour(memory)` returns:

| Key                   | What it detects                                              |
|-----------------------|--------------------------------------------------------------|
| `breakthrough_count`  | Negative → positive emotion transition count                 |
| `peak_time`           | Time bucket with highest average message importance          |
| `strong_associations` | Topics where one emotion dominates (≥60% of appearances)    |
| `behaviour_shift`     | Dominant emotion in first half vs second half of history     |
| `unresolved_threads`  | High-importance topics (7+) absent from last 10 messages    |
| `recurrence_streaks`  | Topics in 3+ consecutive user messages                      |

---

## License

MIT

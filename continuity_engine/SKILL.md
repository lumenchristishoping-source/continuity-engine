# Continuity Engine — Memory Layer Protocol

A drop-in persistent memory layer for any AI system. Every message is stored with
importance, emotion, topics, and a timestamp. Before each AI call, the most relevant
past messages are retrieved and injected into the system prompt so the model responds
with genuine continuity — even across completely new sessions.

---

## How it works

```
User message
    │
    ▼
┌──────────────────────────────────────────────┐
│  1. Analyse                                  │
│     detect_topics(content)   → topic tags   │
│     detect_emotion(content)  → emotion      │
│     calculate_importance()   → score 1–10   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  2. Save to SQLite (memory.db)               │
│     role, content, importance,               │
│     emotion, topics[], timestamp             │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  3. Retrieve relevant context                │
│     — Last 15 messages always included       │
│     — Up to 8 older messages scored by:      │
│       · Exact substring match    (+40)       │
│       · Topic tag overlap        (0–25)      │
│       · TF-IDF cosine similarity (0–20)      │
│       · Importance × 3          (3–30)       │
│       · Relative recency        (0–10)       │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  4. Build pattern summary                    │
│     recurring topics, dominant emotion,      │
│     emotional spikes, behaviour insights     │
│     (breakthroughs, peak time, shifts,       │
│      unresolved threads, recurrence streaks) │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  5. Inject into system prompt                │
│     CONVERSATION HISTORY block +             │
│     PATTERN SUMMARY block                    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
                  AI model call
                       │
                       ▼
              Save AI response → memory.db
```

---

## Memory schema

Each stored message has exactly these fields:

| Field        | Type        | Description                                      |
|-------------|-------------|--------------------------------------------------|
| `role`       | `string`    | `"user"` or `"assistant"`                        |
| `content`    | `string`    | Raw message text                                 |
| `importance` | `int` 1–10  | Scored by length, keywords, question density     |
| `emotion`    | `string`    | `excitement`, `stress`, `motivation`, `doubt`,   |
|              |             | `frustration`, `curiosity`, `neutral`            |
| `topics`     | `string[]`  | From: `ai`, `coding`, `project`, `future`,       |
|              |             | `personal`, `learning`, `problem`, `planning`    |
| `timestamp`  | `string`    | `"YYYY-MM-DD HH:MM:SS"` (local time)             |

---

## System prompt injection format

Prepend this block to your system prompt before every AI call:

```
CONVERSATION HISTORY (your actual memory — treat it as real):
[2025-05-10 14:22:01] USER: I'm building a startup called Sarvix focused on AI tools.
[2025-05-10 14:22:45] ASSISTANT: That sounds exciting. What problem does Sarvix solve?
[2025-05-10 15:01:12] USER: I've been stressed about the launch timeline.
...

PATTERN SUMMARY:
  • Recurring topics: project, ai, coding
  • Overall emotional tone: stress
  • Peak engagement: evening (highest avg importance)
  • Unresolved threads: launch, funding
```

Then append your own system instructions underneath. The model treats the history
block as real memory — not "previous messages" but actual recall.

---

## Core rules to include in your system prompt

Add these as non-negotiable constraints beneath the memory block:

```
1. Only use facts that appear in the conversation history above. Never invent or assume anything about the user.
2. If memory is empty, respond naturally to what the user just said — do not pretend to know them.
3. Treat the conversation history as real memory: if the user told you their name, you know it.
4. When asked about dates or timing, check the timestamps and answer accurately.
5. Never say "as an AI", "I don't have memory", or any similar disclaimer.
```

---

## Integration patterns

### Pattern A — API wrapper (recommended)

Wrap your existing AI call with the memory layer:

```python
from continuity_engine.memory import save_message, load_memory
from continuity_engine.retrieval import get_context
from continuity_engine.topics import detect_topics
from continuity_engine.emotions import detect_emotion
from continuity_engine.summaries import generate_summary

def chat_with_memory(user_input, model_call_fn):
    # 1. Analyse & save user message
    topics  = detect_topics(user_input)
    emotion = detect_emotion(user_input)
    save_message("user", user_input)

    # 2. Retrieve relevant context
    context = get_context(
        current_topics=topics,
        current_emotion=emotion,
        raw_input=user_input
    )

    # 3. Build memory block for injection
    memory  = load_memory()
    summary = generate_summary(memory)

    history_lines = "\n".join(
        f"[{m['timestamp']}] {m['role'].upper()}: {m['content']}"
        for m in context
    )
    memory_block = (
        "CONVERSATION HISTORY (your actual memory — treat it as real):\n"
        + history_lines
        + "\n\nPATTERN SUMMARY:\n"
        + summary
    ) if context else "MEMORY: Empty — this is your first exchange."

    # 4. Call your AI with the injected system prompt
    response = model_call_fn(
        system=f"{memory_block}\n\n[Your system instructions here]",
        user=user_input
    )

    # 5. Save AI response
    save_message("assistant", response)
    return response
```

### Pattern B — Middleware / proxy

Intercept the request before it reaches the model:

```python
def continuity_middleware(request):
    user_input = request["messages"][-1]["content"]

    # Build and prepend memory block to the system message
    context      = get_context(raw_input=user_input)
    memory_block = build_memory_block(context)

    if request.get("system"):
        request["system"] = memory_block + "\n\n" + request["system"]
    else:
        request["system"] = memory_block

    return request
```

### Pattern C — CLI command

```bash
# Single-turn with memory
echo "What should I work on today?" | cogen

# Interactive session
cogen --interactive

# Show memory summary
cogen --summary

# Clear memory
cogen --clear
```

---

## Environment variables

| Variable                             | Description                                      |
|--------------------------------------|--------------------------------------------------|
| `AI_INTEGRATIONS_OPENROUTER_BASE_URL`| OpenRouter-compatible base URL (Replit-managed)  |
| `AI_INTEGRATIONS_OPENROUTER_API_KEY` | API key (Replit-managed or your own)             |

If you are running outside Replit, set these to your own OpenRouter credentials:

```bash
export AI_INTEGRATIONS_OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
export AI_INTEGRATIONS_OPENROUTER_API_KEY="sk-or-..."
```

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
├── memory.db        — SQLite database (auto-created, user-owned)
└── SKILL.md         — This file
```

---

## Behaviour patterns tracked

The `behaviour.py` module analyses memory and surfaces:

| Pattern               | What it detects                                                    |
|-----------------------|--------------------------------------------------------------------|
| `breakthrough_count`  | Times a negative emotion (stress/doubt) → positive (motivation)   |
| `peak_time`           | Morning/afternoon/evening/night with highest avg importance        |
| `strong_associations` | Topics where 60%+ of messages carry the same emotion              |
| `behaviour_shift`     | Dominant emotion changed between first and second half of history  |
| `unresolved_threads`  | High-importance topics (7+) that went silent in last 10 messages  |
| `recurrence_streaks`  | Topics appearing in 3+ consecutive user messages (deep focus)     |

---

## "New chat" is a UI concept — memory is session-agnostic

The continuity engine does not use chat session IDs. Memory persists in `memory.db`
across every conversation, every new session, every browser tab. "New chat" in any
UI means nothing to the engine — the next message always loads the full relevant
history. This is by design.

---

## Retrieval scoring (reference)

```
score = 0
if exact_substring_match:        score += 40
if topic_overlap:                 score += 0–25  (proportional)
score += tfidf_cosine_sim * 20               (handles vague queries)
score += importance * 3                      (range: 3–30)
score += relative_recency_in_pool * 10       (range: 0–10)
```

Minimum score to be included: `> 0`
Maximum extras pulled from older messages: `8`
Recent window always included: last `15` messages

---

## Tool-use integration (AI calls memory itself)

For models that support function calling (Claude, GPT-4, Gemini, any OpenRouter model
with tool use), you can give the AI direct access to memory — it decides when to recall,
save, or summarise without you pre-building anything.

### Setup

```python
import json
from continuity_engine.tools import TOOL_DEFINITIONS, handle_tool_call

# Pass TOOL_DEFINITIONS to your model call
response = client.chat.completions.create(
    model="anthropic/claude-3-haiku-20240307",
    messages=messages,
    tools=TOOL_DEFINITIONS,       # ← inject the tool schemas
    tool_choice="auto"
)

# Dispatch any tool calls the model makes
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = handle_tool_call(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        messages.append({
            "role":         "tool",
            "tool_call_id": tool_call.id,
            "content":      result
        })
    # Send tool results back for the final response
    final = client.chat.completions.create(model=..., messages=messages)
```

### Available tools

| Tool name         | When the AI calls it                                              |
|-------------------|-------------------------------------------------------------------|
| `memory_retrieve` | User references something from the past, or context would help   |
| `memory_summary`  | User asks how they've been doing or what they usually talk about |
| `memory_save`     | User shares something important that should persist long-term    |
| `memory_clear`    | User explicitly asks to forget everything                        |

All four tools are defined in `tools.py` with full OpenAI-compatible JSON schemas.
`handle_tool_call(name, arguments)` dispatches any tool call to the right function
and returns a string result ready to send back as a tool message.

---

## CLI usage (cogen)

`cogen.py` is a ready-to-run CLI that handles everything — retrieve, inject, call, save.

```bash
# Single reply
python cogen.py "what should I work on today?"

# Interactive session
python cogen.py

# Show memory patterns
python cogen.py --summary

# Clear all memory
python cogen.py --clear

# Use a specific model
python cogen.py --model openai/gpt-4o-mini "hello"

# Show recalled context alongside the reply
python cogen.py --verbose "that project I was stressed about"
```

Add a shell alias to use it from anywhere:

```bash
# In ~/.bashrc or ~/.zshrc
alias cogen="python /path/to/continuity_engine/cogen.py"
```

---

## Quick start (standalone Python)

```bash
# Install dependencies
pip install requests flask

# Set your API credentials
export AI_INTEGRATIONS_OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
export AI_INTEGRATIONS_OPENROUTER_API_KEY="your-key-here"

# Run interactive CLI
cd continuity_engine
python main.py
```

Memory is stored in `continuity_engine/memory.db` automatically.
No configuration needed. The database is created on first run.

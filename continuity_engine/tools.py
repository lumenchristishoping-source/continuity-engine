"""
Continuity Engine — Tool-use interface

Exports:
  TOOL_DEFINITIONS   — OpenAI-compatible JSON tool schemas
                       (works with Claude, GPT-4, Gemini, OpenRouter models)
  handle_tool_call() — dispatch function: AI calls a tool → get a result back

Usage with any function-calling model:
    from tools import TOOL_DEFINITIONS, handle_tool_call

    # 1. Pass TOOL_DEFINITIONS to your model call alongside the system prompt
    # 2. When the model returns a tool_call, pass it to handle_tool_call()
    # 3. Send the result back as a tool message
    # 4. The model then responds with full memory context
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from memory import save_message, load_memory, clear_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary


# ── Tool definitions (OpenAI / Anthropic / OpenRouter format) ─────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "memory_retrieve",
            "description": (
                "Retrieve relevant past messages from long-term memory that are "
                "related to the current query. Call this whenever the user asks "
                "about something they mentioned before, references a past event, "
                "or when context from previous sessions would improve your answer."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic, question, or phrase to search memory for."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_summary",
            "description": (
                "Get a high-level summary of the user's conversation patterns — "
                "recurring topics, dominant emotions, behavioural insights, "
                "unresolved threads, and peak engagement times. Use this when "
                "the user asks how they've been doing, what they usually talk about, "
                "or to understand their overall state across sessions."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_save",
            "description": (
                "Save an important piece of information to long-term memory with "
                "full metadata tagging (importance, emotion, topics, timestamp). "
                "Use this to explicitly store facts the user shares that should "
                "survive future sessions — goals, decisions, personal details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["user", "assistant"],
                        "description": "Who said it — 'user' or 'assistant'."
                    },
                    "content": {
                        "type": "string",
                        "description": "The message or fact to store."
                    }
                },
                "required": ["role", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_clear",
            "description": (
                "Permanently wipe all stored memory. Only call this if the user "
                "explicitly asks to clear, reset, or forget all past conversations."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ── Tool implementations ──────────────────────────────────────────────────────

def _memory_retrieve(query: str) -> str:
    topics  = detect_topics(query)
    emotion = detect_emotion(query)
    context = get_context(
        current_topics=topics,
        current_emotion=emotion,
        raw_input=query
    )
    if not context:
        return "No relevant memory found for this query."

    lines = [
        f"[{m.get('timestamp', '?')}] {m['role'].upper()} "
        f"(importance:{m.get('importance',1)} | emotion:{m.get('emotion','neutral')}): "
        f"{m['content']}"
        for m in context
    ]
    return "RETRIEVED MEMORY:\n" + "\n".join(lines)


def _memory_summary() -> str:
    memory  = load_memory()
    summary = generate_summary(memory)
    count   = len(memory)
    return f"Total messages stored: {count}\n\n{summary}"


def _memory_save(role: str, content: str) -> str:
    if role not in ("user", "assistant"):
        return "Error: role must be 'user' or 'assistant'."
    save_message(role, content)
    return f"Saved to memory: [{role}] {content[:60]}{'...' if len(content) > 60 else ''}"


def _memory_clear() -> str:
    clear_memory()
    return "All memory has been cleared."


# ── Dispatcher ────────────────────────────────────────────────────────────────

_HANDLERS = {
    "memory_retrieve": lambda args: _memory_retrieve(args["query"]),
    "memory_summary":  lambda args: _memory_summary(),
    "memory_save":     lambda args: _memory_save(args["role"], args["content"]),
    "memory_clear":    lambda args: _memory_clear(),
}


def handle_tool_call(name: str, arguments: dict) -> str:
    """
    Dispatch an AI tool call to the matching engine function.

    Args:
        name      : tool name (from the model's tool_call response)
        arguments : parsed JSON arguments (dict)

    Returns:
        A string result to send back as a tool message.

    Example (OpenAI SDK):
        for tool_call in response.tool_calls:
            result = handle_tool_call(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      result
            })
    """
    handler = _HANDLERS.get(name)
    if not handler:
        return f"Unknown tool: {name}"
    try:
        return handler(arguments)
    except Exception as e:
        return f"Tool error ({name}): {e}"

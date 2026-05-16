import sys
import json
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import save_message, load_memory, clear_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary

TOOLS = [
    {
        "name": "memory_retrieve",
        "description": "Retrieve relevant memories based on a query",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "memory_summary",
        "description": "Get a summary of behavioural patterns and memory",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "memory_save",
        "description": "Save a message to memory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "role": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["role", "content"]
        }
    },
    {
        "name": "memory_clear",
        "description": "Clear all memory",
        "inputSchema": {"type": "object", "properties": {}}
    }
]

def handle_tool(name, args):
    if name == "memory_retrieve":
        query = args.get("query", "")
        topics = detect_topics(query)
        emotion = detect_emotion(query)
        context = get_context(
            current_topics=topics,
            current_emotion=emotion,
            raw_input=query
        )
        if not context:
            return "No relevant memories found."
        lines = [
            f"[{m['timestamp']}] {m['role'].upper()}: {m['content']}"
            for m in context
        ]
        return "\n".join(lines)

    elif name == "memory_summary":
        memory = load_memory()
        return generate_summary(memory)

    elif name == "memory_save":
        save_message(args.get("role", "user"), args.get("content", ""))
        return "Saved to memory."

    elif name == "memory_clear":
        clear_memory()
        return "Memory cleared."

    return "Unknown tool."

def respond(id, result):
    msg = json.dumps({"jsonrpc": "2.0", "id": id, "result": result})
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            id = req.get("id")

            if method == "initialize":
                respond(id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "cogen", "version": "1.0"}
                })

            elif method == "tools/list":
                respond(id, {"tools": TOOLS})

            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                result = handle_tool(name, args)
                respond(id, {
                    "content": [{"type": "text", "text": result}]
                })

        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")

if __name__ == "__main__":
    main()

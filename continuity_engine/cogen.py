#!/usr/bin/env python3
"""
cogen — Continuity Engine CLI

Usage:
  cogen "your message"                     Single reply with memory
  cogen                                    Interactive session
  cogen --summary                          Show memory pattern summary
  cogen --clear                            Wipe all memory
  cogen --model openai/gpt-4o-mini "hi"   Use a specific model
  cogen --verbose "your message"           Show recalled context too
  cogen --help                             Show this help
"""

import sys
import os

# Works regardless of where cogen is called from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from memory import save_message, load_memory, clear_memory
from retrieval import get_context
from topics import detect_topics
from emotions import detect_emotion
from summaries import generate_summary
from ai import call_ai


# ── Colours ───────────────────────────────────────────────────────────────────
PURPLE = "\033[35m"
WHITE  = "\033[97m"
DIM    = "\033[90m"
RESET  = "\033[0m"
CLEAR  = " " * 20 + "\r"

def _p(colour, text): return f"{colour}{text}{RESET}"


# ── Display helpers ───────────────────────────────────────────────────────────

def print_header():
    memory    = load_memory()
    msg_count = len([m for m in memory if m["role"] == "user"])
    label     = f"{msg_count} past exchanges in memory" if msg_count else "fresh session — no memory yet"
    print(f"\n{_p(PURPLE, '● Continuity Engine')}  {_p(DIM, 'cogen v1')}")
    print(_p(DIM, "─" * 44))
    print(_p(DIM, label))
    print(_p(DIM, "Type 'exit' to quit · 'summary' to see patterns\n"))


def show_summary():
    memory  = load_memory()
    summary = generate_summary(memory)
    print(_p(DIM, "\n┌─ MEMORY SUMMARY " + "─" * 28))
    for line in summary.split("\n"):
        print(f"{_p(DIM, '│')}  {line.strip().lstrip('•').strip()}")
    print(_p(DIM, "└" + "─" * 46))


def show_context(context):
    if not context:
        return
    print(_p(DIM, "┌─ RECALLED " + "─" * 34))
    for msg in context:
        role    = msg["role"].upper()
        ts      = msg.get("timestamp", "")
        content = msg["content"]
        if len(content) > 72:
            content = content[:69] + "..."
        print(f"{_p(DIM, '│')} [{ts}] {_p(DIM, role + ':')} {content}")
    print(_p(DIM, "└" + "─" * 46))


# ── Core turn ─────────────────────────────────────────────────────────────────

def run_turn(user_input, model=None, verbose=False):
    topics  = detect_topics(user_input)
    emotion = detect_emotion(user_input)

    save_message("user", user_input)

    context = get_context(
        current_topics=topics,
        current_emotion=emotion,
        raw_input=user_input
    )

    memory  = load_memory()
    summary = generate_summary(memory)

    if verbose:
        show_context(context)

    try:
        response = call_ai(user_input, context, summary, preferred_model=model)
    except Exception as e:
        response = f"[Error: {e}]"

    save_message("assistant", response)
    return response


# ── Modes ─────────────────────────────────────────────────────────────────────

def interactive_mode(model=None, verbose=False):
    print_header()
    while True:
        try:
            user_input = input(f"{_p(WHITE, 'You:')} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{_p(DIM, 'Session ended.')}")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print(_p(DIM, "Session ended."))
            break
        if user_input.lower() == "summary":
            show_summary()
            continue

        print(f"{_p(DIM, 'Thinking...')}", end="\r")
        response = run_turn(user_input, model=model, verbose=verbose)
        print(CLEAR, end="")
        print(f"\n{_p(PURPLE, 'Cogen:')} {response}\n")


def single_turn_mode(user_input, model=None, verbose=False):
    response = run_turn(user_input, model=model, verbose=verbose)
    print(response)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    model   = None
    verbose = False
    remaining = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--model" and i + 1 < len(args):
            model = args[i + 1]
            i += 2
        elif arg in ("--verbose", "-v"):
            verbose = True
            i += 1
        elif arg == "--summary":
            show_summary()
            return
        elif arg == "--clear":
            clear_memory()
            print(_p(DIM, "Memory cleared."))
            return
        elif arg in ("--help", "-h"):
            print(__doc__)
            return
        else:
            remaining.append(arg)
            i += 1

    if remaining:
        single_turn_mode(" ".join(remaining), model=model, verbose=verbose)
    else:
        interactive_mode(model=model, verbose=verbose)


if __name__ == "__main__":
    main()

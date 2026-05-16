import sqlite3
import json
import os
from datetime import datetime
from importance import calculate_importance
from topics import detect_topics
from emotions import detect_emotion

DB_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db")
LEGACY_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")


# ── Connection ────────────────────────────────────────────────────────────────

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Write-Ahead Logging: faster writes, non-blocking reads
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


# ── Schema init ───────────────────────────────────────────────────────────────

def _init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                role       TEXT    NOT NULL,
                content    TEXT    NOT NULL,
                importance INTEGER DEFAULT 1,
                emotion    TEXT    DEFAULT 'neutral',
                topics     TEXT    DEFAULT '[]',
                timestamp  TEXT    NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts         ON messages(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON messages(importance)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role       ON messages(role)")
        conn.commit()


# ── JSON → SQLite one-time migration ──────────────────────────────────────────

def _migrate_json():
    if not os.path.exists(LEGACY_JSON):
        return
    try:
        with open(LEGACY_JSON, "r") as f:
            data = json.load(f)
        if not data:
            return
        with _get_conn() as conn:
            # Only migrate if the DB is empty (avoids duplicates on restart)
            count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            if count > 0:
                return
            for msg in data:
                conn.execute(
                    """INSERT INTO messages
                       (role, content, importance, emotion, topics, timestamp)
                       VALUES (?,?,?,?,?,?)""",
                    (
                        msg["role"],
                        msg["content"],
                        msg.get("importance", 1),
                        msg.get("emotion", "neutral"),
                        json.dumps(msg.get("topics", [])),
                        msg.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    ),
                )
            conn.commit()
        # Rename so re-migrations never happen
        os.rename(LEGACY_JSON, LEGACY_JSON + ".migrated")
        print(f"[memory] Migrated {len(data)} messages from memory.json → SQLite")
    except Exception as e:
        print(f"[memory] JSON migration skipped: {e}")


# ── Initialise on import ──────────────────────────────────────────────────────
_init_db()
_migrate_json()


# ── Row helper ────────────────────────────────────────────────────────────────

def _row_to_dict(row):
    d = dict(row)
    d["topics"] = json.loads(d.get("topics") or "[]")
    return d


# ── Public API ────────────────────────────────────────────────────────────────

def load_memory():
    """Return all messages in chronological order."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM messages ORDER BY id ASC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def save_message(role, content):
    """Analyse and persist a single message."""
    memory     = load_memory()
    importance = calculate_importance(content, memory_history=memory)
    topics     = detect_topics(content)
    emotion    = detect_emotion(content)
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO messages
               (role, content, importance, emotion, topics, timestamp)
               VALUES (?,?,?,?,?,?)""",
            (role, content, importance, emotion, json.dumps(topics), timestamp),
        )
        conn.commit()


def clear_memory():
    """Wipe all stored messages."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM messages")
        conn.commit()

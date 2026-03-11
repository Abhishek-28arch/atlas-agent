"""
JARVIS — memory/history.py
SQLite-backed conversation history
"""

import sqlite3
import os
from datetime import datetime
from rich.console import Console

console = Console()


class ConversationHistory:
    """Persistent conversation history using SQLite."""

    def __init__(self, db_path: str = "./data/history.db"):
        """
        Initialize the conversation history.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
        self.session_id = self._create_session()

    def _init_db(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def _create_session(self) -> int:
        """Start a new conversation session."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (started_at) VALUES (?)",
                (datetime.now().isoformat(),),
            )
            conn.commit()
            return cursor.lastrowid

    def save_message(self, role: str, content: str):
        """
        Save a message to the current session.

        Args:
            role: 'user' or 'assistant'
            content: The message text.
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (self.session_id, role, content, datetime.now().isoformat()),
            )
            conn.commit()

    def get_recent(self, n: int = 10) -> list[dict]:
        """
        Get the most recent N messages from the current session.

        Args:
            n: Number of messages to retrieve.

        Returns:
            List of message dicts with 'role' and 'content' keys.
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT role, content FROM messages 
                   WHERE session_id = ? 
                   ORDER BY id DESC LIMIT ?""",
                (self.session_id, n),
            ).fetchall()

        # Reverse to get chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def get_all_sessions(self) -> list[dict]:
        """Get a summary of all past sessions."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT s.id, s.started_at, s.ended_at, COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                GROUP BY s.id
                ORDER BY s.id DESC
            """).fetchall()

        return [
            {
                "session_id": row[0],
                "started_at": row[1],
                "ended_at": row[2],
                "message_count": row[3],
            }
            for row in rows
        ]

    def end_session(self):
        """Mark the current session as ended."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET ended_at = ? WHERE id = ?",
                (datetime.now().isoformat(), self.session_id),
            )
            conn.commit()

    def get_total_messages(self) -> int:
        """Get total message count across all sessions."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) FROM messages").fetchone()
            return row[0] if row else 0

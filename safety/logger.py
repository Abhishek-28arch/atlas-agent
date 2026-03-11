"""
JARVIS — safety/logger.py
Action audit logger — logs every action with timestamp
"""

import os
from datetime import datetime
from rich.console import Console

console = Console()


class ActionLogger:
    """Logs all JARVIS actions to a persistent audit file."""

    def __init__(self, log_file: str = "./data/logs/actions.log"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def log(self, action_type: str, description: str, status: str = "ok"):
        """
        Log an action.

        Args:
            action_type: Category (e.g., 'llm_query', 'file_read', 'rag_add')
            description: What happened.
            status: 'ok', 'error', 'blocked', 'dry_run'
        """
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{status.upper()}] [{action_type}] {description}\n"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            console.print(f"[red]✗ Logger error: {e}[/red]")

    def get_recent(self, n: int = 50) -> list[str]:
        """Get the last N log entries."""
        if not os.path.exists(self.log_file):
            return []

        with open(self.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        return lines[-n:]

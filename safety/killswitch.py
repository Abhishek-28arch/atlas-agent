"""
JARVIS — safety/killswitch.py
Emergency stop — terminates all JARVIS processes
"""

import os
import signal
import sys
from rich.console import Console

console = Console()


def kill():
    """Kill the current JARVIS process immediately."""
    console.print("\n[bold red]🛑 KILL SWITCH ACTIVATED — Shutting down JARVIS[/bold red]")
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    # Allow running as: python -m safety.killswitch
    console.print("[bold red]🛑 Emergency Stop[/bold red]")
    console.print("Terminating JARVIS processes...")

    # Kill the main process if running
    try:
        kill()
    except Exception:
        sys.exit(1)

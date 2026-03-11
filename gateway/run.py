"""
JARVIS — gateway/run.py
CLI runner for the Gateway server — start/stop/status
Usage: python -m gateway.run start|stop|status
"""

import os
import sys
import signal
import subprocess
from rich.console import Console

console = Console()

PID_FILE = os.path.expanduser("~/.jarvis_gateway.pid")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def start(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, foreground: bool = False):
    """Start the Gateway server."""
    if is_running():
        console.print("[yellow]⚠ Gateway is already running[/yellow]")
        status()
        return

    if foreground:
        console.print(f"[cyan]◈ Starting JARVIS Gateway on {host}:{port}...[/cyan]")
        os.system(f"uvicorn gateway.server:app --host {host} --port {port} --reload")
    else:
        console.print(f"[cyan]◈ Starting JARVIS Gateway (background) on {host}:{port}...[/cyan]")

        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "gateway.server:app",
             "--host", host, "--port", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        # Save PID
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))

        console.print(f"[green]✓ Gateway started (PID: {process.pid})[/green]")
        console.print(f"[dim]  API: http://{host}:{port}[/dim]")
        console.print(f"[dim]  Docs: http://{host}:{port}/docs[/dim]")


def stop():
    """Stop the Gateway server."""
    if not os.path.exists(PID_FILE):
        console.print("[yellow]⚠ Gateway is not running (no PID file)[/yellow]")
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        console.print(f"[green]✓ Gateway stopped (PID: {pid})[/green]")
    except ProcessLookupError:
        os.remove(PID_FILE)
        console.print("[yellow]⚠ Gateway was not running (stale PID file removed)[/yellow]")


def status():
    """Check if the Gateway is running."""
    if is_running():
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        console.print(f"[green]● Gateway is running (PID: {pid})[/green]")
        console.print(f"[dim]  API: http://{DEFAULT_HOST}:{DEFAULT_PORT}[/dim]")
        console.print(f"[dim]  Docs: http://{DEFAULT_HOST}:{DEFAULT_PORT}/docs[/dim]")
    else:
        console.print("[red]○ Gateway is not running[/red]")


def is_running() -> bool:
    """Check if the Gateway process is alive."""
    if not os.path.exists(PID_FILE):
        return False

    with open(PID_FILE, "r") as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, 0)  # Signal 0 = check existence only
        return True
    except (ProcessLookupError, PermissionError):
        os.remove(PID_FILE)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("Usage: python -m gateway.run [start|stop|status]")
        console.print("  start     — Start the Gateway (background)")
        console.print("  start -f  — Start in foreground (for development)")
        console.print("  stop      — Stop the Gateway")
        console.print("  status    — Check if the Gateway is running")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        fg = "-f" in sys.argv or "--foreground" in sys.argv
        start(foreground=fg)
    elif command == "stop":
        stop()
    elif command == "status":
        status()
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        sys.exit(1)

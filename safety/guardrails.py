"""
JARVIS — safety/guardrails.py
Safety guardrails — path protection, command sanitization, rate limiting, approval gates
Enhanced with patterns from OpenClaw's security model
"""

import os
import time
from collections import deque
from rich.console import Console

console = Console()

# Commands that should NEVER be executed
BLOCKED_COMMANDS = {
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", ":(){", "fork bomb",
    "chmod -R 777 /", "chown -R", "> /dev/sda", "wget | sh", "curl | sh",
    "shutdown", "reboot", "init 0", "init 6", "halt",
}

# Patterns in commands that are dangerous
DANGEROUS_PATTERNS = [
    "rm -rf /",
    "> /dev/sd",
    "mkfs.",
    "dd if=/dev/zero",
    ":(){:|:&};:",
    "fork()",
    "chmod 777 /",
]


class SafetyGuardrails:
    """Enforces safety rules before actions execute."""

    def __init__(self, config: dict):
        """
        Initialize guardrails from config.

        Args:
            config: The 'safety' section of config.yaml.
        """
        self.require_approval = config.get("require_approval_for", [])
        self.blacklisted_paths = [
            os.path.realpath(os.path.expanduser(p))
            for p in config.get("blacklisted_paths", [])
        ]
        self.max_actions_per_minute = config.get("max_actions_per_minute", 10)
        self.dry_run = config.get("dry_run", False)

        # Rate limiting state
        self._action_timestamps: deque = deque()

    def check_path(self, path: str) -> bool:
        """
        Check if a path is safe to access.
        Resolves symlinks and prevents path traversal.

        Args:
            path: The file or directory path to check.

        Returns:
            True if safe, False if blacklisted or dangerous.
        """
        # Remove null bytes
        path = path.replace('\x00', '')

        # Resolve to absolute real path (follows symlinks, resolves ../)
        try:
            expanded = os.path.realpath(os.path.expanduser(path))
        except (ValueError, OSError):
            console.print(f"[red]🛡️ BLOCKED: Invalid path '{path}'[/red]")
            return False

        for blocked in self.blacklisted_paths:
            if expanded == blocked or expanded.startswith(blocked + os.sep):
                console.print(f"[red]🛡️ BLOCKED: Path '{path}' is blacklisted[/red]")
                return False

        return True

    def check_command(self, command: str) -> bool:
        """
        Check if a shell command is safe to execute.

        Args:
            command: The shell command string.

        Returns:
            True if safe, False if dangerous.
        """
        cmd_lower = command.lower().strip()

        # Check exact blocked commands
        for blocked in BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                console.print(f"[red]🛡️ BLOCKED: Dangerous command detected[/red]")
                console.print(f"[red]  Pattern: {blocked}[/red]")
                return False

        # Check dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern.lower() in cmd_lower:
                console.print(f"[red]🛡️ BLOCKED: Dangerous command pattern[/red]")
                return False

        return True

    def check_rate_limit(self) -> bool:
        """
        Check if action rate limit has been exceeded.

        Returns:
            True if within limits, False if rate exceeded.
        """
        now = time.time()

        # Remove timestamps older than 60 seconds
        while self._action_timestamps and (now - self._action_timestamps[0]) > 60:
            self._action_timestamps.popleft()

        if len(self._action_timestamps) >= self.max_actions_per_minute:
            console.print(
                f"[red]🛡️ RATE LIMITED: {self.max_actions_per_minute} "
                f"actions/min exceeded[/red]"
            )
            return False

        self._action_timestamps.append(now)
        return True

    def needs_approval(self, action_type: str) -> bool:
        """Check if an action type requires human approval."""
        return action_type in self.require_approval

    def request_approval(self, action: str) -> bool:
        """
        Ask the user for approval to proceed.

        Args:
            action: Description of what will happen.

        Returns:
            True if approved, False otherwise.
        """
        console.print(f"\n[bold yellow]🛡️ Approval Required:[/bold yellow] {action}")
        response = input("   Approve? (y/n): ").strip().lower()
        approved = response in ("y", "yes")

        if not approved:
            console.print("[dim]Action denied by user.[/dim]")

        return approved

    def is_dry_run(self) -> bool:
        """Check if dry-run mode is active."""
        return self.dry_run

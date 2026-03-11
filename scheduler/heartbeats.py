"""
JARVIS — scheduler/heartbeats.py
Proactive scheduled tasks — morning briefings, periodic checks, reminders
Inspired by OpenClaw's Heartbeat system
"""

import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class HeartbeatScheduler:
    """Runs proactive scheduled tasks and sends notifications."""

    def __init__(self, gateway_url: str = "http://127.0.0.1:8000",
                 telegram_token: str | None = None,
                 telegram_chat_id: int | None = None):
        self.gateway_url = gateway_url
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.scheduler = BackgroundScheduler()
        self._setup_default_heartbeats()

    def _setup_default_heartbeats(self):
        """Register the default set of heartbeat tasks."""

        # Morning briefing — every day at 8:00 AM
        self.scheduler.add_job(
            self.morning_briefing,
            trigger=CronTrigger(hour=8, minute=0),
            id="morning_briefing",
            name="Morning Briefing",
            replace_existing=True,
        )

        # System health check — every 6 hours
        self.scheduler.add_job(
            self.health_check,
            trigger=IntervalTrigger(hours=6),
            id="health_check",
            name="System Health Check",
            replace_existing=True,
        )

        # Evening summary — every day at 9:00 PM
        self.scheduler.add_job(
            self.evening_summary,
            trigger=CronTrigger(hour=21, minute=0),
            id="evening_summary",
            name="Evening Summary",
            replace_existing=True,
        )

    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        jobs = self.scheduler.get_jobs()
        console.print(f"[dim]Heartbeats: {len(jobs)} scheduled tasks active[/dim]")
        for job in jobs:
            next_run = getattr(job, 'next_run_time', None)
            console.print(f"[dim]  ♥ {job.name} — next: {next_run or 'pending'}[/dim]")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=False)
        console.print("[dim]Heartbeats: Scheduler stopped[/dim]")

    def add_heartbeat(self, func, trigger, job_id: str, name: str):
        """Add a custom heartbeat task."""
        self.scheduler.add_job(
            func, trigger=trigger,
            id=job_id, name=name,
            replace_existing=True,
        )
        console.print(f"[green]✓ Added heartbeat: {name}[/green]")

    # ─── Built-in Heartbeat Tasks ────────────

    def morning_briefing(self):
        """Morning briefing — summarize what's coming today."""
        now = datetime.now()
        message = (
            f"☀️ Good morning! It's {now.strftime('%A, %B %d, %Y')}.\n\n"
            f"Here's your morning briefing:\n"
            f"• Check your tasks for today\n"
            f"• Review any pending messages\n"
            f"• Plan your priorities\n\n"
            f"Have a productive day!"
        )
        self._send_notification(message)

    def health_check(self):
        """Periodic system health check."""
        try:
            import httpx
            response = httpx.get(f"{self.gateway_url}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check OK: {data}")
            else:
                self._send_notification(
                    f"⚠️ JARVIS health check warning: Gateway returned {response.status_code}"
                )
        except Exception as e:
            self._send_notification(f"🔴 JARVIS health check failed: {e}")
            logger.error(f"Health check failed: {e}")

    def evening_summary(self):
        """Evening summary of the day."""
        now = datetime.now()
        message = (
            f"🌙 End of day summary — {now.strftime('%A, %B %d')}\n\n"
            f"Your JARVIS session wrap-up:\n"
            f"• Review what you accomplished today\n"
            f"• Plan tomorrow's priorities\n\n"
            f"Rest well!"
        )
        self._send_notification(message)

    # ─── Notification Sending ────────────────

    def _send_notification(self, message: str):
        """Send a notification via Telegram (if configured) or log it."""
        if self.telegram_token and self.telegram_chat_id:
            try:
                import httpx
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                httpx.post(url, json={
                    "chat_id": self.telegram_chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                }, timeout=10)
                logger.info(f"Notification sent via Telegram: {message[:50]}...")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {e}")
        else:
            # Log to console as fallback
            console.print(f"\n[bold cyan]♥ Heartbeat:[/bold cyan] {message}\n")
            logger.info(f"Heartbeat (local): {message[:50]}...")

    def list_jobs(self) -> list[dict]:
        """List all scheduled jobs."""
        result = []
        for job in self.scheduler.get_jobs():
            next_run = getattr(job, 'next_run_time', None)
            result.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(next_run) if next_run else "pending",
            })
        return result

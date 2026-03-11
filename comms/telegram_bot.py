"""
JARVIS — comms/telegram_bot.py
Telegram bot — control JARVIS from your phone
"""

import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes,
)
from rich.console import Console

load_dotenv()
console = Console()

logger = logging.getLogger(__name__)

# Gateway API base URL
GATEWAY_URL = os.getenv("JARVIS_GATEWAY_URL", "http://127.0.0.1:8000")


class JarvisTelegramBot:
    """Telegram interface for JARVIS — routes messages through the Gateway."""

    def __init__(self, token: str | None = None, allowed_user_id: int | None = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.allowed_user_id = allowed_user_id or int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))

        if not self.token:
            raise ValueError(
                "Telegram bot token not found. Set TELEGRAM_BOT_TOKEN in .env"
            )

    def _is_authorized(self, user_id: int) -> bool:
        """Check if the user is authorized to use the bot."""
        if self.allowed_user_id == 0:
            return True  # No restriction set
        return user_id == self.allowed_user_id

    async def _call_gateway(self, endpoint: str, method: str = "GET",
                            json_data: dict | None = None, params: dict | None = None) -> dict:
        """Make a request to the Gateway API."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{GATEWAY_URL}{endpoint}"
            if method == "POST":
                resp = await client.post(url, json=json_data)
            else:
                resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    # ─── Command Handlers ────────────────────

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("🔒 Unauthorized.")
            return

        await update.message.reply_text(
            "◈ **JARVIS is online**\n\n"
            "Send me any message and I'll respond.\n\n"
            "Commands:\n"
            "/help — Show available commands\n"
            "/status — Check system status\n"
            "/memory — Memory statistics\n"
            "/skills — List loaded skills\n"
            "/plan <goal> — Break a goal into steps\n"
            "/killswitch — Emergency stop",
            parse_mode="Markdown",
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        if not self._is_authorized(update.effective_user.id):
            return

        await update.message.reply_text(
            "◈ **JARVIS Commands**\n\n"
            "• Just type anything — I'll chat with you\n"
            "• `/status` — System health check\n"
            "• `/memory` — Show memory stats\n"
            "• `/skills` — List all loaded skills\n"
            "• `/plan <goal>` — Create an action plan\n"
            "• `/search <query>` — Web search\n"
            "• `/sysinfo` — System statistics\n"
            "• `/killswitch` — Emergency stop\n",
            parse_mode="Markdown",
        )

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        if not self._is_authorized(update.effective_user.id):
            return

        try:
            data = await self._call_gateway("/status")
            msg = (
                f"◈ **JARVIS Status**\n\n"
                f"🟢 Online\n"
                f"🤖 Model: `{data.get('model', 'unknown')}`\n"
                f"📚 RAG docs: {data.get('memory_documents', 0)}\n"
                f"💬 Messages: {data.get('total_messages', 0)}\n"
                f"🧩 Skills: {data.get('skills_loaded', 0)}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Gateway unreachable: {e}")

    async def cmd_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /memory command."""
        if not self._is_authorized(update.effective_user.id):
            return

        try:
            data = await self._call_gateway("/memory/stats")
            msg = (
                f"◈ **Memory Stats**\n\n"
                f"📚 RAG documents: {data.get('rag_documents', 0)}\n"
                f"💬 Total messages: {data.get('total_messages', 0)}\n"
                f"📝 Current session: #{data.get('current_session', '?')}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_skills(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /skills command."""
        if not self._is_authorized(update.effective_user.id):
            return

        try:
            data = await self._call_gateway("/skills")
            skills = data.get("skills", [])

            if not skills:
                await update.message.reply_text("No skills loaded.")
                return

            msg = "◈ **Loaded Skills**\n\n"
            for s in skills:
                triggers = ", ".join(s.get("triggers", [])[:3])
                msg += f"🧩 **{s['name']}** — {s['description']}\n   Triggers: `{triggers}`\n\n"

            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /plan <goal> command."""
        if not self._is_authorized(update.effective_user.id):
            return

        goal = " ".join(context.args) if context.args else ""
        if not goal:
            await update.message.reply_text("Usage: /plan <your goal>")
            return

        await update.message.reply_text("🔄 Breaking down your goal...")

        try:
            data = await self._call_gateway("/plan", method="POST", json_data={"goal": goal})
            steps = data.get("steps", [])

            if not steps:
                await update.message.reply_text("Could not create a plan. Try rephrasing.")
                return

            msg = f"◈ **Plan: {goal}**\n\n"
            for step in steps:
                msg += f"  {step.get('step', '?')}. {step.get('action', '')}\n"

            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_killswitch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /killswitch command."""
        if not self._is_authorized(update.effective_user.id):
            return

        await update.message.reply_text("🛑 Kill switch activated. Shutting down JARVIS...")

        from safety.killswitch import kill
        kill()

    # ─── Message Handler ─────────────────────

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages — send to Gateway for processing."""
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("🔒 Unauthorized.")
            return

        user_msg = update.message.text

        try:
            data = await self._call_gateway(
                "/chat", method="POST",
                json_data={"message": user_msg}
            )
            response = data.get("response", "No response.")
            await update.message.reply_text(response)
        except httpx.ConnectError:
            await update.message.reply_text(
                "❌ JARVIS Gateway is not running.\n"
                "Start it with: `python -m gateway.run start`",
                parse_mode="Markdown",
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    # ─── Run the Bot ─────────────────────────

    def run(self):
        """Start the Telegram bot."""
        console.print("[cyan]◈ Starting JARVIS Telegram bot...[/cyan]")

        app = Application.builder().token(self.token).build()

        # Register handlers
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("status", self.cmd_status))
        app.add_handler(CommandHandler("memory", self.cmd_memory))
        app.add_handler(CommandHandler("skills", self.cmd_skills))
        app.add_handler(CommandHandler("plan", self.cmd_plan))
        app.add_handler(CommandHandler("killswitch", self.cmd_killswitch))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        console.print("[green]✓ Telegram bot is running. Press Ctrl+C to stop.[/green]")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Entry point for running the Telegram bot standalone."""
    bot = JarvisTelegramBot()
    bot.run()


if __name__ == "__main__":
    main()

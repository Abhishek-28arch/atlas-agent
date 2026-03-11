"""
JARVIS — setup/onboard.py
First-run onboarding wizard — personalizes JARVIS for the user
Inspired by OpenClaw's persona / onboarding system
"""

import os
import yaml
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

CONFIG_PATH = "config.yaml"


def run_onboarding():
    """Run the first-time setup wizard."""
    console.print(Panel(
        "[bold cyan]◈ Welcome to JARVIS Setup[/bold cyan]\n\n"
        "Let's personalize your AI assistant.\n"
        "This only takes a minute.",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()

    # Ask questions
    user_name = Prompt.ask("[bold]What's your name?[/bold]")

    assistant_name = Prompt.ask(
        "[bold]What would you like to call your assistant?[/bold]",
        default="JARVIS",
    )

    timezone = Prompt.ask(
        "[bold]Your timezone?[/bold]",
        default="Asia/Kolkata",
    )

    work_style = Prompt.ask(
        "[bold]How should I communicate?[/bold]",
        choices=["concise", "detailed", "casual", "professional"],
        default="professional",
    )

    primary_use = Prompt.ask(
        "[bold]Primary use case?[/bold]",
        choices=["coding", "productivity", "research", "automation", "general"],
        default="general",
    )

    # Telegram setup (optional)
    setup_telegram = Confirm.ask(
        "\n[bold]Set up Telegram bot?[/bold]",
        default=False,
    )

    telegram_token = ""
    telegram_user_id = ""
    if setup_telegram:
        telegram_token = Prompt.ask("  Telegram bot token")
        telegram_user_id = Prompt.ask("  Your Telegram user ID")

    # Generate personalized system prompt
    system_prompt = _generate_system_prompt(
        user_name=user_name,
        assistant_name=assistant_name,
        work_style=work_style,
        primary_use=primary_use,
    )

    # Save to config
    _save_config(
        user_name=user_name,
        assistant_name=assistant_name,
        timezone=timezone,
        work_style=work_style,
        primary_use=primary_use,
        system_prompt=system_prompt,
        telegram_token=telegram_token,
        telegram_user_id=telegram_user_id,
    )

    console.print()
    console.print(Panel(
        f"[bold green]✓ Setup complete![/bold green]\n\n"
        f"  Assistant name: [cyan]{assistant_name}[/cyan]\n"
        f"  Personalized for: [cyan]{user_name}[/cyan]\n"
        f"  Communication style: [cyan]{work_style}[/cyan]\n"
        f"  Telegram: [cyan]{'configured' if setup_telegram else 'skipped'}[/cyan]\n\n"
        f"  Start {assistant_name}: [bold]python main.py[/bold]",
        border_style="green",
        padding=(1, 2),
    ))


def _generate_system_prompt(user_name: str, assistant_name: str,
                            work_style: str, primary_use: str) -> str:
    """Generate a personalized system prompt based on user preferences."""
    style_map = {
        "concise": "Keep responses short and to the point. Use bullet points where possible.",
        "detailed": "Provide thorough, well-explained responses with examples when helpful.",
        "casual": "Be friendly and conversational, like chatting with a tech-savvy friend.",
        "professional": "Be professional, precise, and well-structured in responses.",
    }

    use_map = {
        "coding": "You specialize in software development, debugging, code review, and DevOps.",
        "productivity": "You specialize in task management, scheduling, email, and workflow optimization.",
        "research": "You specialize in research, analysis, data gathering, and summarization.",
        "automation": "You specialize in automation, scripting, file management, and system administration.",
        "general": "You are a versatile assistant capable of helping with any task.",
    }

    return (
        f"You are {assistant_name}, a personal AI assistant for {user_name}. "
        f"You run locally on their machine — no cloud, 100% private. "
        f"{style_map.get(work_style, style_map['professional'])} "
        f"{use_map.get(primary_use, use_map['general'])} "
        f"You have access to their files, can search the web, manage tasks, "
        f"and automate workflows. Always be helpful and proactive."
    )


def _save_config(user_name: str, assistant_name: str, timezone: str,
                 work_style: str, primary_use: str, system_prompt: str,
                 telegram_token: str, telegram_user_id: str):
    """Update config.yaml with onboarding answers."""
    # Load existing config
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f) or {}

    # Update persona section
    config["jarvis"] = config.get("jarvis", {})
    config["jarvis"]["name"] = assistant_name
    config["jarvis"]["user_name"] = user_name
    config["jarvis"]["timezone"] = timezone
    config["jarvis"]["work_style"] = work_style
    config["jarvis"]["primary_use"] = primary_use
    config["jarvis"]["system_prompt"] = system_prompt
    config["jarvis"]["onboarded"] = True

    # Update Telegram if provided
    if telegram_token:
        config["telegram"] = config.get("telegram", {})
        config["telegram"]["token"] = telegram_token
        config["telegram"]["allowed_user_id"] = int(telegram_user_id) if telegram_user_id.isdigit() else 0

    # Write back
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    # Also save token to .env if provided
    if telegram_token:
        env_path = ".env"
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                env_lines = f.readlines()

        # Update or add token
        updated = False
        for i, line in enumerate(env_lines):
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                env_lines[i] = f"TELEGRAM_BOT_TOKEN={telegram_token}\n"
                updated = True
            if line.startswith("TELEGRAM_ALLOWED_USER_ID="):
                env_lines[i] = f"TELEGRAM_ALLOWED_USER_ID={telegram_user_id}\n"

        if not updated:
            env_lines.append(f"TELEGRAM_BOT_TOKEN={telegram_token}\n")
            env_lines.append(f"TELEGRAM_ALLOWED_USER_ID={telegram_user_id}\n")

        with open(env_path, "w") as f:
            f.writelines(env_lines)


def needs_onboarding() -> bool:
    """Check if onboarding has been completed."""
    if not os.path.exists(CONFIG_PATH):
        return True

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f) or {}

    return not config.get("jarvis", {}).get("onboarded", False)


if __name__ == "__main__":
    run_onboarding()

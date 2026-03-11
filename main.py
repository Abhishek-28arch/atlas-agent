"""
JARVIS — main.py
Entry point — interactive CLI with Rich-formatted output
Integrates: Brain, Memory, Skills, Onboarding, Gateway
"""

import sys
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from brain.llm import JarvisLLM
from brain.router import Router
from brain.planner import TaskPlanner
from memory.rag import RAGMemory
from memory.history import ConversationHistory
from memory.indexer import FileIndexer
from skills.loader import SkillsLoader
from skills.creator import SkillCreator
from safety.logger import ActionLogger

console = Console()


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        console.print(f"[yellow]⚠ Config not found at {config_path}, using defaults[/yellow]")
        return {}


def print_banner(config: dict):
    """Print the JARVIS startup banner."""
    jarvis_config = config.get("jarvis", {})
    name = jarvis_config.get("name", "JARVIS")
    user_name = jarvis_config.get("user_name", "")

    banner = Text()
    banner.append(f"◈ {name} ", style="bold cyan")
    banner.append("v0.1.0\n", style="dim")
    banner.append("  Just A Rather Very Intelligent System\n", style="italic dim")
    banner.append("  Running locally • 100% private • ₹0/month", style="dim")
    if user_name:
        banner.append(f"\n  Personalized for {user_name}", style="dim")

    console.print(Panel(
        banner,
        border_style="cyan",
        padding=(1, 2),
    ))


def print_help():
    """Print available commands."""
    console.print("\n[bold cyan]◈ Commands:[/bold cyan]")
    console.print("  [bold]/help[/bold]              — Show this help message")
    console.print("  [bold]/memory[/bold]            — Show memory stats")
    console.print("  [bold]/index[/bold] <path>      — Index a file or directory into memory")
    console.print("  [bold]/plan[/bold] <goal>       — Break a goal into steps")
    console.print("  [bold]/skills[/bold]            — List loaded skills")
    console.print("  [bold]/create-skill[/bold] <desc> — AI-generate a new skill")
    console.print("  [bold]/history[/bold]           — Show conversation history")
    console.print("  [bold]/clear[/bold]             — Clear conversation context")
    console.print("  [bold]/gateway[/bold]           — Start the Gateway server")
    console.print("  [bold]/telegram[/bold]          — Start the Telegram bot")
    console.print("  [bold]/quit[/bold]              — Exit JARVIS")
    console.print()


def main():
    """Main entry point — interactive CLI loop."""
    # ─── Check Onboarding ────────────────────
    from setup.onboard import needs_onboarding, run_onboarding
    if needs_onboarding():
        run_onboarding()

    config = load_config()
    model_config = config.get("models", {})
    memory_config = config.get("memory", {})
    jarvis_config = config.get("jarvis", {})

    # ─── Print Banner ────────────────────────
    print_banner(config)
    console.print()

    # ─── Initialize Components ───────────────
    try:
        console.print("[dim]Initializing brain...[/dim]")
        llm = JarvisLLM(
            model=model_config.get("primary", "qwen3.5:4b"),
            host=model_config.get("ollama_host", "http://localhost:11434"),
        )

        # Use personalized system prompt if available
        custom_prompt = jarvis_config.get("system_prompt")
        if custom_prompt:
            llm.SYSTEM_PROMPT = custom_prompt

        console.print("[dim]Initializing memory...[/dim]")
        rag = RAGMemory(
            db_path=memory_config.get("rag_db_path", "./data/rag_db"),
            chunk_size=memory_config.get("chunk_size", 500),
            chunk_overlap=memory_config.get("chunk_overlap", 50),
        )

        history = ConversationHistory(
            db_path=memory_config.get("history_db", "./data/history.db"),
        )

        indexer = FileIndexer(rag)
        router = Router(llm)
        planner = TaskPlanner(llm)

        logger = ActionLogger(
            config.get("safety", {}).get("log_file", "./data/logs/actions.log")
        )

        # ─── Skills System ───────────────────
        console.print("[dim]Loading skills...[/dim]")
        skills_loader = SkillsLoader(skills_dir="skills")
        skills_loader.load_all()
        skills_loader.start_watcher()

        skill_creator = SkillCreator(skills_dir="skills", llm=llm)

        # Auto-index knowledge directory
        knowledge_dir = memory_config.get("knowledge_dir", "./data/knowledge")
        indexer.index_directory(knowledge_dir)

        console.print("[green]✓ JARVIS is ready[/green]")
        console.print("[dim]Type /help for commands, or just start talking.[/dim]\n")

    except ConnectionError:
        console.print("[red]✗ Cannot start JARVIS — Ollama is not running.[/red]")
        console.print("[red]  Start Ollama first: ollama serve[/red]")
        sys.exit(1)

    # ─── Interactive Loop ────────────────────
    while True:
        try:
            name = jarvis_config.get("name", "JARVIS")
            user_input = console.input("[bold cyan]◈ You:[/bold cyan] ").strip()

            if not user_input:
                continue

            # ─── Slash Commands ───────────────
            if user_input.startswith("/"):
                handle_command(
                    user_input, llm, rag, history, indexer,
                    planner, logger, skills_loader, skill_creator, config,
                )
                continue

            # ─── Check Skills First ───────────
            skill = skills_loader.find_skill(user_input)
            if skill:
                console.print(f"[dim]Using skill: {skill.name}[/dim]")
                result = skills_loader.execute_skill(skill.name, user_input)
                console.print(f"[bold green]◈ {name}:[/bold green] {result}\n")
                history.save_message("user", user_input)
                history.save_message("assistant", result)
                logger.log("skill", f"Executed: {skill.name}")
                continue

            # ─── Route and Respond ────────────
            intent = router.classify(user_input)
            logger.log("route", f"Intent: {intent} | Input: {user_input[:100]}")

            if intent == "memory_query":
                handle_memory_query(user_input, llm, rag, history, logger, name)
            elif intent == "memory_add":
                handle_memory_add(user_input, rag, history, logger, name)
            elif intent == "plan":
                handle_plan(user_input, planner, history, logger)
            else:
                handle_chat(user_input, llm, rag, history, logger, name)

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type /quit to exit.[/dim]")
        except EOFError:
            break

    history.end_session()
    console.print("\n[dim]Session ended. Goodbye.[/dim]")


def handle_command(command, llm, rag, history, indexer, planner, logger,
                   skills_loader, skill_creator, config):
    """Handle slash commands."""
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    name = config.get("jarvis", {}).get("name", "JARVIS")

    if cmd == "/help":
        print_help()

    elif cmd == "/memory":
        console.print(f"\n[cyan]◈ Memory Stats[/cyan]")
        console.print(f"  RAG documents: {rag.count()}")
        console.print(f"  Total messages: {history.get_total_messages()}")
        console.print(f"  Current session: #{history.session_id}\n")

    elif cmd == "/index":
        if not arg:
            console.print("[yellow]Usage: /index <file_or_directory_path>[/yellow]")
            return
        import os
        path = os.path.expanduser(arg)
        if os.path.isdir(path):
            indexer.index_directory(path)
        elif os.path.isfile(path):
            rag.add_document(path)
        else:
            console.print(f"[red]✗ Path not found: {path}[/red]")
        logger.log("rag_index", f"Indexed: {arg}")

    elif cmd == "/plan":
        if not arg:
            console.print("[yellow]Usage: /plan <your goal>[/yellow]")
            return
        handle_plan(arg, planner, history, logger)

    elif cmd == "/skills":
        skills = skills_loader.list_skills()
        if not skills:
            console.print("[dim]No skills loaded.[/dim]\n")
            return
        console.print("\n[cyan]◈ Loaded Skills[/cyan]")
        for s in skills:
            triggers = ", ".join(s["triggers"][:3])
            console.print(f"  🧩 [bold]{s['name']}[/bold] — {s['description']}")
            console.print(f"     Triggers: [dim]{triggers}[/dim]")
        console.print()

    elif cmd == "/create-skill":
        if not arg:
            console.print("[yellow]Usage: /create-skill <description of what the skill should do>[/yellow]")
            return
        console.print("[dim]Generating skill with AI...[/dim]")
        filepath = skill_creator.create_from_llm(arg)
        console.print(f"[green]✓ Skill created: {filepath}[/green]")
        console.print("[dim]Skill will be auto-loaded by the file watcher.[/dim]\n")

    elif cmd == "/history":
        messages = history.get_recent(20)
        if not messages:
            console.print("[dim]No messages in this session yet.[/dim]")
            return
        console.print(f"\n[cyan]◈ Recent History (Session #{history.session_id})[/cyan]")
        for msg in messages:
            role_style = "bold cyan" if msg["role"] == "user" else "bold green"
            label = "You" if msg["role"] == "user" else name
            console.print(f"  [{role_style}]{label}:[/{role_style}] {msg['content'][:100]}")
        console.print()

    elif cmd == "/clear":
        history.end_session()
        history.session_id = history._create_session()
        console.print("[dim]Context cleared. New session started.[/dim]\n")

    elif cmd == "/gateway":
        console.print("[cyan]◈ Starting Gateway server...[/cyan]")
        console.print("[dim]Use Ctrl+C to stop[/dim]\n")
        import os
        os.system("uvicorn gateway.server:app --host 127.0.0.1 --port 8000 --reload")

    elif cmd == "/telegram":
        try:
            from comms.telegram_bot import JarvisTelegramBot
            bot = JarvisTelegramBot()
            bot.run()
        except ValueError as e:
            console.print(f"[red]✗ {e}[/red]")
            console.print("[dim]Set TELEGRAM_BOT_TOKEN in .env or run onboarding again.[/dim]")

    elif cmd in ("/quit", "/exit"):
        history.end_session()
        console.print("\n[dim]Session ended. Goodbye.[/dim]")
        sys.exit(0)

    else:
        console.print(f"[yellow]Unknown command: {cmd}. Type /help for options.[/yellow]")


def handle_chat(user_input, llm, rag, history, logger, name="JARVIS"):
    """Handle general chat with optional RAG context."""
    history.save_message("user", user_input)

    conversation = history.get_recent(10)
    if conversation:
        conversation = conversation[:-1]

    rag_context = rag.get_context(user_input)

    system_prompt = llm.SYSTEM_PROMPT
    if rag_context:
        system_prompt += (
            f"\n\nRelevant context from the user's documents:\n"
            f"---\n{rag_context}\n---\n"
            f"Use this context when relevant."
        )

    console.print(f"[bold green]◈ {name}:[/bold green] ", end="")
    full_response = ""
    for chunk in llm.stream_chat(user_input, conversation=conversation, system_prompt=system_prompt):
        console.print(chunk, end="", highlight=False)
        full_response += chunk
    console.print("\n")

    history.save_message("assistant", full_response)
    logger.log("llm_chat", f"Query: {user_input[:80]}")


def handle_memory_query(user_input, llm, rag, history, logger, name="JARVIS"):
    """Handle memory search queries."""
    history.save_message("user", user_input)

    results = rag.query(user_input)
    if not results:
        response = "I don't have any relevant documents in my memory. Add files with `/index <path>`."
        console.print(f"[bold green]◈ {name}:[/bold green] {response}\n")
        history.save_message("assistant", response)
        return

    context = rag.get_context(user_input)
    synthesis_prompt = (
        f"The user asked: {user_input}\n\n"
        f"Relevant excerpts:\n{context}\n\n"
        f"Provide a helpful answer based on these documents."
    )

    console.print(f"[bold green]◈ {name}:[/bold green] ", end="")
    full_response = ""
    for chunk in llm.stream_chat(synthesis_prompt):
        console.print(chunk, end="", highlight=False)
        full_response += chunk
    console.print("\n")

    history.save_message("assistant", full_response)
    logger.log("rag_query", f"Query: {user_input[:80]}")


def handle_memory_add(user_input, rag, history, logger, name="JARVIS"):
    """Handle requests to save information to memory."""
    history.save_message("user", user_input)
    rag.add_text(user_input, source="user_note")

    response = "Got it — I've saved that to my memory."
    console.print(f"[bold green]◈ {name}:[/bold green] {response}\n")
    history.save_message("assistant", response)
    logger.log("rag_add", f"Added user note: {user_input[:80]}")


def handle_plan(goal, planner, history, logger):
    """Handle task planning requests."""
    history.save_message("user", f"Plan: {goal}")

    console.print("[dim]Breaking down your goal...[/dim]")
    steps = planner.decompose(goal)

    if steps:
        planner.display_plan(steps)
        history.save_message(
            "assistant",
            f"Plan: {len(steps)} steps — " +
            "; ".join(s["action"] for s in steps[:5])
        )
    else:
        console.print("[yellow]Could not create a plan. Try rephrasing your goal.[/yellow]\n")

    logger.log("plan", f"Goal: {goal[:80]} | Steps: {len(steps)}")


if __name__ == "__main__":
    main()

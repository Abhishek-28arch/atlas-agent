"""
JARVIS — skills/loader.py
Skills system — scans, loads, registers, and hot-reloads skill modules
"""

import os
import importlib
import importlib.util
import threading
from typing import Callable
from rich.console import Console

console = Console()


class Skill:
    """Represents a loaded skill module."""

    def __init__(self, name: str, description: str, triggers: list[str],
                 run_fn: Callable, schedule_fn: Callable | None = None,
                 filepath: str = ""):
        self.name = name
        self.description = description
        self.triggers = triggers
        self.run = run_fn
        self.schedule = schedule_fn
        self.filepath = filepath

    def matches(self, text: str) -> bool:
        """Check if user input matches any of this skill's trigger keywords."""
        text_lower = text.lower()
        return any(trigger.lower() in text_lower for trigger in self.triggers)


class SkillsLoader:
    """Loads and manages skill modules from the skills/ directory."""

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = os.path.abspath(skills_dir)
        self.skills: dict[str, Skill] = {}
        self._watcher_thread = None

    def load_all(self):
        """Scan the skills directory and load all valid skill modules."""
        if not os.path.isdir(self.skills_dir):
            os.makedirs(self.skills_dir, exist_ok=True)
            console.print(f"[dim]Skills: Created {self.skills_dir}[/dim]")
            return

        loaded = 0
        blocked = 0
        for filename in sorted(os.listdir(self.skills_dir)):
            if (filename.endswith(".py")
                    and not filename.startswith("_")
                    and filename not in ("loader.py", "creator.py")):
                filepath = os.path.join(self.skills_dir, filename)

                # ── Security scan before loading ──
                if not self._security_check(filepath):
                    blocked += 1
                    continue

                try:
                    self._load_skill_file(filepath)
                    loaded += 1
                except Exception as e:
                    console.print(f"[red]✗ Failed to load skill {filename}: {e}[/red]")

        console.print(f"[dim]Skills: {loaded} loaded, {blocked} blocked by scanner[/dim]")

    def _security_check(self, filepath: str) -> bool:
        """Run security scanner on a skill file before loading."""
        try:
            from safety.skill_scanner import scan_file
            result = scan_file(filepath)

            if result.critical > 0:
                filename = os.path.basename(filepath)
                console.print(
                    f"[red]🛡️ BLOCKED: {filename} has {result.critical} "
                    f"critical security finding(s)[/red]"
                )
                for f in result.findings:
                    if f.severity == "critical":
                        console.print(f"[red]   • {f.message}: {f.evidence}[/red]")
                return False

            if result.warn > 0:
                filename = os.path.basename(filepath)
                console.print(
                    f"[yellow]⚠ {filename}: {result.warn} warning(s) "
                    f"(loading anyway)[/yellow]"
                )

            return True

        except ImportError:
            return True  # Scanner not available, proceed

    def _load_skill_file(self, filepath: str):
        """Load a single skill module from a Python file."""
        filename = os.path.basename(filepath)
        module_name = filename[:-3]  # strip .py

        spec = importlib.util.spec_from_file_location(f"skills.{module_name}", filepath)
        if spec is None or spec.loader is None:
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Validate required attributes
        name = getattr(module, "SKILL_NAME", module_name)
        description = getattr(module, "SKILL_DESCRIPTION", "No description")
        triggers = getattr(module, "SKILL_TRIGGERS", [])
        run_fn = getattr(module, "run", None)

        if run_fn is None:
            console.print(f"[yellow]⚠ Skill {filename} has no run() function, skipping[/yellow]")
            return

        schedule_fn = getattr(module, "schedule", None)

        skill = Skill(
            name=name,
            description=description,
            triggers=triggers,
            run_fn=run_fn,
            schedule_fn=schedule_fn,
            filepath=filepath,
        )

        self.skills[name] = skill
        console.print(f"[dim]  ✓ {name}: {description}[/dim]")

    def reload_skill(self, filepath: str):
        """Reload a single skill file (used by hot-reload watcher)."""
        filename = os.path.basename(filepath)
        module_name = filename[:-3]

        # Remove old version if exists
        for name, skill in list(self.skills.items()):
            if skill.filepath == filepath:
                del self.skills[name]
                break

        try:
            self._load_skill_file(filepath)
            console.print(f"[green]♻ Hot-reloaded skill: {module_name}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to reload {module_name}: {e}[/red]")

    def find_skill(self, user_input: str) -> Skill | None:
        """Find a skill that matches the user's input."""
        for skill in self.skills.values():
            if skill.matches(user_input):
                return skill
        return None

    def execute_skill(self, skill_name: str, user_input: str, context: dict | None = None) -> str:
        """Execute a skill by name."""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Skill '{skill_name}' not found."

        try:
            result = skill.run(user_input, context or {})
            return result
        except Exception as e:
            return f"Skill '{skill_name}' failed: {e}"

    def list_skills(self) -> list[dict]:
        """Return a list of all loaded skills and their info."""
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "triggers": skill.triggers,
            }
            for skill in self.skills.values()
        ]

    def start_watcher(self):
        """Start watching the skills directory for file changes (hot-reload)."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class SkillFileHandler(FileSystemEventHandler):
                def __init__(self, loader):
                    self.loader = loader

                def on_modified(self, event):
                    if event.src_path.endswith(".py") and not event.is_directory:
                        self.loader.reload_skill(event.src_path)

                def on_created(self, event):
                    if event.src_path.endswith(".py") and not event.is_directory:
                        self.loader.reload_skill(event.src_path)

            observer = Observer()
            observer.schedule(SkillFileHandler(self), self.skills_dir, recursive=False)
            observer.daemon = True
            observer.start()
            console.print("[dim]Skills: File watcher active (hot-reload enabled)[/dim]")

        except ImportError:
            console.print("[yellow]⚠ watchdog not installed — hot-reload disabled[/yellow]")

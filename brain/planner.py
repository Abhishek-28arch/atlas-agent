"""
JARVIS — brain/planner.py
Task decomposition engine — breaks goals into executable steps
"""

import json
from brain.llm import JarvisLLM
from rich.console import Console

console = Console()


class TaskPlanner:
    """Breaks high-level goals into ordered, executable steps using the LLM."""

    PLANNER_PROMPT = """You are a task planner. Given a user's goal, break it down into clear, ordered, actionable steps.

Rules:
- Each step should be a single, concrete action
- Keep steps concise and specific
- Return your response as a JSON array of objects
- Each object must have: "step" (number), "action" (description), "type" (one of: "search", "read", "write", "execute", "communicate", "analyze")

Example output:
[
    {"step": 1, "action": "Search for Python developer jobs on LinkedIn", "type": "search"},
    {"step": 2, "action": "Read each job description", "type": "read"},
    {"step": 3, "action": "Customize resume for top matches", "type": "write"}
]

Return ONLY the JSON array, no other text."""

    def __init__(self, llm: JarvisLLM):
        self.llm = llm

    def decompose(self, goal: str) -> list[dict]:
        """
        Break a high-level goal into ordered steps.

        Args:
            goal: The user's goal or objective.

        Returns:
            List of step dictionaries with step number, action, and type.
        """
        response = self.llm.chat(
            user_message=f"Break down this goal into steps:\n\n{goal}",
            system_prompt=self.PLANNER_PROMPT,
        )

        return self._parse_steps(response)

    def _parse_steps(self, response: str) -> list[dict]:
        """Parse the LLM response into structured steps."""
        try:
            # Try to extract JSON from the response
            text = response.strip()

            # Handle cases where LLM wraps JSON in markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            steps = json.loads(text)

            if isinstance(steps, list):
                # Add status field to each step
                for step in steps:
                    step["status"] = "pending"
                return steps

        except (json.JSONDecodeError, IndexError):
            console.print("[yellow]⚠ Could not parse plan as JSON, returning raw steps[/yellow]")

        # Fallback: parse numbered lines
        steps = []
        for i, line in enumerate(response.strip().split("\n"), 1):
            line = line.strip()
            if line and not line.startswith("{") and not line.startswith("["):
                # Strip leading numbers/bullets
                for prefix in ["- ", "* ", f"{i}. ", f"{i}) "]:
                    if line.startswith(prefix):
                        line = line[len(prefix):]
                        break
                steps.append({
                    "step": i,
                    "action": line,
                    "type": "general",
                    "status": "pending",
                })

        return steps

    def display_plan(self, steps: list[dict]):
        """Pretty print a plan to the console."""
        console.print("\n[bold cyan]◈ Plan:[/bold cyan]")
        for step in steps:
            status_icon = {
                "pending": "○",
                "in_progress": "◔",
                "done": "●",
                "failed": "✗",
            }.get(step.get("status", "pending"), "○")

            step_type = step.get("type", "general")
            console.print(
                f"  [dim]{status_icon}[/dim] "
                f"[bold]{step['step']}.[/bold] {step['action']} "
                f"[dim]({step_type})[/dim]"
            )
        console.print()

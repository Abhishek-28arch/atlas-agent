"""
JARVIS — skills/creator.py
Lets JARVIS write new skill files via LLM
"""

import os
from rich.console import Console

console = Console()

SKILL_TEMPLATE = '''"""
JARVIS Skill — {name}
{description}
"""

SKILL_NAME = "{skill_id}"
SKILL_DESCRIPTION = "{description}"
SKILL_TRIGGERS = {triggers}


def run(user_input: str, context: dict) -> str:
    """Execute the {name} skill."""
    # TODO: Implement your skill logic here
    return "Skill '{name}' executed successfully."
'''


class SkillCreator:
    """Creates new skill files, either from LLM or from templates."""

    def __init__(self, skills_dir: str = "skills", llm=None):
        self.skills_dir = os.path.abspath(skills_dir)
        self.llm = llm

    def create_from_template(self, name: str, description: str, triggers: list[str]) -> str:
        """
        Create a new skill file from the basic template.

        Args:
            name: Human-readable skill name.
            description: What the skill does.
            triggers: Keywords that activate this skill.

        Returns:
            Path to the created skill file.
        """
        skill_id = name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{skill_id}.py"
        filepath = os.path.join(self.skills_dir, filename)

        if os.path.exists(filepath):
            return f"⚠ Skill file already exists: {filename}"

        content = SKILL_TEMPLATE.format(
            name=name,
            skill_id=skill_id,
            description=description,
            triggers=triggers,
        )

        os.makedirs(self.skills_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        console.print(f"[green]✓ Created skill: {filepath}[/green]")
        return filepath

    def create_from_llm(self, user_request: str) -> str:
        """
        Use the LLM to generate a complete skill file from a natural language request.

        Args:
            user_request: What the user wants the skill to do.

        Returns:
            Path to the created skill file, or error message.
        """
        if not self.llm:
            return "❌ LLM not available for skill generation."

        prompt = f"""Write a Python skill module for JARVIS. The skill should:
{user_request}

The file must follow this exact structure:
- SKILL_NAME = "skill_id" (lowercase, underscores)
- SKILL_DESCRIPTION = "one line description"
- SKILL_TRIGGERS = ["keyword1", "keyword2"] (words that activate this skill)
- def run(user_input: str, context: dict) -> str: (main function, returns a string result)
- Optionally: def schedule() -> dict: (for scheduled tasks)

Rules:
- Return ONLY the Python code, no explanations
- Include necessary imports
- Handle errors gracefully with try/except
- Return helpful error messages if dependencies are missing
- Keep it simple and focused on one thing"""

        response = self.llm.chat(
            user_message=prompt,
            system_prompt="You are a Python skill generator. Output ONLY valid Python code, nothing else.",
        )

        # Extract code from response
        code = self._extract_code(response)
        if not code:
            return "❌ Could not generate valid skill code."

        # Try to extract the skill name from the generated code
        skill_id = "custom_skill"
        for line in code.split("\n"):
            if line.strip().startswith("SKILL_NAME"):
                try:
                    skill_id = line.split("=")[1].strip().strip('"').strip("'")
                except (IndexError, ValueError):
                    pass
                break

        filename = f"{skill_id}.py"
        filepath = os.path.join(self.skills_dir, filename)

        # Safety: don't overwrite existing files
        if os.path.exists(filepath):
            import time
            filepath = os.path.join(self.skills_dir, f"{skill_id}_{int(time.time())}.py")

        os.makedirs(self.skills_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        console.print(f"[green]✓ AI-generated skill: {filepath}[/green]")
        return filepath

    def _extract_code(self, response: str) -> str:
        """Extract Python code from an LLM response."""
        text = response.strip()

        # Strip markdown code blocks
        if "```python" in text:
            text = text.split("```python")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Validate it looks like Python
        if "def run(" in text and "SKILL_NAME" in text:
            return text

        return ""

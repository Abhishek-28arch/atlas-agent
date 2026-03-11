"""
JARVIS — brain/llm.py
Ollama LLM wrapper for Qwen 3.5:2B
Handles think-tag stripping for Qwen 3.5 thinking models
"""

import re
import ollama
from rich.console import Console

console = Console()

# Regex to strip <think>...</think> blocks from Qwen 3.5 responses
THINK_TAG_RE = re.compile(r'<think>.*?</think>\s*', re.DOTALL)


class JarvisLLM:
    """Wrapper around the Ollama Python client for local LLM inference."""

    SYSTEM_PROMPT = (
        "You are JARVIS, a highly capable AI assistant that runs locally. "
        "You are helpful, precise, and concise. You assist with tasks, answer "
        "questions, manage files, and automate workflows. Always respond in a "
        "professional and friendly tone."
    )

    def __init__(self, model: str = "qwen3.5:2b", host: str = "http://localhost:11434"):
        """
        Initialize the LLM client.

        Args:
            model: Ollama model name to use.
            host: Ollama server address.
        """
        self.model = model
        self.client = ollama.Client(host=host)
        self._verify_connection()

    def _verify_connection(self):
        """Check that Ollama is running and the model is available."""
        try:
            models = self.client.list()
            model_names = [m.model for m in models.models]
            if not any(self.model in name for name in model_names):
                console.print(
                    f"[yellow]⚠ Model '{self.model}' not found locally. "
                    f"Available: {model_names}[/yellow]"
                )
                console.print(
                    f"[yellow]  Run: ollama pull {self.model}[/yellow]"
                )
        except Exception as e:
            console.print(
                f"[red]✗ Cannot connect to Ollama at {self.client._client._base_url}: {e}[/red]"
            )
            console.print(
                "[red]  Make sure Ollama is running: ollama serve[/red]"
            )
            raise ConnectionError(f"Ollama not reachable: {e}")

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        """Remove <think>...</think> blocks from Qwen 3.5 responses."""
        return THINK_TAG_RE.sub('', text).strip()

    def chat(self, user_message: str, conversation: list[dict] | None = None,
             system_prompt: str | None = None) -> str:
        """
        Send a message and get a complete response.

        Args:
            user_message: The user's input text.
            conversation: Optional list of prior messages for context.
            system_prompt: Override the default system prompt.

        Returns:
            The assistant's response text (think tags stripped).
        """
        messages = self._build_messages(user_message, conversation, system_prompt)

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
            )
            return self._strip_think_tags(response.message.content)
        except Exception as e:
            console.print(f"[red]✗ LLM error: {e}[/red]")
            return f"Error: Could not get a response from {self.model}."

    def stream_chat(self, user_message: str, conversation: list[dict] | None = None,
                    system_prompt: str | None = None):
        """
        Send a message and stream the response token by token.
        Buffers and strips <think>...</think> blocks before yielding.

        Args:
            user_message: The user's input text.
            conversation: Optional list of prior messages for context.
            system_prompt: Override the default system prompt.

        Yields:
            Response text chunks (after think block is complete).
        """
        messages = self._build_messages(user_message, conversation, system_prompt)

        try:
            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True,
            )

            in_think = False
            buffer = ""

            for chunk in stream:
                token = chunk.message.content or ""

                if not token:
                    continue

                buffer += token

                # Detect start of think block
                if "<think>" in buffer and not in_think:
                    in_think = True
                    # Yield anything before <think>
                    before = buffer.split("<think>")[0]
                    if before.strip():
                        yield before
                    buffer = buffer[buffer.index("<think>"):]

                # Detect end of think block
                if in_think and "</think>" in buffer:
                    in_think = False
                    after = buffer.split("</think>", 1)[1]
                    buffer = after
                    # Yield any content after </think>
                    if buffer.strip():
                        yield buffer
                        buffer = ""
                    continue

                # If not in think block, yield tokens normally
                if not in_think:
                    yield token
                    buffer = ""

        except Exception as e:
            console.print(f"[red]✗ LLM streaming error: {e}[/red]")
            yield f"Error: {e}"

    def _build_messages(self, user_message: str, conversation: list[dict] | None = None,
                        system_prompt: str | None = None) -> list[dict]:
        """Build the messages list with system prompt, history, and user message."""
        messages = [
            {"role": "system", "content": system_prompt or self.SYSTEM_PROMPT}
        ]

        if conversation:
            messages.extend(conversation)

        messages.append({"role": "user", "content": user_message})
        return messages

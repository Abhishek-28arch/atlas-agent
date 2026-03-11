"""
JARVIS — brain/router.py
Intent classification — fast keyword-based routing (no LLM call)
"""

import re
from rich.console import Console

console = Console()


class Router:
    """Classifies user intent using keyword matching — zero latency."""

    VALID_INTENTS = {"chat", "memory_query", "memory_add", "plan", "action", "skill"}

    # Keyword patterns for each intent
    PATTERNS = {
        "memory_query": [
            r"\bremember\b.*\b(about|what|when|where)\b",
            r"\bwhat (did|does) .+ (say|mention|contain)\b",
            r"\bsearch (my|the) (memory|notes|documents?)\b",
            r"\brecall\b", r"\bfind in (my|the)\b",
            r"\bwhat do you know about\b",
        ],
        "memory_add": [
            r"\bremember (that|this)\b",
            r"\bsave (this|that)\b",
            r"\bnote (that|this|down)\b",
            r"\bstore (this|that)\b",
            r"\bkeep (this|that) in mind\b",
            r"\badd (this|that) to (memory|notes)\b",
        ],
        "plan": [
            r"\bplan (to|for|how)\b",
            r"\bbreak(down| down| it down)\b",
            r"\bsteps? (to|for)\b",
            r"\bhow (do|can|should) (i|we)\b",
            r"\bcreate a (plan|roadmap|strategy)\b",
            r"\bdecompose\b", r"\bactionable\b",
        ],
        "action": [
            r"\borganize\b", r"\bclean up\b", r"\bsort\b",
            r"\bdelete\b", r"\bmove\b", r"\bcopy\b", r"\brename\b",
            r"\brun (the|a|this)?\s*(script|command)\b",
            r"\bexecute\b", r"\binstall\b",
        ],
    }

    def __init__(self, llm=None):
        """Initialize router. LLM param kept for backward compatibility but not used."""
        self._compiled = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in self.PATTERNS.items()
        }

    def classify(self, user_message: str) -> str:
        """
        Classify user intent using keyword matching.
        Zero latency — no LLM call needed.

        Args:
            user_message: The raw user input.

        Returns:
            One of: "chat", "memory_query", "memory_add", "plan", "action", "skill"
        """
        text = user_message.strip()

        # Check each intent's patterns
        for intent, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.search(text):
                    return intent

        # Default to chat
        return "chat"

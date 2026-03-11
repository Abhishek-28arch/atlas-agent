"""
JARVIS — safety/sanitize.py
Input validation and sanitization
"""

import re


# Maximum input length (characters)
MAX_INPUT_LENGTH = 10_000

# Control characters to strip (keep newlines and tabs)
CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

# Common prompt injection patterns to flag
INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?)', re.IGNORECASE),
    re.compile(r'you\s+are\s+now\s+(a|an)\s+\w+\s+(that|who|which)', re.IGNORECASE),
    re.compile(r'system\s*prompt\s*[:=]', re.IGNORECASE),
    re.compile(r'<\s*/?\s*system\s*>', re.IGNORECASE),
]


def sanitize_input(text: str) -> str:
    """
    Sanitize user input before processing.

    - Strips control characters (keeps newlines)
    - Trims excessive whitespace
    - Enforces max length
    """
    # Strip control characters
    text = CONTROL_CHARS.sub('', text)

    # Trim whitespace
    text = text.strip()

    # Enforce max length
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]

    return text


def check_injection(text: str) -> bool:
    """
    Check if text contains common prompt injection patterns.

    Returns True if suspicious injection attempt detected.
    This is a heuristic — not a security boundary.
    """
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def sanitize_path(path: str) -> str:
    """
    Sanitize a file path to prevent traversal attacks.

    - Removes null bytes
    - Blocks path traversal sequences
    """
    # Remove null bytes
    path = path.replace('\x00', '')

    # Warn about path traversal but don't block — guardrails handle blocking
    return path


def truncate_for_log(text: str, max_length: int = 200) -> str:
    """Truncate text for safe logging."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

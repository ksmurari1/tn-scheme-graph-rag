from __future__ import annotations
import re

def check_question(question: str) -> tuple[bool, str]:
    """Lightweight input guardrail; not a substitute for full moderation/evaluation."""
    if not question or not question.strip():
        return False, "Please enter a question about a government scheme."
    if len(question) > 1500:
        return False, "Please shorten your question to 1,500 characters or fewer."
    suspicious = [
        r"ignore (all )?(previous|prior) instructions",
        r"reveal (the )?(system prompt|api key|secret)",
        r"\b(drop|delete|destroy)\s+(all\s+)?(nodes|database|data)\b",
    ]
    if any(re.search(pattern, question, flags=re.I) for pattern in suspicious):
        return False, "I can help with government scheme information, but I can't follow requests to reveal secrets or modify the knowledge database."
    return True, ""

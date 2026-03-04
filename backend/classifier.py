"""
classifier.py — Rule/keyword-based query intent classifier for ZX Bank Assistant
"""

import re
import logger

# ── Pattern lists ────────────────────────────────────────────────────────────

ADVERSARIAL_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"you are now",
    r"pretend you are",
    r"\bdan\b",
    r"jailbreak",
    r"forget your rules",
    r"forget (all )?previous",
    r"bypass your",
    r"override (your )?(instructions|rules|system|prompt)",
    r"act as (an? )?(unrestricted|unfiltered|evil|hacked)",
    r"reveal (your )?system prompt",
    r"reveal (all )?customer (data|information|accounts?)",
    r"another customer('s)? (account|data|balance|information)",
    r"transfer funds? (without|bypass)",
    r"disable (your )?(safety|filter|restriction)",
]

ESCALATION_KEYWORDS = [
    r"\bhuman\b",
    r"\bagent\b",
    r"\brepresentative\b",
    r"\bcall me\b",
    r"speak to (a|an)? ?(person|someone|human|agent|representative)",
    r"talk to (a|an)? ?(person|someone|human|agent|representative)",
    r"connect me (to|with) (a|an)? ?(person|human|agent|representative)",
    r"i need (a human|a person|human help|to speak to someone)",
    r"escalate",
]

SMALL_TALK_KEYWORDS = [
    r"\bhello\b",
    r"\bhi\b",
    r"\bhey\b",
    r"how are you",
    r"what can you do",
    r"what do you do",
    r"who are you",
    r"tell me a joke",
    r"\bthanks\b",
    r"\bthank you\b",
    r"\bbye\b",
    r"\bgoodbye\b",
    r"\bhelp\b$",         # just "help" alone
    r"^help me?$",
    r"good (morning|afternoon|evening|night)",
]


def _matches(text: str, patterns: list[str]) -> str | None:
    """Return the first matching pattern string, or None."""
    lowered = text.lower().strip()
    for pattern in patterns:
        if re.search(pattern, lowered):
            return pattern
    return None


def classify(query: str) -> tuple[str, str | None]:
    """
    Classify a query into one of:
      ADVERSARIAL, ESCALATION, SMALL_TALK, DOCUMENT_QUERY

    Returns (intent, matched_pattern_or_None)
    """
    # Priority order: ADVERSARIAL → ESCALATION → SMALL_TALK → DOCUMENT_QUERY
    match = _matches(query, ADVERSARIAL_PATTERNS)
    if match:
        logger.log_intent("ADVERSARIAL")
        logger.log_adversarial(match)
        return "ADVERSARIAL", match

    match = _matches(query, ESCALATION_KEYWORDS)
    if match:
        logger.log_intent("ESCALATION")
        return "ESCALATION", match

    match = _matches(query, SMALL_TALK_KEYWORDS)
    if match:
        logger.log_intent("SMALL_TALK")
        return "SMALL_TALK", match

    logger.log_intent("DOCUMENT_QUERY")
    return "DOCUMENT_QUERY", None

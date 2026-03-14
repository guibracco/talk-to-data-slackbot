"""
Output guardrails: PII detection and redaction.

Receives the Reasoner's response as text and redacts common PII patterns
(email, phone) so no PII is exposed before formatting or posting.
"""

import re
from typing import Pattern

REDACTED_PLACEHOLDER = "[REDACTED]"

# (pattern, replacement) for PII redaction. Replacement is the placeholder.
_PII_PATTERNS: list[tuple[Pattern[str], str]] = [
    # Email: local@domain.tld
    (
        re.compile(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            re.IGNORECASE,
        ),
        REDACTED_PLACEHOLDER,
    ),
    # Phone: international (+1 555 123 4567), US (555) 123-4567, 555-123-4567, 5551234567
    # Lookbehind/lookahead: not after digit (avoids decimals); not before digit (word boundary).
    (
        re.compile(
            r"(?<!\d)\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}(?!\d)",
        ),
        REDACTED_PLACEHOLDER,
    ),
    # Phone: longer international (e.g. +44 20 7123 4567)
    (
        re.compile(
            r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}(?!\d)",
        ),
        REDACTED_PLACEHOLDER,
    ),
]


def apply_output_guardrails(content: str) -> str:
    """
    Redact PII (email, phone) in the given string.

    Applies all configured PII patterns and returns the string with
    matches replaced by a placeholder. Always returns a string.

    Parameters
    ----------
    content : str
        Raw response text from the Reasoner (or string representation of
        tables/other output).

    Returns
    -------
    str
        Content with PII redacted (replaced by [REDACTED]).
    """
    if not content:
        return content
    result = content
    for pattern, replacement in _PII_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def contains_pii(content: str) -> bool:
    """
    Return True if the content contains any detected PII pattern.

    Useful for callers that prefer to block the response instead of
    redacting when PII is present.

    Parameters
    ----------
    content : str
        Text to check.

    Returns
    -------
    bool
        True if any PII pattern matches, False otherwise.
    """
    if not content:
        return False
    for pattern, _ in _PII_PATTERNS:
        if pattern.search(content):
            return True
    return False

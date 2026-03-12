"""
Input guardrails: PII block, meta "available data", and vague/out-of-scope clarification.

Ensures PII in the question never reaches the LLM; answers "what data is available";
asks for clarification when the question is too vague or out of scope.
"""

from talk_to_data_slackbot.output.guardrails import contains_pii
from talk_to_data_slackbot.semantic_layer.db_connection import TABLE_SOURCES


PII_BLOCK_MESSAGE = (
    "Please don't include personal or sensitive information (e.g. email, phone numbers) "
    "in your question. Rephrase without PII and try again."
)

CLARIFICATION_MESSAGE = (
    "Your question seems too vague or outside the scope of data queries. "
    "You can ask about users, subscriptions, payments, and sessions. "
    "Try being more specific (e.g. 'How many users do we have?')."
)

# Phrases that indicate "what data is available" (normalized to lowercase).
_META_PHRASES = [
    "what data",
    "what can i ask",
    "what can i query",
    "available data",
    "available tables",
    "what tables",
    "what do you have",
    "schema",
    "list of tables",
    "what's available",
    "which data",
    "what is available",
]

# Data-like keywords that suggest a valid analytical question.
_DATA_KEYWORDS = [
    "count", "sum", "average", "total", "how many", "users", "subscriptions",
    "payments", "sessions", "revenue", "plan", "status", "amount", "duration",
]

# Blocklist: clearly off-topic (normalized).
_OFF_SCOPE_PHRASES = [
    "write a poem",
    "tell me a joke",
    "tell me a story",
    "write code",
    "hello",
    "hi",
    "hey",
]


def _normalize(s: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    return " ".join(s.lower().split())


def _build_available_data_message() -> str:
    """Build static message listing queryable tables from TABLE_SOURCES."""
    lines = ["You can query the following data:"]
    for table_name, description in TABLE_SOURCES:
        lines.append(f"• *{table_name}* — {description}")
    return "\n".join(lines)


def _is_meta_question(question: str) -> bool:
    """True if the question is asking what data is available."""
    q = _normalize(question)
    return any(phrase in q for phrase in _META_PHRASES)


def _is_vague_or_out_of_scope(question: str) -> bool:
    """True if the question is too short/vague or clearly off-topic."""
    q = _normalize(question)
    words = q.split()
    if not words:
        return True
    if any(phrase in q for phrase in _OFF_SCOPE_PHRASES):
        return True
    if len(words) < 3 and not any(kw in q for kw in _DATA_KEYWORDS):
        return True
    return False


def apply_input_guardrails(question: str) -> tuple[bool, str]:
    """
    Apply input guardrails: PII block, meta "available data", vague/out-of-scope.

    Returns (proceed, response). If proceed is False, the caller should post
    response and not send the question to the Engine. If True, response is
    empty and the caller should proceed with the pipeline.

    Parameters
    ----------
    question : str
        Raw question from the user.

    Returns
    -------
    tuple of (bool, str)
        (True, "") to proceed to Engine; (False, message) to block and post message.
    """
    q_stripped = question.strip()
    if not q_stripped:
        return (False, CLARIFICATION_MESSAGE)
    if contains_pii(q_stripped):
        return (False, PII_BLOCK_MESSAGE)
    if _is_meta_question(q_stripped):
        return (False, _build_available_data_message())
    if _is_vague_or_out_of_scope(q_stripped):
        return (False, CLARIFICATION_MESSAGE)
    return (True, "")

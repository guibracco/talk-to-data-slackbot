"""
Input guardrails: meta "available data", scope, and PII-intent classification.

Answers "what data is available?" with a static message. Uses an LLM to evaluate
scope (is the question related to the data?) and intent (is the user asking to
retrieve PII?). Responds with clarification for out-of-scope, refusal for PII-seeking.
"""

import json
import re
from talk_to_data_slackbot.llm import completion
from talk_to_data_slackbot.semantic_layer.db_connection import TABLE_SOURCES


CLARIFICATION_MESSAGE = (
    "Your question seems too vague or outside the scope of data queries. "
    "You can ask about users, subscriptions, payments, and sessions. "
    "Try being more specific (e.g. 'How many users do we have?')."
)

PII_REFUSAL_MESSAGE = (
    "We don't provide personal or sensitive information (e.g. email, phone numbers) "
    "from the data. Please ask aggregated or non-PII questions "
    "(e.g. 'How many users?' or 'Total revenue by plan')."
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

_CLASSIFIER_SYSTEM = """You classify user questions for a data-query Slack bot. The bot can only query the following data (tables and short descriptions):

{table_descriptions}

Reply with a single JSON object only, no other text. Use this exact shape:
{{"in_scope": true or false, "asking_for_pii": true or false, "clarification_hint": "string or null"}}

Rules:
- in_scope: true if the question is about querying or analyzing this data (counts, sums, trends, filters, etc.). false if off-topic, a greeting, or not about this data.
- asking_for_pii: true if the user is asking to retrieve or list personal/sensitive data (e.g. emails, phone numbers, individual identifiers). false for aggregated or anonymous questions (e.g. "how many users", "revenue by plan").
- clarification_hint: when in_scope is false, a short suggestion to reframe (e.g. "Try asking about counts or aggregates, e.g. 'How many users by country?'"). null when in_scope is true."""


def _normalize(s: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    return " ".join(s.lower().split())


def _build_available_data_message() -> str:
    """Build static message listing queryable tables from TABLE_SOURCES."""
    lines = ["You can query the following data:"]
    for table_name, description in TABLE_SOURCES:
        lines.append(f"• *{table_name}* — {description}")
    return "\n".join(lines)


def _build_table_descriptions() -> str:
    """One-line summary of TABLE_SOURCES for the classifier prompt."""
    parts = [f"{name}: {desc}" for name, desc in TABLE_SOURCES]
    return "\n".join(parts)


def _is_meta_question(question: str) -> bool:
    """True if the question is asking what data is available."""
    q = _normalize(question)
    return any(phrase in q for phrase in _META_PHRASES)


def _parse_classifier_response(raw: str) -> tuple[bool, bool, str | None]:
    """Parse JSON from classifier; return (in_scope, asking_for_pii, clarification_hint). Defaults: (True, False, None) on parse error."""
    raw = raw.strip()
    # Strip markdown code block if present
    if raw.startswith("```"):
        raw = re.sub(r"^```\w*\n?", "", raw)
        raw = re.sub(r"\n?```\s*$", "", raw)
    try:
        data = json.loads(raw)
        in_scope = bool(data.get("in_scope", True))
        asking_for_pii = bool(data.get("asking_for_pii", False))
        hint = data.get("clarification_hint")
        if hint is not None and not isinstance(hint, str):
            hint = None
        return (in_scope, asking_for_pii, hint)
    except (json.JSONDecodeError, TypeError):
        return (True, False, None)


def classify_question_scope_and_pii(
    question: str, table_descriptions: str
) -> tuple[bool, bool, str | None]:
    """
    Use the LLM to classify the question: in-scope? asking for PII?

    Parameters
    ----------
    question : str
        Raw user question.
    table_descriptions : str
        Description of available tables (e.g. from _build_table_descriptions()).

    Returns
    -------
    tuple of (bool, bool, str or None)
        (in_scope, asking_for_pii, clarification_hint). On LLM failure, returns
        (True, False, None) to fail open.
    """
    system = _CLASSIFIER_SYSTEM.format(table_descriptions=table_descriptions)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    try:
        response = completion(messages, temperature=0.0)
        return _parse_classifier_response(response)
    except Exception:
        return (True, False, None)


def apply_input_guardrails(question: str) -> tuple[bool, str]:
    """
    Apply input guardrails: meta "available data", then scope and PII-intent via LLM.

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
    if _is_meta_question(q_stripped):
        return (False, _build_available_data_message())

    table_descriptions = _build_table_descriptions()
    try:
        in_scope, asking_for_pii, clarification_hint = classify_question_scope_and_pii(
            q_stripped, table_descriptions
        )
    except Exception:
        return (True, "")  # fail open

    if asking_for_pii:
        return (False, PII_REFUSAL_MESSAGE)
    if not in_scope:
        msg = CLARIFICATION_MESSAGE
        if clarification_hint and clarification_hint.strip():
            msg = f"{msg}\n\n{clarification_hint.strip()}"
        return (False, msg)
    return (True, "")

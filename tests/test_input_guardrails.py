"""Tests for input guardrails: PII block, meta 'available data', vague/out-of-scope."""

import pytest

from talk_to_data_slackbot.input.guardrails import (
    CLARIFICATION_MESSAGE,
    PII_BLOCK_MESSAGE,
    apply_input_guardrails,
)


def test_pii_in_question_blocks_and_returns_message():
    """PII in question → (False, message) and message asks user not to include PII."""
    proceed, msg = apply_input_guardrails("What is john@example.com's subscription?")
    assert proceed is False
    assert "don't include personal" in msg or "PII" in msg or "sensitive" in msg
    assert PII_BLOCK_MESSAGE == msg

    proceed2, msg2 = apply_input_guardrails("Call me at 555-123-4567 for data")
    assert proceed2 is False
    assert msg2 == PII_BLOCK_MESSAGE


def test_meta_question_returns_available_data_message():
    """Meta question ('what data can I query?') → (False, message) with table names/descriptions."""
    proceed, msg = apply_input_guardrails("What data can I query?")
    assert proceed is False
    assert "users" in msg
    assert "subscriptions" in msg
    assert "payments" in msg
    assert "sessions" in msg
    assert "query" in msg.lower() or "data" in msg.lower()


def test_vague_short_question_returns_clarification():
    """Vague/short question ('hi') → (False, clarification message)."""
    proceed, msg = apply_input_guardrails("hi")
    assert proceed is False
    assert msg == CLARIFICATION_MESSAGE


def test_clear_data_question_proceeds():
    """Clear data question ('How many users?') → (True, '')."""
    proceed, msg = apply_input_guardrails("How many users?")
    assert proceed is True
    assert msg == ""


def test_empty_string_returns_clarification():
    """Empty string → (False, clarification)."""
    proceed, msg = apply_input_guardrails("")
    assert proceed is False
    assert msg == CLARIFICATION_MESSAGE

    proceed2, msg2 = apply_input_guardrails("   ")
    assert proceed2 is False
    assert msg2 == CLARIFICATION_MESSAGE


def test_blocklist_phrase_returns_clarification():
    """Question with only blocklist phrase (e.g. 'tell me a joke') → (False, clarification)."""
    proceed, msg = apply_input_guardrails("tell me a joke")
    assert proceed is False
    assert msg == CLARIFICATION_MESSAGE

    proceed2, _ = apply_input_guardrails("write a poem")
    assert proceed2 is False


def test_meta_phrases_detected():
    """Various meta phrasings are detected and return available-data message."""
    for q in ["What do you have?", "What tables are available?", "Show me the schema"]:
        proceed, msg = apply_input_guardrails(q)
        assert proceed is False, f"Expected block for: {q!r}"
        assert "users" in msg and "subscriptions" in msg

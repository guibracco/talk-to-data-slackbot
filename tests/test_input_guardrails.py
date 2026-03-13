"""Tests for input guardrails: meta 'available data', scope and PII-intent (LLM classifier)."""

from unittest.mock import patch

from talk_to_data_slackbot.input.guardrails import (
    CLARIFICATION_MESSAGE,
    PII_REFUSAL_MESSAGE,
    apply_input_guardrails,
    classify_question_scope_and_pii,
)


def test_empty_string_returns_clarification():
    """Empty string → (False, clarification)."""
    proceed, msg = apply_input_guardrails("")
    assert proceed is False
    assert msg == CLARIFICATION_MESSAGE

    proceed2, msg2 = apply_input_guardrails("   ")
    assert proceed2 is False
    assert msg2 == CLARIFICATION_MESSAGE


def test_meta_question_returns_available_data_message():
    """Meta question ('what data can I query?') → (False, message) with table names/descriptions."""
    proceed, msg = apply_input_guardrails("What data can I query?")
    assert proceed is False
    assert "users" in msg
    assert "subscriptions" in msg
    assert "payments" in msg
    assert "sessions" in msg
    assert "query" in msg.lower() or "data" in msg.lower()


def test_meta_phrases_detected():
    """Various meta phrasings are detected and return available-data message (no LLM)."""
    for q in ["What do you have?", "What tables are available?", "Show me the schema"]:
        proceed, msg = apply_input_guardrails(q)
        assert proceed is False, f"Expected block for: {q!r}"
        assert "users" in msg and "subscriptions" in msg


@patch("talk_to_data_slackbot.input.guardrails.classify_question_scope_and_pii")
def test_asking_for_pii_refused(mock_classify):
    """When classifier says user is asking for PII → (False, PII_REFUSAL_MESSAGE)."""
    mock_classify.return_value = (True, True, None)  # in_scope, asking_for_pii
    proceed, msg = apply_input_guardrails("list all user emails")
    assert proceed is False
    assert msg == PII_REFUSAL_MESSAGE
    assert "don't provide" in msg or "personal" in msg or "sensitive" in msg


@patch("talk_to_data_slackbot.input.guardrails.classify_question_scope_and_pii")
def test_out_of_scope_returns_clarification(mock_classify):
    """When classifier says out of scope → (False, clarification) optionally with hint."""
    mock_classify.return_value = (False, False, "Try asking about counts.")
    proceed, msg = apply_input_guardrails("hi")
    assert proceed is False
    assert CLARIFICATION_MESSAGE in msg
    assert "Try asking" in msg or "counts" in msg


@patch("talk_to_data_slackbot.input.guardrails.classify_question_scope_and_pii")
def test_in_scope_not_pii_proceeds(mock_classify):
    """When classifier says in scope and not asking for PII → (True, '')."""
    mock_classify.return_value = (True, False, None)
    proceed, msg = apply_input_guardrails("How many users?")
    assert proceed is True
    assert msg == ""


@patch("talk_to_data_slackbot.input.guardrails.classify_question_scope_and_pii")
def test_question_containing_pii_text_can_proceed_if_intent_ok(mock_classify):
    """Question that contains PII in text (e.g. email) is allowed if intent is not to retrieve PII."""
    mock_classify.return_value = (True, False, None)  # in scope, not asking for PII
    proceed, msg = apply_input_guardrails("What is john@example.com's subscription?")
    assert proceed is True
    assert msg == ""


@patch("talk_to_data_slackbot.input.guardrails.classify_question_scope_and_pii")
def test_classifier_fail_open_proceeds(mock_classify):
    """When classifier raises, we fail open → (True, '')."""
    mock_classify.side_effect = RuntimeError("LLM down")
    proceed, msg = apply_input_guardrails("How many users?")
    assert proceed is True
    assert msg == ""


def test_parse_classifier_response():
    """_parse_classifier_response handles valid JSON and code blocks."""
    from talk_to_data_slackbot.input.guardrails import _parse_classifier_response

    out = _parse_classifier_response('{"in_scope": true, "asking_for_pii": false, "clarification_hint": null}')
    assert out == (True, False, None)

    out2 = _parse_classifier_response('{"in_scope": false, "asking_for_pii": false, "clarification_hint": "Try counts."}')
    assert out2 == (False, False, "Try counts.")

    # Invalid JSON → fail open
    out3 = _parse_classifier_response("not json")
    assert out3 == (True, False, None)

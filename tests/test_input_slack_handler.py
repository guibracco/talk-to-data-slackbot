"""Tests for the Input Slack handler."""

import pytest

from talk_to_data_slackbot.input import extract_question_from_event


class TestExtractQuestionFromEvent:
    """Tests for extract_question_from_event."""

    def test_strips_bot_mention_from_text(self):
        """Mention like <@U123ABC> is removed from the question."""
        event = {"text": "<@U123ABC> How many users do we have?"}
        assert extract_question_from_event(event) == "How many users do we have?"

    def test_handles_dm_with_no_mention(self):
        """DM message with no mention returns trimmed text."""
        event = {"text": "  What is the total revenue?  "}
        assert extract_question_from_event(event) == "What is the total revenue?"

    def test_handles_multiple_mentions(self):
        """Multiple mentions are all stripped."""
        event = {"text": "<@U1> <@U2> show me subscriptions"}
        assert extract_question_from_event(event) == "show me subscriptions"

    def test_handles_empty_text(self):
        """Empty or missing text returns empty string."""
        assert extract_question_from_event({"text": ""}) == ""
        assert extract_question_from_event({}) == ""

    def test_preserves_rest_of_message(self):
        """Only mentions are removed; rest of text is unchanged."""
        event = {"text": "<@UBOT> List countries (top 5)"}
        assert extract_question_from_event(event) == "List countries (top 5)"

"""Tests for the Input Slack handler."""

import pytest

from talk_to_data_slackbot.input import extract_question_from_event, get_conversation_key


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


class TestGetConversationKey:
    """Tests for get_conversation_key."""

    def test_returns_channel_and_thread_ts_when_in_thread(self):
        """When event has thread_ts, return (channel, thread_ts) as strings."""
        event = {"channel": "C123", "ts": "1234567890.123456", "thread_ts": "1234567890.000000"}
        channel_id, thread_ts = get_conversation_key(event)
        assert channel_id == "C123"
        assert thread_ts == "1234567890.000000"

    def test_uses_ts_as_thread_ts_when_not_in_thread(self):
        """When event has no thread_ts, use ts so the reply chain is the thread."""
        event = {"channel": "C456", "ts": "1234567890.123456"}
        channel_id, thread_ts = get_conversation_key(event)
        assert channel_id == "C456"
        assert thread_ts == "1234567890.123456"

    def test_thread_ts_is_always_string(self):
        """thread_ts is returned as string (e.g. for cache key and API)."""
        event = {"channel": "C1", "ts": 1234567890.123456}
        _, thread_ts = get_conversation_key(event)
        assert isinstance(thread_ts, str)
        assert thread_ts == "1234567890.123456"

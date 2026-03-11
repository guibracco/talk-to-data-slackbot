"""Tests for the Output Slack formatter."""

import pytest

from talk_to_data_slackbot.output.slack_formatter import (
    MAX_SLACK_TEXT_LENGTH,
    format_for_slack,
)


class TestFormatForSlack:
    """Tests for format_for_slack."""

    def test_plain_text_returned_unchanged(self):
        """Single-line response is returned as-is."""
        text = "The total count is 42."
        assert format_for_slack(text) == text

    def test_empty_string_returned_unchanged(self):
        """Empty string is returned as-is."""
        assert format_for_slack("") == ""

    def test_multiline_wrapped_in_code_block(self):
        """Multiline response (e.g. table) is wrapped in code block."""
        text = "col1\tcol2\n1\t2"
        result = format_for_slack(text)
        assert result.startswith("```\n")
        assert result.endswith("\n```")
        assert "col1\tcol2" in result

    def test_long_response_truncated(self):
        """Response longer than max length is truncated with suffix."""
        long_text = "x" * (MAX_SLACK_TEXT_LENGTH + 100)
        result = format_for_slack(long_text)
        assert len(result) <= MAX_SLACK_TEXT_LENGTH + 30
        assert "... (truncated)" in result

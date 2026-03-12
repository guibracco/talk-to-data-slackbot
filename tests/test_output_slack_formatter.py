"""Tests for the Output Slack formatter."""

import os
import tempfile

import pytest

from talk_to_data_slackbot.output.slack_formatter import (
    MAX_SLACK_TEXT_LENGTH,
    format_for_slack,
    prepare_slack_response,
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


class TestPrepareSlackResponse:
    """Tests for prepare_slack_response."""

    def test_chart_path_returns_comment_and_absolute_path(self):
        """When response is a path to an existing image file, return (comment, abspath)."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            text, file_path = prepare_slack_response(path)
            assert text == "Here's your chart."
            assert file_path == os.path.abspath(path)
        finally:
            os.unlink(path)

    def test_chart_path_relative_returns_absolute(self):
        """Relative chart path is resolved to absolute."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            rel = os.path.relpath(path)
            text, file_path = prepare_slack_response(rel)
            assert file_path == os.path.abspath(path)
        finally:
            os.unlink(path)

    def test_plain_text_returns_formatted_text_and_no_file(self):
        """When response is plain text, return (formatted text, None)."""
        text, file_path = prepare_slack_response("The total is 42.")
        assert "42" in text
        assert file_path is None

    def test_nonexistent_path_treated_as_text(self):
        """A string that looks like a path but file does not exist is treated as text."""
        text, file_path = prepare_slack_response("exports/charts/nonexistent.png")
        assert file_path is None
        assert "exports" in text or "nonexistent" in text

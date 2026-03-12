"""Tests for the Output Slack poster."""

from unittest.mock import MagicMock

import pytest

from talk_to_data_slackbot.output import post_to_slack


class TestPostToSlack:
    """Tests for post_to_slack."""

    def test_text_only_calls_say(self):
        """When file_path is None, say() is called with text and thread_ts."""
        say = MagicMock()
        client = MagicMock()
        post_to_slack(
            text="The total is 42.",
            file_path=None,
            channel_id="C123",
            thread_ts="1234567890.123",
            say=say,
            client=client,
        )
        say.assert_called_once_with(text="The total is 42.", thread_ts="1234567890.123")
        client.files_upload_v2.assert_not_called()

    def test_file_upload_calls_files_upload_v2(self):
        """When file_path is set, files_upload_v2 is called with channel, thread_ts, file."""
        say = MagicMock()
        client = MagicMock()
        post_to_slack(
            text="Here's your chart.",
            file_path="/path/to/chart.png",
            channel_id="C456",
            thread_ts="1234567890.456",
            say=say,
            client=client,
        )
        client.files_upload_v2.assert_called_once_with(
            channel="C456",
            thread_ts="1234567890.456",
            file="/path/to/chart.png",
            title="Chart",
            initial_comment="Here's your chart.",
        )
        say.assert_not_called()

    def test_empty_text_uses_default_message(self):
        """When text is None or empty, say uses 'No response.' for text-only."""
        say = MagicMock()
        client = MagicMock()
        post_to_slack(
            text=None,
            file_path=None,
            channel_id="C1",
            thread_ts="1",
            say=say,
            client=client,
        )
        say.assert_called_once_with(text="No response.", thread_ts="1")

    def test_file_upload_with_empty_text_uses_default_comment(self):
        """When file_path is set and text is empty, initial_comment is default."""
        say = MagicMock()
        client = MagicMock()
        post_to_slack(
            text="",
            file_path="/tmp/chart.png",
            channel_id="C1",
            thread_ts="1",
            say=say,
            client=client,
        )
        client.files_upload_v2.assert_called_once()
        assert client.files_upload_v2.call_args[1]["initial_comment"] == "Here's your chart."

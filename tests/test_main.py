"""Tests for main entry (env validation and Socket Mode wiring)."""

import os
from unittest.mock import patch

import pytest

from talk_to_data_slackbot.main import main


class TestMainMissingTokens:
    """main() raises when Slack tokens are missing."""

    @patch("talk_to_data_slackbot.main.load_dotenv")
    def test_raises_when_bot_token_missing(self, _ld):
        with patch.dict(
            os.environ,
            {"SLACK_BOT_TOKEN": "", "SLACK_APP_TOKEN": "xapp-1"},
            clear=False,
        ):
            with pytest.raises(ValueError, match="SLACK_BOT_TOKEN and SLACK_APP_TOKEN"):
                main()

    @patch("talk_to_data_slackbot.main.load_dotenv")
    def test_raises_when_app_token_missing(self, _ld):
        with patch.dict(
            os.environ,
            {"SLACK_BOT_TOKEN": "xoxb-1", "SLACK_APP_TOKEN": ""},
            clear=False,
        ):
            with pytest.raises(ValueError, match="SLACK_BOT_TOKEN and SLACK_APP_TOKEN"):
                main()


class TestMainStartsSocketMode:
    """main() constructs App, SocketModeHandler, and starts (Bolt App mocked to avoid auth.test)."""

    @patch("talk_to_data_slackbot.main.SocketModeHandler")
    @patch("talk_to_data_slackbot.main.App")
    @patch("talk_to_data_slackbot.main.load_dotenv")
    def test_socket_mode_handler_started(self, _ld, mock_app_cls, mock_handler_cls):
        mock_app = mock_app_cls.return_value
        with patch.dict(
            os.environ,
            {
                "SLACK_BOT_TOKEN": "xoxb-test-token",
                "SLACK_APP_TOKEN": "xapp-test-token",
            },
            clear=False,
        ):
            main()

        mock_app_cls.assert_called_once_with(token="xoxb-test-token")
        mock_handler_cls.assert_called_once_with(mock_app, "xapp-test-token")
        mock_handler_cls.return_value.start.assert_called_once()

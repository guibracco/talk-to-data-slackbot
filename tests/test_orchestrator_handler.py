"""Tests for orchestrator handle_message."""

from unittest.mock import MagicMock, patch

from talk_to_data_slackbot.orchestrator.handler import handle_message


class TestHandleMessageGuardrailBlocks:
    """When input guardrails reject, only guardrail response is posted."""

    @patch("talk_to_data_slackbot.orchestrator.handler.run_pipeline")
    @patch("talk_to_data_slackbot.orchestrator.handler.post_to_slack")
    @patch("talk_to_data_slackbot.orchestrator.handler.apply_input_guardrails")
    def test_posts_guardrail_only_no_thinking_no_pipeline(
        self, mock_guard, mock_post, mock_run
    ):
        mock_guard.return_value = (False, "Please clarify your question.")
        event = {"text": "vague", "channel": "C1", "ts": "1.0"}
        say, client = MagicMock(), MagicMock()

        handle_message(event, say, client)

        mock_run.assert_not_called()
        mock_post.assert_called_once()
        args = mock_post.call_args[0]
        assert args[0] == "Please clarify your question."
        assert args[1] is None
        assert args[2] == "C1"
        thinking_calls = [
            c for c in mock_post.call_args_list if c[0][0] == "Thinking..."
        ]
        assert len(thinking_calls) == 0


class TestHandleMessageGuardrailAllows:
    """Thinking, pipeline, then result in order."""

    @patch("talk_to_data_slackbot.orchestrator.handler.run_pipeline")
    @patch("talk_to_data_slackbot.orchestrator.handler.post_to_slack")
    @patch("talk_to_data_slackbot.orchestrator.handler.apply_input_guardrails")
    def test_posts_thinking_then_pipeline_result(
        self, mock_guard, mock_post, mock_run
    ):
        mock_guard.return_value = (True, None)
        mock_run.return_value = ("The answer is 42.", "/tmp/plot.png")
        event = {"text": "How many?", "channel": "C9", "ts": "9.9"}
        say, client = MagicMock(), MagicMock()

        handle_message(event, say, client)

        assert mock_post.call_count == 2
        first = mock_post.call_args_list[0][0]
        assert first[0] == "Thinking..."
        assert first[1] is None
        assert first[2] == "C9"

        second = mock_post.call_args_list[1][0]
        assert second[0] == "The answer is 42."
        assert second[1] == "/tmp/plot.png"
        assert second[2] == "C9"

        mock_run.assert_called_once_with("How many?", "C9", "9.9")

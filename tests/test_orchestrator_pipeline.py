"""Tests for orchestrator pipeline (agent cache and run_pipeline)."""

from unittest.mock import MagicMock, patch

import pytest

import talk_to_data_slackbot.orchestrator.pipeline as pipeline_mod


@pytest.fixture(autouse=True)
def clear_agent_cache():
    """Isolate tests that use module-level _agent_cache."""
    pipeline_mod._agent_cache.clear()
    yield
    pipeline_mod._agent_cache.clear()


class TestRunPipelineEmptyQuestion:
    """Empty or whitespace-only questions."""

    @patch("talk_to_data_slackbot.orchestrator.pipeline.create_agent")
    def test_returns_prompt_and_does_not_create_agent(self, mock_create):
        """Blank question returns fixed message; create_agent never called."""
        text, path = pipeline_mod.run_pipeline("   ", "C1", "T1")
        assert text == "Please ask a data-related question."
        assert path is None
        mock_create.assert_not_called()


class TestRunPipelineChatAndFollowUp:
    """First question uses chat; same thread uses follow_up."""

    @patch("talk_to_data_slackbot.orchestrator.pipeline.prepare_slack_response")
    @patch("talk_to_data_slackbot.orchestrator.pipeline.create_agent")
    def test_same_thread_chat_then_follow_up(
        self, mock_create, mock_prepare
    ):
        """Same (channel_id, thread_ts): chat then follow_up."""
        agent = MagicMock()
        agent.chat.return_value = "r1"
        agent.follow_up.return_value = "r2"
        mock_create.return_value = agent
        mock_prepare.side_effect = lambda r: (str(r), None)

        t1, _ = pipeline_mod.run_pipeline("q1", "C", "T")
        t2, _ = pipeline_mod.run_pipeline("q2", "C", "T")

        mock_create.assert_called_once()
        agent.chat.assert_called_once_with("q1")
        agent.follow_up.assert_called_once_with("q2")
        assert t1 == "r1"
        assert t2 == "r2"

    @patch("talk_to_data_slackbot.orchestrator.pipeline.prepare_slack_response")
    @patch("talk_to_data_slackbot.orchestrator.pipeline.create_agent")
    def test_different_thread_uses_chat_again(self, mock_create, mock_prepare):
        """Different thread_ts creates a new agent and uses chat."""
        agent_a = MagicMock()
        agent_a.chat.return_value = "a"
        agent_b = MagicMock()
        agent_b.chat.return_value = "b"
        mock_create.side_effect = [agent_a, agent_b]
        mock_prepare.side_effect = lambda r: (str(r), None)

        pipeline_mod.run_pipeline("q", "C", "T1")
        pipeline_mod.run_pipeline("q", "C", "T2")

        assert mock_create.call_count == 2
        agent_a.chat.assert_called_once()
        agent_b.chat.assert_called_once()
        agent_a.follow_up.assert_not_called()
        agent_b.follow_up.assert_not_called()

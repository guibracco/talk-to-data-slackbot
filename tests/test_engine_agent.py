"""Tests for the Engine minimal Agent."""

import os
from unittest.mock import MagicMock, patch

import pytest

from talk_to_data_slackbot.engine.agent import (
    _configure_llm,
    create_agent,
    answer_question,
)


class TestConfigureLlm:
    """Tests for _configure_llm."""

    def test_sets_pai_config_with_llm_from_env(self):
        """_configure_llm loads env and calls pai.config.set with an LLM."""
        env = {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-4o-mini",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("talk_to_data_slackbot.engine.agent.pai") as mock_pai:
                _configure_llm()
        mock_pai.config.set.assert_called_once()
        call_args = mock_pai.config.set.call_args[0][0]
        assert "llm" in call_args
        assert call_args["llm"] is not None

    def test_uses_default_model_when_openai_model_unset(self):
        """When OPENAI_MODEL is unset, LiteLLM is called with default model."""
        env = {"OPENAI_API_KEY": "test-key"}
        with patch.dict(os.environ, env, clear=False):
            with patch("talk_to_data_slackbot.engine.agent.LiteLLM") as mock_llm:
                with patch("talk_to_data_slackbot.engine.agent.pai"):
                    _configure_llm()
        mock_llm.assert_called_once_with(model="gpt-4o-mini", api_key="test-key")


class TestCreateAgent:
    """Tests for create_agent."""

    @pytest.fixture
    def minimal_env(self):
        """Minimal env for agent creation (avoids real DB/API)."""
        return {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-4o-mini",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "u",
            "DB_PASS": "p",
        }

    def test_returns_agent_with_sources_from_semantic_layer(self, minimal_env):
        """create_agent calls get_data_sources and returns an Agent built with them."""
        fake_sources = [MagicMock(), MagicMock()]
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.engine.agent.get_data_sources") as mock_get:
                with patch("talk_to_data_slackbot.engine.agent.Agent") as mock_agent_cls:
                    mock_get.return_value = fake_sources
                    result = create_agent()
        mock_get.assert_called_once()
        mock_agent_cls.assert_called_once_with(fake_sources)
        assert result == mock_agent_cls.return_value

    def test_configures_llm_before_creating_agent(self, minimal_env):
        """create_agent calls _configure_llm before get_data_sources."""
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.engine.agent._configure_llm") as mock_cfg:
                with patch("talk_to_data_slackbot.engine.agent.get_data_sources") as mock_get:
                    with patch("talk_to_data_slackbot.engine.agent.Agent"):
                        mock_get.return_value = []
                        create_agent()
        mock_cfg.assert_called_once()
        # _configure_llm should be called before get_data_sources
        assert mock_cfg.call_count == 1
        assert mock_get.call_count == 1


class TestAnswerQuestion:
    """Tests for answer_question."""

    @pytest.fixture
    def minimal_env(self):
        return {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-4o-mini",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "u",
            "DB_PASS": "p",
        }

    def test_returns_agent_chat_result(self, minimal_env):
        """answer_question creates agent, calls chat(question), returns result."""
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.engine.agent.create_agent") as mock_create:
                mock_agent = MagicMock()
                mock_agent.chat.return_value = "The answer is 42."
                mock_create.return_value = mock_agent
                result = answer_question("What is the total?")
        mock_create.assert_called_once()
        mock_agent.chat.assert_called_once_with("What is the total?")
        assert result == "The answer is 42."

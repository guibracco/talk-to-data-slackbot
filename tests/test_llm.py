"""Tests for shared LLM config and completion."""

import os
from types import SimpleNamespace
from unittest.mock import patch

from talk_to_data_slackbot import llm


class TestGetModelAndApiKey:
    """get_model_and_api_key reads env with defaults."""

    @patch("talk_to_data_slackbot.llm.load_dotenv")
    def test_default_model_when_openai_model_unset(self, _ld):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=False):
            os.environ.pop("OPENAI_MODEL", None)
            model, key = llm.get_model_and_api_key()
        assert model == "gpt-4o-mini"
        assert key == "sk-test"

    @patch("talk_to_data_slackbot.llm.load_dotenv")
    def test_custom_model_from_env(self, _ld):
        with patch.dict(
            os.environ,
            {"OPENAI_MODEL": "gpt-4o", "OPENAI_API_KEY": "k"},
            clear=False,
        ):
            model, key = llm.get_model_and_api_key()
        assert model == "gpt-4o"
        assert key == "k"

    @patch("talk_to_data_slackbot.llm.load_dotenv")
    def test_empty_api_key_when_unset(self, _ld):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("OPENAI_MODEL", None)
            _model, key = llm.get_model_and_api_key()
        assert key == ""


class TestCompletion:
    """completion delegates to litellm with shared model/key."""

    @patch("talk_to_data_slackbot.llm.litellm.completion")
    @patch("talk_to_data_slackbot.llm.get_model_and_api_key")
    def test_calls_litellm_and_returns_stripped_content(self, mock_gmk, mock_comp):
        mock_gmk.return_value = ("my-model", "secret")
        msg = SimpleNamespace(content="  hello world  ")
        choice = SimpleNamespace(message=msg)
        resp = SimpleNamespace(choices=[choice])
        mock_comp.return_value = resp

        out = llm.completion([{"role": "user", "content": "hi"}], temperature=0.1)

        mock_comp.assert_called_once_with(
            model="my-model",
            messages=[{"role": "user", "content": "hi"}],
            api_key="secret",
            temperature=0.1,
        )
        assert out == "hello world"

    @patch("talk_to_data_slackbot.llm.litellm.completion")
    @patch("talk_to_data_slackbot.llm.get_model_and_api_key")
    def test_empty_string_when_no_choices(self, mock_gmk, mock_comp):
        mock_gmk.return_value = ("m", "k")
        mock_comp.return_value = SimpleNamespace(choices=[])

        assert llm.completion([{"role": "user", "content": "x"}]) == ""

    @patch("talk_to_data_slackbot.llm.litellm.completion")
    @patch("talk_to_data_slackbot.llm.get_model_and_api_key")
    def test_empty_string_when_content_none(self, mock_gmk, mock_comp):
        mock_gmk.return_value = ("m", "k")
        msg = SimpleNamespace(content=None)
        mock_comp.return_value = SimpleNamespace(choices=[SimpleNamespace(message=msg)])

        assert llm.completion([{"role": "user", "content": "x"}]) == ""

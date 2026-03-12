"""Tests for the Semantic Layer database connection component."""

import os
from unittest.mock import patch

import pytest

from talk_to_data_slackbot.semantic_layer.db_connection import (
    TABLE_SOURCES,
    clear_data_sources_cache,
    get_data_sources,
    _get_connection_config,
)


class TestGetConnectionConfig:
    """Tests for _get_connection_config."""

    def test_reads_connection_from_env(self):
        """Connection config contains host, port, database, user, password from env."""
        env = {
            "DB_HOST": "localhost",
            "DB_PORT": "5433",
            "DB_NAME": "mydb",
            "DB_USER": "u",
            "DB_PASS": "p",
        }
        with patch.dict(os.environ, env, clear=False):
            config = _get_connection_config()
        assert config["host"] == "localhost"
        assert config["port"] == 5433
        assert config["database"] == "mydb"
        assert config["user"] == "u"
        assert config["password"] == "p"

    def test_default_port_when_not_set(self):
        """DB_PORT defaults to 5432 when not set."""
        env = {
            "DB_HOST": "localhost",
            "DB_NAME": "mydb",
            "DB_USER": "u",
            "DB_PASS": "p",
        }
        with patch.dict(os.environ, env, clear=False):
            config = _get_connection_config()
        assert config["port"] == 5432


class TestGetDataSources:
    """Tests for get_data_sources."""

    @pytest.fixture
    def minimal_env(self):
        """Minimal DB env vars for get_data_sources."""
        return {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASS": "testpass",
        }

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Reset data sources cache so each test gets fresh pai.create calls."""
        clear_data_sources_cache()
        yield
        clear_data_sources_cache()

    def test_returns_four_sources(self, minimal_env):
        """get_data_sources returns one source per table (4 total)."""
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.semantic_layer.db_connection.pai") as mock_pai:
                mock_pai.create.side_effect = lambda **kwargs: object()
                sources = get_data_sources()
        assert len(sources) == 4
        assert mock_pai.create.call_count == 4

    def test_calls_create_with_correct_path_and_table_for_each(self, minimal_env):
        """Each pai.create call uses path <organization>/<table> (default organization) and matching table name."""
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.semantic_layer.db_connection.pai") as mock_pai:
                mock_pai.create.side_effect = lambda **kwargs: object()
                get_data_sources()
        calls = mock_pai.create.call_args_list
        for i, (table_name, _) in enumerate(TABLE_SOURCES):
            assert calls[i].kwargs["path"] == f"organization/{table_name}"
            assert calls[i].kwargs["source"]["table"] == table_name
            assert calls[i].kwargs["source"]["type"] == "postgres"
            assert calls[i].kwargs["source"]["connection"]["host"] == "localhost"
            assert calls[i].kwargs["source"]["connection"]["database"] == "testdb"

    def test_calls_create_with_path_from_semantic_layer_organization_env(self, minimal_env):
        """When SEMANTIC_LAYER_ORGANIZATION is set, pai.create path uses that value."""
        minimal_env["SEMANTIC_LAYER_ORGANIZATION"] = "myorg"
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.semantic_layer.db_connection.pai") as mock_pai:
                mock_pai.create.side_effect = lambda **kwargs: object()
                get_data_sources()
        calls = mock_pai.create.call_args_list
        for i, (table_name, _) in enumerate(TABLE_SOURCES):
            assert calls[i].kwargs["path"] == f"myorg/{table_name}"

    def test_second_call_returns_cached_sources_without_calling_create(self, minimal_env):
        """Second get_data_sources() returns cache; pai.create is not called again."""
        with patch.dict(os.environ, minimal_env, clear=False):
            with patch("talk_to_data_slackbot.semantic_layer.db_connection.pai") as mock_pai:
                mock_pai.create.side_effect = lambda **kwargs: object()
                first = get_data_sources()
                second = get_data_sources()
        assert first is second
        assert mock_pai.create.call_count == 4

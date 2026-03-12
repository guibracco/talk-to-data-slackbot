"""
Database connection component for the Semantic Layer.

Uses pandasai.create() to register Postgres tables as semantic-layer data sources.
Credentials are read from the environment (e.g. .env via python-dotenv).
"""

import os
import shutil
from typing import Any

from dotenv import load_dotenv
import pandasai as pai

def _get_semantic_layer_organization() -> str:
    """Organization name for PandasAI datasets; from SEMANTIC_LAYER_ORGANIZATION env, default 'organization'."""
    load_dotenv()
    return os.environ.get("SEMANTIC_LAYER_ORGANIZATION", "organization")


def _semantic_layer_organization_path() -> str:
    """Path where PandasAI persists organization/ datasets (so we can clear it after restart)."""
    return os.path.join(os.getcwd(), "datasets", _get_semantic_layer_organization())


# Table metadata: path suffix, description (for semantic layer).
TABLE_SOURCES = [
    (
        "users",
        "Stores information about individual users (user_id, signup_date, country, device_type).",
    ),
    (
        "subscriptions",
        "Tracks user subscriptions to different plans (subscription_id, user_id, plan, status, start_date, end_date).",
    ),
    (
        "payments",
        "Logs all payment transactions for subscriptions (payment_id, subscription_id, payment_date, amount_usd, method).",
    ),
    (
        "sessions",
        "Logs user activity sessions (session_id, user_id, session_date, duration_minutes, activity_type).",
    ),
]


def _get_connection_config() -> dict[str, Any]:
    """
    Build Postgres connection config from environment variables.

    Expects DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS to be set
    (e.g. via .env loaded with python-dotenv).

    Returns
    -------
    dict
        Connection dict suitable for pai.create() source["connection"].
    """
    load_dotenv()
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", "5432")),
        "database": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASS"],
    }


# Cache so pai.create() is only called once per process (avoids "Dataset already exists").
_cached_sources: list[Any] | None = None


def clear_data_sources_cache() -> None:
    """
    Clear the cached data sources (for tests or process restart).

    After calling this, the next get_data_sources() will call pai.create() again.
    """
    global _cached_sources
    _cached_sources = None


def get_data_sources() -> list[Any]:
    """
    Create and return semantic-layer data sources for all Postgres tables.

    On first call, reads DB_* from the environment, calls pandasai.create()
    for each table (users, subscriptions, payments, sessions), caches the
    result, and returns it. Subsequent calls return the cached list so
    pai.create() is not run again (PandasAI raises if a path already exists).

    Returns
    -------
    list
        List of data source objects returned by pai.create(), one per table.
        Order: users, subscriptions, payments, sessions.

    Raises
    ------
    KeyError
        If any required env var (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS) is missing.
    """
    global _cached_sources
    if _cached_sources is not None:
        return _cached_sources
    # Remove persisted organization datasets from a previous process so pai.create() can run again.
    org_path = _semantic_layer_organization_path()
    if os.path.isdir(org_path):
        shutil.rmtree(org_path, ignore_errors=True)
    load_dotenv()
    connection = _get_connection_config()
    organization = _get_semantic_layer_organization()
    sources = []
    for table_name, description in TABLE_SOURCES:
        df = pai.create(
            path=f"{organization}/{table_name}",
            description=description,
            source={
                "type": "postgres",
                "connection": connection,
                "table": table_name,
            },
        )
        sources.append(df)
    _cached_sources = sources
    return sources

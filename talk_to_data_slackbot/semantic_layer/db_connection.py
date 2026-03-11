"""
Database connection component for the Semantic Layer.

Uses pandasai.create() to register Postgres tables as semantic-layer data sources.
Credentials are read from the environment (e.g. .env via python-dotenv).
"""

import os
from typing import Any

from dotenv import load_dotenv
import pandasai as pai


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


def get_data_sources() -> list[Any]:
    """
    Create and return semantic-layer data sources for all Postgres tables.

    Reads DB_* from the environment, calls pandasai.create() for each table
    (users, subscriptions, payments, sessions), and returns the list of
    created objects for use by the Engine (e.g. Agent(sources)).

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
    load_dotenv()
    connection = _get_connection_config()
    sources = []
    for table_name, description in TABLE_SOURCES:
        df = pai.create(
            path=f"company/{table_name}",
            description=description,
            source={
                "type": "postgres",
                "connection": connection,
                "table": table_name,
            },
        )
        sources.append(df)
    return sources

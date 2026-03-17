"""
Pipeline: agent cache and run_pipeline.

Holds the per-thread agent cache (channel_id, thread_ts) -> Agent and runs
questions through the engine (chat or follow_up), then prepares the response
for Slack.
"""

from typing import Any

from talk_to_data_slackbot.engine import create_agent
from talk_to_data_slackbot.output import prepare_slack_response

# Per-thread agent cache for follow-up context.
_agent_cache: dict[tuple[str, str], Any] = {}


def run_pipeline(
    question: str, channel_id: str, thread_ts: str
) -> tuple[str | None, str | None]:
    """
    Get answer (chat or follow_up), prepare for Slack.

    Returns (text, file_path). Uses in-memory agent cache keyed by
    (channel_id, thread_ts).
    """
    if not question.strip():
        return ("Please ask a data-related question.", None)
    key = (channel_id, thread_ts)
    if key not in _agent_cache:
        _agent_cache[key] = create_agent()
        response = _agent_cache[key].chat(question)
    else:
        response = _agent_cache[key].follow_up(question)
    return prepare_slack_response(response)

"""
Output: format the response for Slack.

Prepares the guardrails output for posting (plain text or code block for MVP).
Handles chart responses by returning a file path for upload.
"""

import os
from typing import Any

# Slack message limit is 4000; leave headroom for blocks/formatting.
MAX_SLACK_TEXT_LENGTH = 3900


def _is_chart_path(path: str) -> bool:
    """True if path looks like an image file and exists on disk."""
    path = path.strip()
    if not path or not path.endswith((".png", ".jpg", ".jpeg", ".svg")):
        return False
    abs_path = os.path.abspath(path)
    return os.path.isfile(abs_path)


def prepare_slack_response(response: Any) -> tuple[str | None, str | None]:
    """
    Turn the agent response into text and/or a chart file path for Slack.

    If the response is a chart (path to an image file), returns (comment, abs_path)
    so the caller can upload the file. Otherwise returns (formatted_text, None).

    Parameters
    ----------
    response : Any
        Raw response from agent.chat() (str, number, path, or ChartResponse-like).

    Returns
    -------
    tuple of (text or None, file_path or None)
        (initial_comment or formatted text, path to image file or None).
    """
    from talk_to_data_slackbot.output.guardrails import apply_output_guardrails

    # PandasAI may return a path string or an object with .value as path
    path_candidate = None
    if isinstance(response, str) and _is_chart_path(response):
        path_candidate = os.path.abspath(response.strip())
    elif hasattr(response, "value") and isinstance(getattr(response, "value"), str):
        val = getattr(response, "value")
        if _is_chart_path(val):
            path_candidate = os.path.abspath(val.strip())

    if path_candidate:
        return ("Here's your chart.", path_candidate)

    # Text response: apply guardrails and format
    text = apply_output_guardrails(str(response))
    return (format_for_slack(text), None)


def format_for_slack(response: str) -> str:
    """
    Format the response string for posting to Slack.

    For MVP: return as-is, or wrap in a code block if long or multiline
    (e.g. table-like output). Optionally truncate if over Slack limit.

    Parameters
    ----------
    response : str
        Guardrails-safe response text.

    Returns
    -------
    str
        Formatted string suitable for chat_postMessage/say.
    """
    if not response:
        return response
    if len(response) > MAX_SLACK_TEXT_LENGTH:
        response = response[: MAX_SLACK_TEXT_LENGTH - 20] + "\n... (truncated)"
    # Use code block for multiline (e.g. tables) so it doesn't get mangled
    if "\n" in response and response.strip().count("\n") >= 1:
        return f"```\n{response}\n```"
    return response

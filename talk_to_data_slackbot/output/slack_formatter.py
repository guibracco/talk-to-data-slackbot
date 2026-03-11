"""
Output: format the response for Slack.

Prepares the guardrails output for posting (plain text or code block for MVP).
"""

# Slack message limit is 4000; leave headroom for blocks/formatting.
MAX_SLACK_TEXT_LENGTH = 3900


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

"""
Input: receive and parse Slack messages.

Extracts the user's question text from Slack message or app_mention events.
"""

import re
from typing import Any


def extract_question_from_event(event: dict[str, Any]) -> str:
    """
    Get the raw question text from a Slack message or app_mention event.

    Strips bot user IDs (e.g. <@U123ABC>) from the message so the
    question can be sent to the Engine. Handles both channel mentions
    and DMs (where there may be no mention).

    Parameters
    ----------
    event : dict
        Slack event payload; must have a "text" key (message or app_mention).

    Returns
    -------
    str
        Trimmed question text with mentions removed.
    """
    text = event.get("text") or ""
    # Remove <@U123ABC> style mentions (bot user IDs)
    text = re.sub(r"<@[A-Z0-9]+>", "", text)
    return text.strip()

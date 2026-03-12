"""
Input: receive and parse Slack messages.

Extracts the user's question and conversation context from Slack events.
"""

import re
from typing import Any


def get_conversation_key(event: dict[str, Any]) -> tuple[str, str]:
    """
    Get (channel_id, thread_ts) from a Slack event for conversation context.

    Use the same pair to key per-thread agent state and to post replies
    in the same channel/thread.

    Parameters
    ----------
    event : dict
        Slack message or app_mention event with "channel" and "ts";
        may have "thread_ts" for replies.

    Returns
    -------
    tuple of (str, str)
        (channel_id, thread_ts) with thread_ts as string. For top-level
        messages, thread_ts is the message ts so the thread is the reply chain.
    """
    channel_id = event.get("channel", "")
    thread_ts = event.get("thread_ts") or event.get("ts")
    return (channel_id, str(thread_ts))


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

"""
Output: post the prepared answer to Slack.

Sends text messages or uploads chart files to the channel/thread.
"""

from typing import Any


def post_to_slack(
    text: str | None,
    file_path: str | None,
    channel_id: str,
    thread_ts: str,
    say: Any,
    client: Any,
) -> None:
    """
    Post the answer to Slack (text or file upload in the given channel/thread).

    If file_path is set, uploads the file with initial_comment; otherwise
    posts the text via say().

    Parameters
    ----------
    text : str or None
        Message text (initial comment for file, or main message for text).
    file_path : str or None
        Path to image file to upload, or None for text-only.
    channel_id : str
        Slack channel ID.
    thread_ts : str
        Thread timestamp for replies.
    say : callable
        Bolt say() to post a text message.
    client : Slack WebClient
        Bolt client for files_upload_v2.
    """
    if file_path:
        client.files_upload_v2(
            channel=channel_id,
            thread_ts=thread_ts,
            file=file_path,
            title="Chart",
            initial_comment=text or "Here's your chart.",
        )
    else:
        say(text=text or "No response.", thread_ts=thread_ts)

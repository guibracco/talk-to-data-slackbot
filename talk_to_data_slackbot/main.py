"""
Talk-to-Data Slackbot entry point.

Starts the Slack Bolt app in Socket Mode: on app_mention or DM message,
runs the pipeline (Engine + Output guardrails + formatter) and posts the reply.
"""

# Use non-GUI backend before any chart code runs (Bolt handlers run in worker threads;
# macOS requires NSWindow on the main thread, so GUI backends would crash).
import matplotlib
matplotlib.use("Agg")

import os
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from talk_to_data_slackbot.engine import create_agent
from talk_to_data_slackbot.input import extract_question_from_event, get_conversation_key
from talk_to_data_slackbot.output import prepare_slack_response

# Per-thread agent cache: (channel_id, thread_ts) -> Agent for follow-up context.
_thread_agents: dict[tuple[str, str], Any] = {}


def _run_pipeline(
    question: str, channel_id: str, thread_ts: str
) -> tuple[str | None, str | None]:
    """Get answer (chat or follow_up), prepare for Slack. Returns (text, file_path)."""
    if not question.strip():
        return ("Please ask a data-related question.", None)
    key = (channel_id, thread_ts)
    if key not in _thread_agents:
        _thread_agents[key] = create_agent()
        response = _thread_agents[key].chat(question)
    else:
        response = _thread_agents[key].follow_up(question)
    return prepare_slack_response(response)


def _handle_message(event: dict[str, Any], say: Any, client: Any) -> None:
    """Process one message: parse input, run pipeline, post text or upload chart."""
    question = extract_question_from_event(event)
    channel_id, thread_ts = get_conversation_key(event)
    text, file_path = _run_pipeline(question, channel_id, thread_ts)

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


def main() -> None:
    """Load env, create Bolt app, register listeners, start Socket Mode."""
    load_dotenv()
    token = os.environ.get("SLACK_BOT_TOKEN")
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not token or not app_token:
        raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set")
    app = App(token=token)

    @app.event("app_mention")
    def on_app_mention(event: dict[str, Any], say: Any, client: Any) -> None:
        _handle_message(event, say, client)

    @app.event("message")
    def on_message(event: dict[str, Any], say: Any, client: Any) -> None:
        # Only respond to DMs (channel_type im); ignore bot messages and subtypes
        if event.get("channel_type") != "im":
            return
        if event.get("bot_id"):
            return
        if event.get("subtype"):
            return
        _handle_message(event, say, client)

    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    main()

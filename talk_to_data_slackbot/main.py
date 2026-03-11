"""
Talk-to-Data Slackbot entry point.

Starts the Slack Bolt app in Socket Mode: on app_mention or DM message,
runs the pipeline (Engine + Output guardrails + formatter) and posts the reply.
"""

import os
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from talk_to_data_slackbot.engine import answer_question
from talk_to_data_slackbot.input import extract_question_from_event
from talk_to_data_slackbot.output import apply_output_guardrails, format_for_slack


def _run_pipeline(question: str) -> str:
    """Get answer, apply guardrails, format for Slack."""
    if not question.strip():
        return "Please ask a data-related question."
    response = answer_question(question)
    safe = apply_output_guardrails(str(response))
    return format_for_slack(safe)


def _handle_message(event: dict[str, Any], say: Any) -> None:
    """Process one message: extract question, run pipeline, reply."""
    question = extract_question_from_event(event)
    formatted = _run_pipeline(question)
    thread_ts = event.get("thread_ts") or event.get("ts")
    say(text=formatted, thread_ts=thread_ts)


def main() -> None:
    """Load env, create Bolt app, register listeners, start Socket Mode."""
    load_dotenv()
    token = os.environ.get("SLACK_BOT_TOKEN")
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not token or not app_token:
        raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set")
    app = App(token=token)

    @app.event("app_mention")
    def on_app_mention(event: dict[str, Any], say: Any) -> None:
        _handle_message(event, say)

    @app.event("message")
    def on_message(event: dict[str, Any], say: Any) -> None:
        # Only respond to DMs (channel_type im); ignore bot messages and subtypes
        if event.get("channel_type") != "im":
            return
        if event.get("bot_id"):
            return
        if event.get("subtype"):
            return
        _handle_message(event, say)

    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    main()

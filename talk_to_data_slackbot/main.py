"""
Talk-to-Data Slackbot entry point.

Starts the Slack Bolt app in Socket Mode: on app_mention or DM message,
delegates to orchestrator (handle_message) for parse → guardrails → pipeline → post.
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

from talk_to_data_slackbot.orchestrator import handle_message


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
        handle_message(event, say, client)

    @app.event("message")
    def on_message(event: dict[str, Any], say: Any, client: Any) -> None:
        # Only respond to DMs (channel_type im); ignore bot messages and subtypes
        if event.get("channel_type") != "im":
            return
        if event.get("bot_id"):
            return
        if event.get("subtype"):
            return
        handle_message(event, say, client)

    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == "__main__":
    main()

"""
Message handler: parse, guardrails, thinking, pipeline, post.

Single entry point for processing a Slack message: extract question and
conversation key, apply input guardrails, post "Thinking..." if proceeding,
run pipeline, post result (or guardrail response).
"""

from typing import Any

from talk_to_data_slackbot.input import (
    apply_input_guardrails,
    extract_question_from_event,
    get_conversation_key,
)
from talk_to_data_slackbot.output import post_to_slack
from talk_to_data_slackbot.orchestrator.pipeline import run_pipeline


def handle_message(event: dict[str, Any], say: Any, client: Any) -> None:
    """
    Process one message: parse, guardrails, run pipeline or post guardrail response.
    """
    question = extract_question_from_event(event)
    channel_id, thread_ts = get_conversation_key(event)
    proceed, guardrail_response = apply_input_guardrails(question)
    if not proceed:
        post_to_slack(guardrail_response, None, channel_id, thread_ts, say, client)
        return
    post_to_slack("Thinking...", None, channel_id, thread_ts, say, client)
    text, file_path = run_pipeline(question, channel_id, thread_ts)
    post_to_slack(text, file_path, channel_id, thread_ts, say, client)

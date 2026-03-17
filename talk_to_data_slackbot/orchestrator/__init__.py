"""
Orchestration: composes input, pipeline, and output for each Slack message.

Handler (handle_message) and pipeline (run_pipeline) together define the
message flow: parse → guardrails → thinking → engine → post.
"""

from talk_to_data_slackbot.orchestrator.handler import handle_message
from talk_to_data_slackbot.orchestrator.pipeline import run_pipeline

__all__ = ["handle_message", "run_pipeline"]

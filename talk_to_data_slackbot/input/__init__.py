"""Input: receive and parse user questions from Slack."""

from talk_to_data_slackbot.input.slack_handler import extract_question_from_event

__all__ = ["extract_question_from_event"]

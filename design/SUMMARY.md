# Talk-to-Data Slackbot Design Summary

## Design Choices

This design is intentionally (albeit not easily) minimal. The diagram tells one simple story: a question starts in Slack (and can bounce back in case of error or ambiguity), moves through a small agent flow, touches the database as an external dependency, and ends as an answer back in Slack.

Inside the agent, there are five high-level subsystems:

- `Input`: receives the Slack message and applies basic safety checks.
- `Engine` and `Semantic Layer`: determine how to answer the question.
- `Memory`: stores the context of the conversation.
- `Output`: turns the result into a Slack-friendly response.

The `Database` is an external environment, not part of the bot itself. The agent depends on it for company data but does not own it.

## How This Meets User Needs

- It takes free-text questions from the user.
- It turns the question back in case of ambiguity.
- It keeps context for follow-up questions.
- The separation between Engine and Semantic makes it easier to update business logic.

## Potential Risks

1. A very simple flow may hide important edge cases like ambiguous questions or permission issues.
2. Not sure how to handle the double access to Memory — will context window be a problem over long interactions?
3. Not sure how to handle ambiguity — PandasAI may still generate incorrect analysis if the question is unclear.
4. The external database can become a bottleneck if queries are slow or poorly scoped — how to prevent terabyte-queries?

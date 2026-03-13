# Talk-to-Data Slackbot

A Slack bot that lets you ask natural-language questions about internal data (Postgres) and get answers directly in Slack. Powered by [PandasAI](https://docs.pandas-ai.com/) and OpenAI. No SQL or dashboards required.

![System Design](design/agent_design.png)

## Features

- **Ask in Slack**: Mention the bot in a channel or send a DM; ask questions in plain language.
- **Queryable data**: Answers are based on tables exposed by the semantic layer (users, subscriptions, payments, sessions).
- **Follow-up context**: Questions in the same thread keep conversation context for multi-turn queries.
- **Input guardrails**:
  - **Scope and intent**: A single LLM call classifies each question — is it about the available data (scope)? Is the user asking to retrieve PII from the data (intent)? Out-of-scope questions get a clarification and optional reframing hint; PII-seeking questions are refused with a clear reason. Questions that merely mention PII (e.g. “subscription for john@example.com”) are allowed when the intent is not to list or export PII.
  - **“What data is available?”**: Answered with a static list of tables and descriptions (no LLM).
- **Output**: Slack-friendly formatting, optional file upload (e.g. charts); output guardrails redact PII from responses before posting.

## Requirements

- **Python 3.11**
- **Poetry** for dependency management
- **Postgres** database with the expected schema (or compatible tables)
- **OpenAI** API key
- **Slack app** with Bot Token and App Token (Socket Mode), and the right OAuth scopes and event subscriptions (`app_mention`, `message` in DMs). See [Slack API](https://api.slack.com/) for creating an app.

## Installation

1. Clone the repository.
2. From the project root, run:
  ```bash
   poetry install
  ```
   For development and tests:
   Poetry creates and uses a virtual environment automatically.

## Configuration

1. Copy `.env.example` to `.env` and fill in the values.
2. **Required variables**
  - **Postgres**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`
  - **OpenAI**: `OPENAI_API_KEY`
  - **Slack**: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`
3. **Optional**
  - `OPENAI_MODEL` — default `gpt-4o-mini`
  - `SEMANTIC_LAYER_ORGANIZATION` — PandasAI dataset path prefix; default `organization`
  - `SLACK_SIGNING_SECRET` — if needed for your setup

Do not commit `.env` or real secrets; use environment variables only.

## Running the bot

From the project root:

```bash
poetry run python -m talk_to_data_slackbot.main
```

The app uses **Slack Socket Mode**, so no public URL is required for receiving events.

## Usage in Slack

- **Channels**: Mention the bot and ask a data question in the same message. You can send follow-up questions in the thread.
- **DMs**: Send a message; the bot replies in the thread. Follow-up messages in the thread use conversation memory.

**Example questions**

- “How many users do we have?”
- “What’s the total revenue by plan?”
- “What data can I query?” — returns a list of available tables and descriptions.

If your question is vague or off-topic, the bot asks for clarification (sometimes with a reframing hint). If you ask to retrieve personal or sensitive data (e.g. “list all user emails”), the bot refuses and suggests aggregated or non-PII questions instead.

## Project structure

- **Input** (`talk_to_data_slackbot/input/`) — Parse Slack events (question, conversation key); input guardrails: meta “what data available” (static), then scope and PII-intent via LLM classifier (`classify_question_scope_and_pii`).
- **LLM** (`talk_to_data_slackbot/llm.py`) — Shared config and completion: `get_model_and_api_key()`, `completion(messages)`. Used by the engine (PandasAI) and by the input guardrails classifier so env and model live in one place.
- **Engine** (`talk_to_data_slackbot/engine/`) — PandasAI Agent; `chat` and `follow_up` for answering questions. Uses shared LLM config.
- **Semantic Layer** (`talk_to_data_slackbot/semantic_layer/`) — Postgres connection, table metadata (`TABLE_SOURCES`), `get_data_sources()` for the Agent.
- **Output** (`talk_to_data_slackbot/output/`) — Output guardrails (PII redaction), formatter, Slack posting (text and optional file).
- **Memory** — Conversation context per thread (in-memory agent cache via PandasAI Agent).
- **Main** (`talk_to_data_slackbot/main.py`) — Bolt app, Socket Mode, message handler: Input → guardrails → pipeline or guardrail response → Output.

### Input guardrails: design choices

- **Why an LLM for scope and PII intent?** Heuristics (length, keywords, blocklists) were too brittle and blocked valid questions. The LLM judges whether the question is about the available data and whether the user is asking to retrieve PII (e.g. “list all emails”) vs. aggregated analytics. That keeps the bot usable while still refusing PII-seeking requests.
- **Shared LLM module:** The engine and the guardrails both use `talk_to_data_slackbot.llm` for model and API key. One place to change env or provider; the guardrail is just another consumer of `completion()`.
- **Fail-open:** If the classifier call fails (network, parse error), the bot proceeds to the main pipeline instead of blocking. Availability is preferred; the main engine and output guardrails still apply.
- **“What data is available?”** stays heuristic + static response so we don’t spend an LLM call on a simple meta question.

## Testing

Run tests:

```bash
poetry run pytest -q
```

Verbose:

```bash
poetry run pytest -v
```

## Author

Guilherme Bracco
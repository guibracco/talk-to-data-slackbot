# Talk-to-Data Slackbot — Project Context

## Project Overview

The **Talk-to-Data Slackbot** is a conversational AI agent that lets team members ask data-related questions in Slack and receive verified, analyzed answers — including text, tables, and diagrams or graphs — directly in chat. It consults an external database, reasons over the data, and returns responses that are accurate and safe to share.

**Why it exists:** It enables analysts, product managers, marketers, and other non-technical users to get instant insights from internal data without writing SQL or opening dashboards.

---

## System Scope

**In scope:**

- Receiving natural-language questions from users in Slack.
- Parsing and validating user input (guardrails for safety and accuracy).
- Planning which data sources to use and reasoning over retrieved data.
- Maintaining conversational context for follow-up questions and clarifications.
- Accessing company data via a semantic layer that abstracts tables, relationships, and join logic.
- Formatting answers for Slack (text, tables, diagrams/graphs) and applying output guardrails before posting.

**Out of scope:**

- Owning or operating the external database; the database is an external dependency.
- User authentication/authorization aside from what Slack and the hosting environment provide.
- General-purpose chat beyond data-related questions (unless explicitly extended later).

---

## Data Sources

PostgreSQL database with 4 tables:

- `users` — stores information about individual users (user_id, signup_date, country, device_type).
- `subscriptions` — tracks user subscriptions to different plans (subscription_id, user_id, plan, status, start_date, end_date).
- `payments` — logs all payment transactions for subscriptions (payment_id, subscription_id, payment_date, amount_usd, method).
- `sessions` — logs user activity sessions (session_id, user_id, session_date, duration_minutes, activity_type).

---

## Architecture Summary

The system is the **Talk-to-Data Slackbot**. It interacts with two **external environments**: **Slack** (user interface) and a **Database** (data source).

The bot is organized into five **subsystems**:


| Subsystem          | Role                                                                                                                                                                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Input**          | Receives the question from Slack, parses it, and applies input guardrails. Exchanges context with Memory for conversation state. Sends a parsed request to the Engine.                                                        |
| **Memory**         | Stores and retrieves conversational context so the agent can handle follow-ups and clarifications.                                                                                                                            |
| **Engine**         | **Planner** decides which data to investigate and the execution strategy; **Reasoner** analyzes data and produces the answer. Both use the Semantic Layer for schema and data access; Planner can update Memory with context. |
| **Semantic Layer** | Holds metadata (tables, relationships, join logic) and bridges the Engine and the Database so the Engine can work in conceptual terms rather than raw SQL.                                                                    |
| **Output**         | Receives the analysis from the Reasoner, applies output guardrails, then formats the answer for Slack (text, tables, diagrams/graphs) and posts it to the user.                                                               |


**Flow:** Question → Input (parse, guardrails, context) → Engine (plan, reason, via Semantic Layer ↔ Database) → Output (guardrails, format) → Answer back to Slack.

---

## Key Inputs and Outputs


| Direction | What                                          | Where                               |
| --------- | --------------------------------------------- | ----------------------------------- |
| **In**    | User question (natural language)              | From Slack into the Input subsystem |
| **Out**   | Answer (text, tables, and/or diagrams/graphs) | From Output subsystem back to Slack |


Internal flows: parsed request (Input → Engine), context (Input ↔ Memory, Planner → Memory), schema/data queries (Engine ↔ Semantic Layer ↔ Database), and analysis (Reasoner → Output).

---

## Design Rationale

- **Input and output guardrails** ensure user input is safe and valid, and that answers are checked for safety and accuracy before they are shown in Slack.
- **Memory** keeps conversation context so users can ask follow-ups or provide clarifications without restating everything.
- **Semantic Layer** lets the Engine work with business concepts and metadata instead of raw SQL, improving maintainability and clarity of data access.
- **Separation of Engine (planning + reasoning) and Semantic Layer** makes it easier to change business logic or data definitions without rewriting the core agent flow.
- **Formatter in Output** is responsible for Slack-friendly presentation (text, tables, diagrams/graphs), so the rest of the system stays independent of Slack’s formatting details.

This structure aims to keep the system **modular**, **explainable**, and **reliable** for non-technical users who need fast, trustworthy answers from company data.
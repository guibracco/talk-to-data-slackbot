# Stage 1: generate requirements from poetry.lock (no need to commit requirements.txt)
FROM python:3.11-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && pip freeze > /build/requirements.txt

# Stage 2: runtime image
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY talk_to_data_slackbot/ talk_to_data_slackbot/
COPY pyproject.toml .

CMD ["python", "-m", "talk_to_data_slackbot.main"]

"""
Minimal PandasAI Agent for the Engine.

Configures the LLM from shared config, creates an Agent from Semantic Layer
data sources, and exposes create_agent() and answer_question() as entry points.
"""

from typing import Any

import pandasai as pai
from pandasai import Agent
from pandasai_litellm.litellm import LiteLLM

from talk_to_data_slackbot.llm import get_model_and_api_key
from talk_to_data_slackbot.semantic_layer import get_data_sources


def _configure_llm() -> None:
    """
    Set PandasAI global LLM using shared model and API key (OPENAI_* env).
    """
    model, api_key = get_model_and_api_key()
    llm = LiteLLM(model=model, api_key=api_key)
    pai.config.set({"llm": llm})


def create_agent() -> Agent:
    """
    Create and return a PandasAI Agent with Semantic Layer data sources.

    Configures the global LLM from .env, then instantiates Agent(sources)
    for use with chat() and follow_up().

    Returns
    -------
    Agent
        PandasAI Agent instance; call agent.chat(question) and
        agent.follow_up(question) for conversational use.
    """
    _configure_llm()
    sources = get_data_sources()
    return Agent(sources)


def answer_question(question: str) -> Any:
    """
    One-off entry point: create an agent, run chat(question), return the result.

    For multi-turn conversations, use create_agent() then agent.chat() and
    agent.follow_up() on the same agent instance.

    Parameters
    ----------
    question : str
        Natural-language question about the data.

    Returns
    -------
    Any
        Agent response (string, number, dataframe, or chart depending on question).
    """
    agent = create_agent()
    return agent.chat(question)

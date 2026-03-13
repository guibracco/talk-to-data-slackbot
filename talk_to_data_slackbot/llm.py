"""
Shared LLM configuration and completion.

Single place for OPENAI_API_KEY and OPENAI_MODEL. Used by the engine (PandasAI)
and by input guardrails (scope/PII classifier).
"""

import os
from typing import Any

from dotenv import load_dotenv
import litellm


def get_model_and_api_key() -> tuple[str, str]:
    """
    Load env and return (model, api_key) for OpenAI via LiteLLM.

    Returns
    -------
    tuple of (str, str)
        (OPENAI_MODEL or 'gpt-4o-mini', OPENAI_API_KEY or '').
    """
    load_dotenv()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    return (model, api_key)


def completion(messages: list[dict[str, str]], **kwargs: Any) -> str:
    """
    Single completion using the shared model and API key.

    Parameters
    ----------
    messages : list of dict
        Chat messages with 'role' and 'content' keys (e.g. [{"role": "user", "content": "..."}]).
    **kwargs
        Passed through to litellm.completion (e.g. temperature, max_tokens).

    Returns
    -------
    str
        Content of the assistant reply. Empty string if no content or on error.

    Raises
    ------
    Exception
        Re-raises any exception from litellm.completion (caller may catch and fail open/closed).
    """
    model, api_key = get_model_and_api_key()
    response = litellm.completion(
        model=model,
        messages=messages,
        api_key=api_key,
        **kwargs,
    )
    content = response.choices[0].message.content if response.choices else None
    return (content or "").strip()

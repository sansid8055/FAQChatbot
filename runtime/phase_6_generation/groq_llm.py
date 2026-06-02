"""Groq Chat Completions (OpenAI-compatible API)."""

from __future__ import annotations

import json
import re
from typing import Any

from runtime.phase_6_generation import config


def _extract_json_object(text: str) -> dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
        t = re.sub(r"\s*```$", "", t)
    return json.loads(t)


def groq_chat_json(
    *,
    system: str,
    user: str,
) -> tuple[dict[str, Any], str, str]:
    """
    Call Groq and parse JSON object from assistant message.

    Returns (parsed_dict, raw_content, model_id).
    """
    try:
        from groq import Groq
    except ModuleNotFoundError as e:
        ne = ModuleNotFoundError(
            "No module named 'groq'; install with: pip install groq",
        )
        ne.name = "groq"
        raise ne from e

    key = config.groq_api_key()
    if not key:
        raise ValueError("GROQ_API_KEY is not set")

    client = Groq(api_key=key)
    model = config.groq_model()
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=config.groq_temperature(),
    )
    choice = resp.choices[0]
    content = (choice.message.content or "").strip()
    parsed = _extract_json_object(content)
    return parsed, content, model

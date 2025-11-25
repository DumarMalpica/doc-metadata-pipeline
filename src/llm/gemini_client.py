from __future__ import annotations

import json
import re
from typing import Any, Dict

from google import genai
from config.settings import settings


class GeminiError(RuntimeError):
    pass


def _get_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is not set in environment/.env")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Robustly extract a JSON object from the model response text.
    Handles cases where the model wraps output in ```json ... ``` fences.
    """
    # Try to find a JSON block inside triple backticks
    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fenced_match:
        candidate = fenced_match.group(1)
    else:
        candidate = text.strip()

    # Now try to load JSON; if fails, raise a descriptive error
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise GeminiError(f"Model output is not valid JSON: {e}\nRaw text: {text}") from e


def generate_contract_metadata(json_payload: str) -> Dict[str, Any]:
    """
    Given a JSON payload as string, call Gemini with the metadata prompt and return
    the parsed JSON dict.
    """
    from src.llm.prompt_templates import build_contract_metadata_prompt

    client = _get_client()
    prompt = build_contract_metadata_prompt(json_payload)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    text = response.text or ""
    if not text.strip():
        raise GeminiError("Empty response from Gemini")

    return _extract_json_from_text(text)

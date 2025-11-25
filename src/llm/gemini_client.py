# src/llm/gemini_client.py
from __future__ import annotations

import json
from typing import Any, Dict

import google.generativeai as genai

from src.config.settings import get_settings


class GeminiClient:
    """Thin client around Gemini text or multimodal API."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel(self.settings.gemini_model_name)

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Sends a prompt and expects pure JSON as the response.
        """
        response = self.model.generate_content(prompt)
        text = response.text or ""
        # Basic parse with minimal cleanup. You can harden this later.
        text = text.strip().strip("```json").strip("```").strip()
        return json.loads(text)

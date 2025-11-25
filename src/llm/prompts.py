# src/llm/prompts.py
from __future__ import annotations

from typing import Dict, Any


class PromptBuilder:
    """
    Builds prompts for Gemini to extract structured data from combined context.
    """

    @staticmethod
    def build_extraction_prompt(
        doc_id: str,
        structured_context: Dict[str, Any],
        semantic_snippets: list[str],
        output_instructions: str,
    ) -> str:
        """
        `output_instructions` is where you describe the expected JSON schema.
        """
        return f"""
You are an expert document analysis assistant.

You have a document with id: {doc_id}.

STRUCTURED CONTEXT (from BigQuery):
{structured_context}

SEMANTIC SNIPPETS (from vector search):
{semantic_snippets}

TASK:
Extract ONLY the requested fields, following exactly this specification:

{output_instructions}

Return ONLY valid JSON, no explanations, no markdown.
        """.strip()

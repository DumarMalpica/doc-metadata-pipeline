# src/pipelines/run_llm_insights.py
from __future__ import annotations

from src.llm.orchestrator import LLMOrchestrator


def run_llm_insights(
    doc_id: str,
    profile: str = "default",
) -> dict:
    """
    Runs Gemini-based extraction for a document.
    `profile` can map to different output_instructions and semantic_query.
    """
    # TODO: define profiles mapping somewhere else if needed
    if profile == "default":
        output_instructions = """
Produce JSON with this shape:
{
  "fields": [
    {"name": "contract_number", "value": string, "confidence": float, "source_page": int, "source_snippet": string},
    {"name": "effective_date", "value": string, "confidence": float, "source_page": int, "source_snippet": string}
  ]
}
If a field is not found, omit it.
        """.strip()
        semantic_query = "main contract details such as parties, effective date, and contract number"
    else:
        # Placeholder for custom profiles
        output_instructions = "Produce JSON with a 'fields' array of extracted fields."
        semantic_query = "important key-value fields in the document"

    orchestrator = LLMOrchestrator()
    result = orchestrator.extract_fields_for_doc(
        doc_id=doc_id,
        output_instructions=output_instructions,
        semantic_query=semantic_query,
    )

    return result.model_dump()

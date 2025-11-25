# src/llm/orchestrator.py
from __future__ import annotations

from typing import Any, Dict, List

from src.retrieval.bigquery_reader import BigQueryReader
from src.retrieval.vector_search import VectorSearcher
from src.llm.gemini_client import GeminiClient
from src.llm.prompts import PromptBuilder
from src.llm.schema_output import FinalExtraction, ExtractedField


class LLMOrchestrator:
    """
    Orchestrates querying BigQuery + Chroma and calling Gemini to extract final JSON.
    """

    def __init__(
        self,
        bq_reader: BigQueryReader | None = None,
        vector_searcher: VectorSearcher | None = None,
        gemini_client: GeminiClient | None = None,
    ) -> None:
        self.bq_reader = bq_reader or BigQueryReader()
        self.vector_searcher = vector_searcher or VectorSearcher()
        self.gemini_client = gemini_client or GeminiClient()

    def extract_fields_for_doc(
        self,
        doc_id: str,
        output_instructions: str,
        semantic_query: str,
        k_snippets: int = 8,
    ) -> FinalExtraction:
        # 1) Get structured context
        record = self.bq_reader.get_document_record(doc_id)
        if not record:
            raise ValueError(f"No document record found in BigQuery for doc_id={doc_id}")

        structured_context: Dict[str, Any] = record.get("superjson", {})

        # 2) Get semantic context
        semantic_hits = self.vector_searcher.search_document(doc_id=doc_id, query=semantic_query, k=k_snippets)
        semantic_snippets: List[str] = [hit["text"] for hit in semantic_hits]

        # 3) Build prompt
        prompt = PromptBuilder.build_extraction_prompt(
            doc_id=doc_id,
            structured_context=structured_context,
            semantic_snippets=semantic_snippets,
            output_instructions=output_instructions,
        )

        # 4) Call Gemini
        raw_json = self.gemini_client.generate_json(prompt)

        # 5) Map raw JSON into FinalExtraction schema
        # Expecting something like: {"fields": [{"name": "...", "value": "...", ...}, ...]}
        fields_raw = raw_json.get("fields", [])
        fields = [ExtractedField(**f) for f in fields_raw]

        return FinalExtraction(doc_id=doc_id, fields=fields, extra=raw_json.get("extra", {}))

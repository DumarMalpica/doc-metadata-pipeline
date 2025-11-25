# src/ingestion/extractor_docai.py
from __future__ import annotations

from typing import Any, Dict, Optional

from google.cloud import documentai_v1 as documentai

from src.config.settings import get_settings
from .pdf_loader import PDFDocument


class DocumentAIExtractor:
    """Wrapper for Google Document AI extraction."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us",
        processor_id: str | None = None,
    ) -> None:
        self.settings = get_settings()
        self.project_id = project_id or self.settings.gcp_project
        self.location = location
        self.processor_id = processor_id  # set via config or env
        self._client: Optional[documentai.DocumentProcessorServiceClient] = None

    @property
    def client(self) -> documentai.DocumentProcessorServiceClient:
        if self._client is None:
            self._client = documentai.DocumentProcessorServiceClient()
        return self._client

    def extract(self, pdf: PDFDocument) -> Dict[str, Any]:
        if not self.processor_id:
            raise ValueError("processor_id must be provided for Document AI")

        name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

        raw_document = documentai.RawDocument(
            content=pdf.bytes_content,
            mime_type="application/pdf",
        )

        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document,
        )
        result = self.client.process_document(request=request)
        doc = result.document

        # NOTE: Here we just serialize Document proto to dict; normalizer will handle structure.
        return {
            "tool": "documentai",
            "document": documentai.Document.to_dict(doc),
            "metadata": pdf.metadata.copy(),
        }

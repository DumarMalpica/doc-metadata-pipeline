# src/processing/merger.py
from __future__ import annotations

from typing import List, Dict, Any

from .models import SuperJSON, DocumentMetadata, Page
from .normalizer import (
    PyMuPDFNormalizer,
    PDFPlumberNormalizer,
    DocumentAINormalizer,
)


class SuperJSONMerger:
    """Combines normalized outputs from all extractors into a single SuperJSON."""

    def __init__(self) -> None:
        self.pymupdf_norm = PyMuPDFNormalizer()
        self.pdfplumber_norm = PDFPlumberNormalizer()
        self.docai_norm = DocumentAINormalizer()

    def merge(
        self,
        doc_id: str,
        source_uri: str,
        base_metadata: Dict[str, Any],
        pymupdf_raw: Dict[str, Any] | None,
        pdfplumber_raw: Dict[str, Any] | None,
        docai_raw: Dict[str, Any] | None,
    ) -> SuperJSON:
        pages_by_index: Dict[int, Page] = {}
        tools_used: List[str] = []

        def merge_pages(norm_pages: List[Page]):
            for p in norm_pages:
                if p.index not in pages_by_index:
                    pages_by_index[p.index] = p
                else:
                    # Simple strategy: extend blocks and tables
                    existing = pages_by_index[p.index]
                    existing.blocks.extend(p.blocks)
                    existing.tables.extend(p.tables)

        if pymupdf_raw:
            tools_used.append("pymupdf")
            merge_pages(self.pymupdf_norm.normalize(pymupdf_raw))

        if pdfplumber_raw:
            tools_used.append("pdfplumber")
            merge_pages(self.pdfplumber_norm.normalize(pdfplumber_raw))

        if docai_raw:
            tools_used.append("documentai")
            merge_pages(self.docai_norm.normalize(docai_raw))

        pages = [pages_by_index[i] for i in sorted(pages_by_index.keys())]

        metadata = DocumentMetadata(
            doc_id=doc_id,
            source_uri=source_uri,
            source=base_metadata.get("source"),
            extra=base_metadata,
        )

        return SuperJSON(metadata=metadata, pages=pages, tools_used=tools_used)

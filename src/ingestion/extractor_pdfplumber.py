# src/ingestion/extractor_pdfplumber.py
from __future__ import annotations

from typing import Any, Dict

import pdfplumber

from .pdf_loader import PDFDocument


class PDFPlumberExtractor:
    """Wrapper for PDFPlumber extraction."""

    def extract(self, pdf: PDFDocument) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "tool": "pdfplumber",
            "pages": [],
            "metadata": pdf.metadata.copy(),
        }

        with pdfplumber.open(pdf.bytes_content) as doc:
            for page_index, page in enumerate(doc.pages):
                text = page.extract_text() or ""
                tables = page.extract_tables()
                page_dict = {
                    "page_index": page_index,
                    "text": text,
                    "tables": tables,
                }
                result["pages"].append(page_dict)

        return result

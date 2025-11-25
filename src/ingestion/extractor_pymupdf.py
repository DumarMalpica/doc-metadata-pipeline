# src/ingestion/extractor_pymupdf.py
from __future__ import annotations

from typing import Any, Dict

import fitz  # PyMuPDF

from .pdf_loader import PDFDocument


class PyMuPDFExtractor:
    """Wrapper for PyMuPDF extraction."""

    def extract(self, pdf: PDFDocument) -> Dict[str, Any]:
        """
        Returns a raw dict with pages, text blocks, etc.
        This is a PRE-normalization structure; normalizer will standardize it.
        """
        result: Dict[str, Any] = {
            "tool": "pymupdf",
            "pages": [],
            "metadata": pdf.metadata.copy(),
        }

        doc = fitz.open(stream=pdf.bytes_content, filetype="pdf")
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text")
            blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, text, block_no, ...)
            page_dict = {
                "page_index": page_index,
                "text": text,
                "blocks": blocks,
            }
            result["pages"].append(page_dict)

        return result

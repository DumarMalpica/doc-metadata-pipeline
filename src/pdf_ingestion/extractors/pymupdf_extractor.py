from __future__ import annotations

from typing import Any, Dict, List

import fitz  # PyMuPDF


def extract_with_pymupdf(pdf_path: str) -> Dict[str, Any]:
    """
    Basic text extraction with PyMuPDF.
    For now, we ignore tables and use only text blocks.
    """
    text_spans: List[Dict[str, Any]] = []

    doc = fitz.open(pdf_path)
    for page_index, page in enumerate(doc):
        page_text = page.get_text("text") or ""
        if page_text.strip():
            text_spans.append(
                {
                    "page": page_index + 1,
                    "text": page_text,
                    "bbox": None,
                    "source": "pymupdf",
                }
            )

    return {
        "meta": {
            "num_pages": len(doc),
            "tool": "pymupdf",
        },
        "text_spans": text_spans,
        "tables": [],
    }

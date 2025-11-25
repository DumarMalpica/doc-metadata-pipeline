from __future__ import annotations

from typing import Any, Dict, List

import pdfplumber


def extract_with_pdfplumber(pdf_path: str) -> Dict[str, Any]:
    """
    Basic extraction with pdfplumber.
    Returns a dict with text_spans and tables.
    """
    text_spans: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []

    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        for page_index, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_spans.append(
                    {
                        "page": page_index + 1,
                        "text": page_text,
                        "bbox": None,
                        "source": "pdfplumber",
                    }
                )

            # crude table extraction (if any)
            extracted_tables = page.extract_tables()
            for t in extracted_tables:
                cells = []
                for r_idx, row in enumerate(t):
                    for c_idx, cell_text in enumerate(row):
                        if cell_text is None:
                            continue
                        cells.append(
                            {
                                "row": r_idx,
                                "col": c_idx,
                                "text": cell_text,
                            }
                        )
                if cells:
                    tables.append(
                        {
                            "page": page_index + 1,
                            "cells": cells,
                            "source": "pdfplumber",
                        }
                    )

    return {
        "meta": {
            "num_pages": len(text_spans) and max(ts["page"] for ts in text_spans) or 0,
            "tool": "pdfplumber",
        },
        "text_spans": text_spans,
        "tables": tables,
    }

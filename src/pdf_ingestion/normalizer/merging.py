from __future__ import annotations

from typing import Any, Dict, List


def merge_extractions(
    pdfplumber_data: Dict[str, Any],
    pymupdf_data: Dict[str, Any],
    docai_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    For now we just concatenate text_spans and tables from all tools.
    Later you can add smarter merging / de-duplication.
    """
    all_text_spans: List[Dict[str, Any]] = []
    all_tables: List[Dict[str, Any]] = []

    for data in (pdfplumber_data, pymupdf_data, docai_data):
        all_text_spans.extend(data.get("text_spans", []))
        all_tables.extend(data.get("tables", []))

    num_pages_candidates = []
    for data in (pdfplumber_data, pymupdf_data, docai_data):
        meta = data.get("meta", {})
        if "num_pages" in meta and meta["num_pages"]:
            num_pages_candidates.append(meta["num_pages"])

    num_pages = max(num_pages_candidates) if num_pages_candidates else 0

    merged_meta: Dict[str, Any] = {
        "tools_used": [d.get("meta", {}).get("tool") for d in (pdfplumber_data, pymupdf_data, docai_data)],
        "num_pages": num_pages,
    }

    return {
        "meta": merged_meta,
        "text_spans": all_text_spans,
        "tables": all_tables,
    }

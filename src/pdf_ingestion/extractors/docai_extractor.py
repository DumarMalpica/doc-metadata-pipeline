from __future__ import annotations

from typing import Any, Dict

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
from google.api_core.exceptions import InvalidArgument

from config.settings import settings


def _docai_client() -> documentai.DocumentProcessorServiceClient:
    client_options = ClientOptions(
        api_endpoint=f"{settings.DOC_AI_LOCATION}-documentai.googleapis.com"
    )
    return documentai.DocumentProcessorServiceClient(client_options=client_options)


def _empty_result(reason: str) -> Dict[str, Any]:
    """Return a consistent empty structure when DocAI is skipped or fails."""
    return {
        "meta": {
            "num_pages": 0,
            "tool": "docai",
            "skipped": True,
            "reason": reason,
        },
        "text_spans": [],
        "tables": [],
    }


def process_with_docai(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Calls Google Document AI if configured.
    If configuration is missing or API returns PAGE_LIMIT_EXCEEDED (or any other
    error), we log and return an empty structure so the pipeline can continue
    with pdfplumber / PyMuPDF only.
    """
    # If DocAI is not configured, skip it gracefully
    if not (settings.DOC_AI_PROJECT_ID and settings.DOC_AI_PROCESSOR_ID):
        print("[DocAI] Skipping: DOC_AI_PROJECT_ID or DOC_AI_PROCESSOR_ID not set.")
        return _empty_result("not_configured")

    try:
        client = _docai_client()

        name = client.processor_path(
            settings.DOC_AI_PROJECT_ID,
            settings.DOC_AI_LOCATION,
            settings.DOC_AI_PROCESSOR_ID,
        )

        raw_document = documentai.RawDocument(
            content=pdf_bytes, mime_type="application/pdf"
        )
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        result = client.process_document(request=request)
        doc = result.document

    except InvalidArgument as e:
        # Handle page limit issues and similar parameter errors
        if "PAGE_LIMIT_EXCEEDED" in str(e):
            print(f"[DocAI] Skipping due to page limit: {e}")
            return _empty_result("page_limit_exceeded")
        print(f"[DocAI] InvalidArgument, skipping DocAI: {e}")
        return _empty_result("invalid_argument")
    except Exception as e:
        # Any other unexpected error -> log and skip
        print(f"[DocAI] Unexpected error, skipping DocAI: {e}")
        return _empty_result("unexpected_error")

    # If we reach here, DocAI worked
    text_spans = []
    tables = []

    # Simple pass: whole document text as one span
    if doc.text:
        text_spans.append(
            {
                "page": 1,
                "text": doc.text,
                "bbox": None,
                "source": "docai",
            }
        )

    num_pages = len(doc.pages)

    # Minimal table parsing
    for page_index, page in enumerate(doc.pages):
        for table in page.tables:
            cells = []
            # header_rows + body_rows
            all_rows = list(table.header_rows) + list(table.body_rows)
            for r_idx, row in enumerate(all_rows):
                for c_idx, cell in enumerate(row.cells):
                    # Some layouts might not have text_anchor.content populated
                    cell_text = ""
                    if cell.layout and cell.layout.text_anchor:
                        cell_text = cell.layout.text_anchor.content or ""
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
                        "source": "docai",
                    }
                )

    return {
        "meta": {
            "num_pages": num_pages,
            "tool": "docai",
            "skipped": False,
        },
        "text_spans": text_spans,
        "tables": tables,
    }

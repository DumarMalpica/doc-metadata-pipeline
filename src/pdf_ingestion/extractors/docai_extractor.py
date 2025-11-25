from __future__ import annotations

from typing import Any, Dict

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai

from config.settings import settings


def _docai_client() -> documentai.DocumentProcessorServiceClient:
    client_options = ClientOptions(api_endpoint=f"{settings.DOC_AI_LOCATION}-documentai.googleapis.com")
    return documentai.DocumentProcessorServiceClient(client_options=client_options)


def process_with_docai(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Calls Google Document AI if configured, otherwise returns an empty result.
    """
    if not (settings.DOC_AI_PROJECT_ID and settings.DOC_AI_PROCESSOR_ID):
        # Not configured; return empty structure
        return {
            "meta": {
                "num_pages": 0,
                "tool": "docai",
                "skipped": True,
            },
            "text_spans": [],
            "tables": [],
        }

    name = _docai_client().processor_path(
        settings.DOC_AI_PROJECT_ID,
        settings.DOC_AI_LOCATION,
        settings.DOC_AI_PROCESSOR_ID,
    )

    raw_document = documentai.RawDocument(content=pdf_bytes, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    client = _docai_client()
    result = client.process_document(request=request)
    doc = result.document

    text_spans = []
    tables = []

    # Simple pass: use full doc text as one span, plus page count
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

    # Table parsing – minimal example
    for page_index, page in enumerate(doc.pages):
        for table in page.tables:
            cells = []
            for r_idx, row in enumerate(table.header_rows + table.body_rows):
                for c_idx, cell in enumerate(row.cells):
                    cells.append(
                        {
                            "row": r_idx,
                            "col": c_idx,
                            "text": cell.layout.text_anchor.content or "",
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
        },
        "text_spans": text_spans,
        "tables": tables,
    }

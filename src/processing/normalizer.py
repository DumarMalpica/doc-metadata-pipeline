# src/processing/normalizer.py
from __future__ import annotations

import uuid
from typing import Any, Dict, List

from .models import (
    BoundingBox,
    Page,
    Table,
    TableCell,
    TextBlock,
)


class PyMuPDFNormalizer:
    """Normalizes raw PyMuPDF extraction into Page/Block/Table structures."""

    def normalize(self, raw: Dict[str, Any]) -> List[Page]:
        pages: List[Page] = []
        tool = raw.get("tool", "pymupdf")

        for p in raw.get("pages", []):
            page_index: int = p["page_index"]
            blocks_raw = p.get("blocks", [])
            blocks: List[TextBlock] = []
            for b in blocks_raw:
                # PyMuPDF blocks: (x0, y0, x1, y1, text, block_no, ...)
                x0, y0, x1, y1, text, *_ = b
                blocks.append(
                    TextBlock(
                        id=str(uuid.uuid4()),
                        page_index=page_index,
                        text=text or "",
                        bbox=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1),
                        tool=tool,
                    )
                )

            page = Page(
                index=page_index,
                text=p.get("text", ""),
                blocks=blocks,
                tables=[],
            )
            pages.append(page)

        return pages


class PDFPlumberNormalizer:
    """Normalizes raw PDFPlumber extraction into Page/Block/Table structures."""

    def normalize(self, raw: Dict[str, Any]) -> List[Page]:
        pages: List[Page] = []
        tool = raw.get("tool", "pdfplumber")

        for p in raw.get("pages", []):
            page_index: int = p["page_index"]
            text = p.get("text", "") or ""
            blocks: List[TextBlock] = []

            if text:
                blocks.append(
                    TextBlock(
                        id=str(uuid.uuid4()),
                        page_index=page_index,
                        text=text,
                        bbox=None,
                        tool=tool,
                    )
                )

            tables: List[Table] = []
            for tbl_idx, table_raw in enumerate(p.get("tables", [])):
                cells: List[TableCell] = []
                for row_idx, row in enumerate(table_raw):
                    for col_idx, cell_text in enumerate(row):
                        cells.append(
                            TableCell(
                                row=row_idx,
                                col=col_idx,
                                text=cell_text or "",
                                bbox=None,
                            )
                        )
                tables.append(
                    Table(
                        id=f"{tool}_p{page_index}_t{tbl_idx}",
                        page_index=page_index,
                        cells=cells,
                        tool=tool,
                    )
                )

            pages.append(Page(index=page_index, text=text, blocks=blocks, tables=tables))

        return pages


class DocumentAINormalizer:
    """Normalizes raw Document AI dict into Page/Block/Table structures."""

    def normalize(self, raw: Dict[str, Any]) -> List[Page]:
        # TODO: interpret Document AI structure properly.
        # For now, return an empty list to be extended.
        # You will parse raw["document"]["pages"], paragraphs, tables, etc.
        return []

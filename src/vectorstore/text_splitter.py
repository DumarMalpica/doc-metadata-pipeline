# src/vectorstore/text_splitter.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.processing.models import SuperJSON, Page


@dataclass
class TextChunk:
    id: str
    doc_id: str
    page_index: int
    text: str
    metadata: Dict[str, str]


class SimpleTextSplitter:
    """
    Very basic splitter: one chunk per block, plus page-level text if needed.
    Replace with smarter splitter later.
    """

    def split(self, doc: SuperJSON) -> List[TextChunk]:
        chunks: List[TextChunk] = []

        for page in doc.pages:
            chunks.extend(self._chunks_from_page(doc.metadata.doc_id, page))

        return chunks

    def _chunks_from_page(self, doc_id: str, page: Page) -> List[TextChunk]:
        from uuid import uuid4

        chunks: List[TextChunk] = []

        for block in page.blocks:
            text = (block.text or "").strip()
            if not text:
                continue
            chunks.append(
                TextChunk(
                    id=str(uuid4()),
                    doc_id=doc_id,
                    page_index=page.index,
                    text=text,
                    metadata={
                        "doc_id": doc_id,
                        "page_index": str(page.index),
                        "tool": block.tool,
                    },
                )
            )

        return chunks

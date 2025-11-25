# src/retrieval/vector_search.py
from __future__ import annotations

from typing import Any, Dict, List

from src.vectorstore.chroma_client import ChromaVectorStore


class VectorSearcher:
    """Facilitates semantic search over ChromaDB."""

    def __init__(self, store: ChromaVectorStore | None = None) -> None:
        self.store = store or ChromaVectorStore()

    def search_document(self, doc_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        results = self.store.query(
            query_text=query,
            n_results=k,
            where={"doc_id": doc_id},
        )
        return [
            {"id": chunk_id, "text": text, "metadata": meta}
            for chunk_id, text, meta in results
        ]

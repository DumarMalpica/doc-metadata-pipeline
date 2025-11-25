# src/vectorstore/chroma_client.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import chromadb

from src.config.settings import get_settings
from .text_splitter import TextChunk
from .embeddings import EmbeddingsClient


class ChromaVectorStore:
    """Wrapper around ChromaDB for storing and querying document chunks."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self.client = chromadb.PersistentClient(path=self.settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma_collection_name
        )
        self.embeddings_client = EmbeddingsClient()

    def upsert_chunks(self, chunks: List[TextChunk]) -> None:
        texts = [c.text for c in chunks]
        embeddings = self.embeddings_client.embed_documents(texts)

        self.collection.upsert(
            ids=[c.id for c in chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[c.metadata for c in chunks],
        )

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Dict[str, Any] | None = None,
    ) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Returns list of (id, text, metadata)
        """
        resp = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        ids = resp["ids"][0]
        docs = resp["documents"][0]
        metas = resp["metadatas"][0]
        return list(zip(ids, docs, metas))

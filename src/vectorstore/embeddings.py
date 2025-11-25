# src/vectorstore/embeddings.py
from __future__ import annotations

from typing import List

# Placeholder: you can plug Gemini embeddings or other provider here.


class EmbeddingsClient:
    """Responsible for converting text into embedding vectors."""

    def __init__(self) -> None:
        # Initialize client for embeddings provider if needed
        pass

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Given list of texts, return list of embedding vectors.
        TODO: implement using Gemini or another embedding model.
        """
        raise NotImplementedError("Implement embed_documents with your provider")

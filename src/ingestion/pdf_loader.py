# src/ingestion/pdf_loader.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from google.cloud import storage

from src.config.settings import get_settings


@dataclass
class PDFDocument:
    doc_id: str
    bytes_content: bytes
    source_uri: str
    metadata: Dict[str, Any]


class PDFLoader:
    """Loads PDF bytes from local FS or GCS."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self._gcs_client: Optional[storage.Client] = None

    @property
    def gcs_client(self) -> storage.Client:
        if self._gcs_client is None:
            self._gcs_client = storage.Client(project=self.settings.gcp_project)
        return self._gcs_client

    def load_from_local(self, path: str | Path, doc_id: str) -> PDFDocument:
        p = Path(path)
        content = p.read_bytes()
        return PDFDocument(
            doc_id=doc_id,
            bytes_content=content,
            source_uri=str(p.resolve()),
            metadata={"source": "local", "filename": p.name},
        )

    def load_from_gcs(self, gcs_uri: str, doc_id: str) -> PDFDocument:
        """
        gcs_uri example: gs://bucket/path/to/file.pdf
        """
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")

        _, remainder = gcs_uri.split("gs://", 1)
        bucket_name, blob_name = remainder.split("/", 1)

        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        content = blob.download_as_bytes()

        return PDFDocument(
            doc_id=doc_id,
            bytes_content=content,
            source_uri=gcs_uri,
            metadata={"source": "gcs", "bucket": bucket_name, "blob": blob_name},
        )

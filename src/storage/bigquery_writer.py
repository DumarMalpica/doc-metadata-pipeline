# src/storage/bigquery_writer.py
from __future__ import annotations

from typing import Dict, Any

from .bigquery_client import BigQueryClient
from src.processing.models import SuperJSON
from src.config.settings import get_settings


class SuperJSONWriter:
    """Persists SuperJSON into BigQuery as a raw JSON record."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self.bq = BigQueryClient(settings=self.settings)

    def write_raw(self, superjson: SuperJSON) -> None:
        row: Dict[str, Any] = {
            "doc_id": superjson.metadata.doc_id,
            "source_uri": superjson.metadata.source_uri,
            "version": superjson.version,
            "tools_used": superjson.tools_used,
            "superjson": superjson.model_dump(),  # store as JSON column
        }
        self.bq.insert_json_rows(self.settings.bigquery_raw_table, [row])

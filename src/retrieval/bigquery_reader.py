# src/retrieval/bigquery_reader.py
from __future__ import annotations

from typing import Any, Dict

from src.storage.bigquery_client import BigQueryClient
from src.config.settings import get_settings


class BigQueryReader:
    """High-level queries for structured info from SuperJSON table."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self.bq = BigQueryClient(settings=self.settings)

    def get_document_record(self, doc_id: str) -> Dict[str, Any] | None:
        sql = f"""
        SELECT *
        FROM `{self.settings.gcp_project}.{self.settings.bigquery_dataset}.{self.settings.bigquery_raw_table}`
        WHERE doc_id = @doc_id
        ORDER BY version DESC
        LIMIT 1
        """
        # For brevity, no query params implemented here; you can extend BigQueryClient
        sql = sql.replace("@doc_id", f"'{doc_id}'")
        rows = self.bq.query(sql)
        return rows[0] if rows else None

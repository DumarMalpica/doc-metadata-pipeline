# src/storage/bigquery_client.py
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from google.cloud import bigquery

from src.config.settings import get_settings


class BigQueryClient:
    """Thin wrapper over google-cloud-bigquery for inserts/queries."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self.client = bigquery.Client(project=self.settings.gcp_project)

    def table_ref(self, table_name: str) -> bigquery.TableReference:
        return self.client.dataset(self.settings.bigquery_dataset).table(table_name)

    def insert_json_rows(
        self,
        table_name: str,
        rows: Iterable[Dict[str, Any]],
    ) -> None:
        table = self.table_ref(table_name)
        errors = self.client.insert_rows_json(table, list(rows))
        if errors:
            raise RuntimeError(f"BigQuery insert errors: {errors}")

    def query(self, sql: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        job_config = bigquery.QueryJobConfig()
        if params:
            # Optionally implement query parameters here
            pass
        query_job = self.client.query(sql, job_config=job_config)
        return [dict(row) for row in query_job]

from __future__ import annotations

from typing import Any, Dict, Optional

from google.cloud import bigquery

from config.settings import settings
from src.storage.bigquery_client import get_bq_client


def get_super_json_record(doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single record from super_json_docs by doc_id.
    Returns a dict with keys: doc_id, filename, super_json.
    """
    client: bigquery.Client = get_bq_client()

    dataset = settings.BQ_DATASET
    table = settings.BQ_TABLE
    project = settings.GCP_PROJECT_ID

    table_ref = f"`{project}.{dataset}.{table}`"

    query = f"""
        SELECT doc_id, filename, super_json
        FROM {table_ref}
        WHERE doc_id = @doc_id
        LIMIT 1
    """

    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("doc_id", "STRING", doc_id),
            ]
        ),
    )

    rows = list(job.result())
    if not rows:
        return None

    row = rows[0]
    return {
        "doc_id": row["doc_id"],
        "filename": row["filename"],
        "super_json": row["super_json"],  # stored as STRING
    }

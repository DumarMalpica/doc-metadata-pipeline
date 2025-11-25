from __future__ import annotations

from typing import Any, Dict

from google.cloud import bigquery

from config.settings import settings


def get_bq_client() -> bigquery.Client:
    if not settings.GCP_PROJECT_ID:
        raise RuntimeError("GCP_PROJECT_ID is not set in environment.")
    return bigquery.Client(project=settings.GCP_PROJECT_ID)


def ensure_super_json_table_exists() -> None:
    client = get_bq_client()
    dataset_id = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}"
    table_id = f"{dataset_id}.{settings.BQ_TABLE}"

    # Create dataset if not exists
    try:
        client.get_dataset(dataset_id)
    except Exception:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)

    # Try to get table; if it exists, we assume schema is fine and return
    try:
        client.get_table(table_id)
        return
    except Exception:
        pass

    # New table schema:
    # - doc_id: string
    # - source_path: string
    # - filename: string
    # - super_json: string (JSON serialized)
    schema = [
        bigquery.SchemaField("doc_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_path", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("super_json", "STRING", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table, exists_ok=True)


def insert_super_json_row(row: Dict[str, Any]) -> None:
    client = get_bq_client()
    dataset_id = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}"
    table_id = f"{dataset_id}.{settings.BQ_TABLE}"

    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"Error inserting rows into BigQuery: {errors}")

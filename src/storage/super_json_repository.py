from __future__ import annotations

import json

from src.models.super_json_schema import SuperJSON
from src.storage.bigquery_client import (
    ensure_super_json_table_exists,
    insert_super_json_row,
)


def save_super_json_to_bq(super_json: SuperJSON) -> None:
    """
    Save SuperJSON into BigQuery.
    If GCP is not configured, we skip gracefully.
    """
    try:
        ensure_super_json_table_exists()
    except RuntimeError as e:
        # BigQuery not configured → just log and skip
        print(f"[BQ] Skipping BigQuery storage: {e}")
        return

    row = {
        "doc_id": super_json.doc_id,
        "source_path": super_json.source_path,
        "filename": super_json.filename,
        # Store the entire structure as a JSON string
        "super_json": json.dumps(super_json.model_dump(), ensure_ascii=False),
    }

    try:
        insert_super_json_row(row)
    except RuntimeError as e:
        print(f"[BQ] Error inserting row into BigQuery, skipping: {e}")

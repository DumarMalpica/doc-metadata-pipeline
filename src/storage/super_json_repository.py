from __future__ import annotations

from src.models.super_json_schema import SuperJSON
from src.storage.bigquery_client import ensure_super_json_table_exists, insert_super_json_row


def save_super_json_to_bq(super_json: SuperJSON) -> None:
    ensure_super_json_table_exists()

    row = {
        "doc_id": super_json.doc_id,
        "source_path": super_json.source_path,
        "filename": super_json.filename,
        # BigQuery JSON field can take a dict
        "super_json": super_json.model_dump(),
    }

    insert_super_json_row(row)

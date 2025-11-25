from __future__ import annotations

import datetime
import json

from typing import Any, Dict, Optional, List

from google.cloud import bigquery

from config.settings import settings
from src.storage.bigquery_client import get_bq_client


def ensure_contract_metadata_table_exists() -> None:
    """
    Create pdf_processing.contract_metadata if it does not exist.
    Stores flattened fields + the raw JSON.
    """
    client: bigquery.Client = get_bq_client()

    dataset_id = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}"
    table_id = f"{dataset_id}.contract_metadata"

    # Ensure dataset exists
    try:
        client.get_dataset(dataset_id)
    except Exception:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)

    # Check table
    try:
        client.get_table(table_id)
        return
    except Exception:
        pass

    schema = [
        bigquery.SchemaField("doc_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("llm_model", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),

        bigquery.SchemaField("supplier_legal_name", "STRING"),
        bigquery.SchemaField("supplier_names", "STRING"),
        bigquery.SchemaField("sap_contract_number", "STRING"),
        bigquery.SchemaField("scipartner", "STRING"),
        bigquery.SchemaField("effective_date", "STRING"),
        bigquery.SchemaField("agreement_type", "STRING"),
        bigquery.SchemaField("agreement_names", "STRING"),
        bigquery.SchemaField("parent_document", "STRING"),
        bigquery.SchemaField("document_type", "STRING"),
        bigquery.SchemaField("is_evergreen", "BOOL"),
        bigquery.SchemaField("expiration_date", "STRING"),
        bigquery.SchemaField("sap_supplier", "STRING"),
        bigquery.SchemaField("document_url", "STRING"),
        bigquery.SchemaField("file_name", "STRING"),
        bigquery.SchemaField("expiration_email_recipients", "STRING", mode="REPEATED"),
        bigquery.SchemaField("mime_type", "STRING"),
        bigquery.SchemaField("file_source_url", "STRING"),

        bigquery.SchemaField("raw_metadata_json", "STRING", mode="REQUIRED"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table, exists_ok=True)


def insert_contract_metadata_row(
    doc_id: str,
    filename: str,
    llm_model: str,
    metadata: Dict[str, Any],
) -> None:
    """
    Flatten the metadata dict into columns and insert into contract_metadata table.
    """
    client: bigquery.Client = get_bq_client()
    ensure_contract_metadata_table_exists()

    dataset_id = f"{settings.GCP_PROJECT_ID}.{settings.BQ_DATASET}"
    table_id = f"{dataset_id}.contract_metadata"

    # Helper to safely get keys
    def g(key: str, default=None):
        return metadata.get(key, default)

    # expiration_email_recipients should be a list; if not, coerce
    recipients = g("expiration_email_recipients")
    if recipients is None:
        recipients_list: Optional[List[str]] = None
    elif isinstance(recipients, list):
        recipients_list = [str(x) for x in recipients]
    else:
        recipients_list = [str(recipients)]

    # is_evergreen: convert to bool or None
    is_evergreen_val = g("is_evergreen")
    if isinstance(is_evergreen_val, bool):
        is_evergreen = is_evergreen_val
    elif is_evergreen_val in ("true", "True", "TRUE", 1):
        is_evergreen = True
    elif is_evergreen_val in ("false", "False", "FALSE", 0):
        is_evergreen = False
    elif is_evergreen_val is None:
        is_evergreen = None
    else:
        # unknown type -> store as None in BOOL column
        is_evergreen = None

    row = {
        "doc_id": doc_id,
        "filename": filename,
        "llm_model": llm_model,
        "created_at": datetime.datetime.utcnow().isoformat(),

        "supplier_legal_name": g("supplier_legal_name"),
        "supplier_names": g("supplier_names"),
        "sap_contract_number": g("sap_contract_number"),
        "scipartner": g("scipartner"),
        "effective_date": g("effective_date"),
        "agreement_type": g("agreement_type"),
        "agreement_names": g("agreement_names"),
        "parent_document": g("parent_document"),
        "document_type": g("document_type"),
        "is_evergreen": is_evergreen,
        "expiration_date": g("expiration_date"),
        "sap_supplier": g("sap_supplier"),
        "document_url": g("document_url"),
        "file_name": g("file_name"),
        "expiration_email_recipients": recipients_list,
        "mime_type": g("mime_type"),
        "file_source_url": g("file_source_url"),

        "raw_metadata_json": json.dumps(metadata, ensure_ascii=False),
    }

    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"Error inserting contract metadata into BigQuery: {errors}")

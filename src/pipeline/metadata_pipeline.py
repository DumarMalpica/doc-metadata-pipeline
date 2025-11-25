from __future__ import annotations

from typing import Dict, Any

from config.settings import settings
from src.storage.super_json_reader import get_super_json_record
from src.llm.gemini_client import generate_contract_metadata, GeminiError
from src.storage.contract_metadata_repository import insert_contract_metadata_row


def extract_and_store_contract_metadata(doc_id: str) -> Dict[str, Any]:
    """
    Step 2 main function:
    - Reads JSON (super_json) from BigQuery for the given doc_id
    - Sends it to Gemini with the contract metadata prompt
    - Parses the normalized JSON
    - Stores result in contract_metadata table
    - Returns the metadata dict
    """
    record = get_super_json_record(doc_id)
    if record is None:
        raise RuntimeError(f"No record found in {settings.BQ_TABLE} for doc_id={doc_id}")

    json_payload = record["super_json"]  # string
    filename = record["filename"]

    # Call Gemini
    try:
        metadata = generate_contract_metadata(json_payload)
    except GeminiError as e:
        raise RuntimeError(f"Gemini error while processing doc_id={doc_id}: {e}") from e

    # Insert into BigQuery
    insert_contract_metadata_row(
        doc_id=record["doc_id"],
        filename=filename,
        llm_model=settings.GEMINI_MODEL,
        metadata=metadata,
    )

    return metadata

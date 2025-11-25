from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Tuple

from src.pdf_ingestion.extractors.pdfplumber_extractor import extract_with_pdfplumber
from src.pdf_ingestion.extractors.pymupdf_extractor import extract_with_pymupdf
from src.pdf_ingestion.extractors.docai_extractor import process_with_docai
from src.pdf_ingestion.normalizer.merging import merge_extractions
from src.pdf_ingestion.normalizer.builders import build_super_json
from src.pdf_ingestion.loaders import ensure_dir, get_processed_json_path
from src.models.super_json_schema import SuperJSON
from src.storage.super_json_repository import save_super_json_to_bq


def run_extraction(pdf_path: str) -> Tuple[dict, dict, dict]:
    pdfplumber_data = extract_with_pdfplumber(pdf_path)
    pymupdf_data = extract_with_pymupdf(pdf_path)

    # Read bytes for DocAI
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    docai_data = process_with_docai(pdf_bytes)

    return pdfplumber_data, pymupdf_data, docai_data


def build_and_store_super_json(
    pdf_path: str,
    processed_dir: str,
    to_bigquery: bool = True,
) -> SuperJSON:
    # Generate ID from filename + UUID
    filename = Path(pdf_path).name
    base_name = Path(pdf_path).stem
    doc_id = f"{base_name}-{uuid.uuid4().hex[:8]}"

    pdfplumber_data, pymupdf_data, docai_data = run_extraction(pdf_path)
    merged = merge_extractions(pdfplumber_data, pymupdf_data, docai_data)

    super_json = build_super_json(
        merged_data=merged,
        doc_id=doc_id,
        filename=filename,
        source_path=str(Path(pdf_path).resolve()),
    )

    # Save to local processed JSON
    ensure_dir(processed_dir)
    out_path = get_processed_json_path(processed_dir, doc_id)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(super_json.model_dump(), f, ensure_ascii=False, indent=2)

    # Save to BigQuery
    if to_bigquery:
        save_super_json_to_bq(super_json)

    return super_json

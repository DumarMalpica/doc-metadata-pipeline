from __future__ import annotations

from pathlib import Path
from typing import List

from config.settings import settings
from src.pdf_ingestion.loaders import list_pdfs, ensure_dir
from src.pipeline.steps import build_and_store_super_json


def process_single_pdf(pdf_path: str, to_bigquery: bool = True) -> None:
    processed_dir = str(Path("data") / "processed")
    ensure_dir(processed_dir)
    build_and_store_super_json(pdf_path, processed_dir=processed_dir, to_bigquery=to_bigquery)


def process_batch(input_dir: str, to_bigquery: bool = True) -> None:
    processed_dir = str(Path("data") / "processed")
    ensure_dir(processed_dir)

    pdf_files: List[Path] = list_pdfs(input_dir)
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path}")
        build_and_store_super_json(str(pdf_path), processed_dir=processed_dir, to_bigquery=to_bigquery)
        print(f"  ✔ Done {pdf_path.name}")

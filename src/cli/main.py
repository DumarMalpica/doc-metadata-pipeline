from __future__ import annotations

import argparse
import json

from src.pipeline.run_pipeline import process_single_pdf, process_batch
from src.pipeline.metadata_pipeline import extract_and_store_contract_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF processing pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Step 1: process single pdf
    single = subparsers.add_parser("process-pdf", help="Process a single PDF")
    single.add_argument("--input", required=True, help="Path to input PDF")
    single.add_argument(
        "--no-bq",
        action="store_true",
        help="Do not send data to BigQuery (only local JSON)",
    )

    # Step 1: process batch
    batch = subparsers.add_parser("process-batch", help="Process all PDFs in a folder")
    batch.add_argument("--input-dir", required=True, help="Path to folder with PDFs")
    batch.add_argument(
        "--no-bq",
        action="store_true",
        help="Do not send data to BigQuery (only local JSON)",
    )

    # Step 2: extract normalized metadata via Gemini and save to BigQuery
    meta = subparsers.add_parser(
        "extract-metadata",
        help="Extract contract metadata from BigQuery JSON via Gemini",
    )
    meta.add_argument(
        "--doc-id",
        required=True,
        help="doc_id of the record in super_json_docs",
    )
    meta.add_argument(
        "--print",
        action="store_true",
        help="Print resulting JSON to stdout",
    )

    args = parser.parse_args()

    if args.command == "process-pdf":
        process_single_pdf(args.input, to_bigquery=not args.no_bq)

    elif args.command == "process-batch":
        process_batch(args.input_dir, to_bigquery=not args.no_bq)

    elif args.command == "extract-metadata":
        metadata = extract_and_store_contract_metadata(args.doc_id)
        if args.print:
            print(json.dumps(metadata, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

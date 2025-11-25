from __future__ import annotations

import argparse

from src.pipeline.run_pipeline import process_single_pdf, process_batch


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF → SuperJSON → BigQuery pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # process single pdf
    single = subparsers.add_parser("process-pdf", help="Process a single PDF")
    single.add_argument("--input", required=True, help="Path to input PDF")
    single.add_argument(
        "--no-bq",
        action="store_true",
        help="Do not send data to BigQuery (only local JSON)",
    )

    # process batch
    batch = subparsers.add_parser("process-batch", help="Process all PDFs in a folder")
    batch.add_argument("--input-dir", required=True, help="Path to folder with PDFs")
    batch.add_argument(
        "--no-bq",
        action="store_true",
        help="Do not send data to BigQuery (only local JSON)",
    )

    args = parser.parse_args()

    if args.command == "process-pdf":
        process_single_pdf(args.input, to_bigquery=not args.no_bq)
    elif args.command == "process-batch":
        process_batch(args.input_dir, to_bigquery=not args.no_bq)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

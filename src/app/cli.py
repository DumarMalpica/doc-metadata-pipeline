# src/app/cli.py
from __future__ import annotations

import click

from src.pipelines.run_ingestion import run_ingestion
from src.pipelines.run_llm_insights import run_llm_insights


@click.group()
def cli() -> None:
    """Document processing pipeline CLI."""
    pass


@cli.command()
@click.argument("doc_uri")
@click.option("--doc-id", required=True, help="Unique id for the document.")
@click.option("--use-gcs", is_flag=True, default=False, help="Treat doc_uri as a GCS URI.")
@click.option("--docai-processor-id", default=None, help="Document AI processor id.")
def ingest(doc_uri: str, doc_id: str, use_gcs: bool, docai_processor_id: str | None) -> None:
    """Run the ingestion pipeline for a PDF."""
    run_ingestion(
        doc_uri=doc_uri,
        doc_id=doc_id,
        use_gcs=use_gcs,
        docai_processor_id=docai_processor_id,
    )
    click.echo(f"Ingestion finished for doc_id={doc_id}")


@cli.command()
@click.argument("doc_id")
@click.option("--profile", default="default", help="Extraction profile name.")
def insights(doc_id: str, profile: str) -> None:
    """Run LLM insights extraction for a document."""
    result = run_llm_insights(doc_id=doc_id, profile=profile)
    click.echo(result)


if __name__ == "__main__":
    cli()

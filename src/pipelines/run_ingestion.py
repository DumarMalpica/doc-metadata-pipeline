# src/pipelines/run_ingestion.py
from __future__ import annotations

from typing import Optional

from src.ingestion.pdf_loader import PDFLoader
from src.ingestion.extractor_pymupdf import PyMuPDFExtractor
from src.ingestion.extractor_pdfplumber import PDFPlumberExtractor
from src.ingestion.extractor_docai import DocumentAIExtractor
from src.processing.merger import SuperJSONMerger
from src.storage.bigquery_writer import SuperJSONWriter
from src.vectorstore.text_splitter import SimpleTextSplitter
from src.vectorstore.chroma_client import ChromaVectorStore


def run_ingestion(
    doc_uri: str,
    doc_id: str,
    use_gcs: bool = False,
    docai_processor_id: Optional[str] = None,
) -> None:
    """
    End-to-end ingestion for a single PDF:
    PDF -> extractors -> SuperJSON -> BigQuery + Chroma.
    """
    loader = PDFLoader()

    if use_gcs:
        pdf = loader.load_from_gcs(doc_uri, doc_id=doc_id)
    else:
        pdf = loader.load_from_local(doc_uri, doc_id=doc_id)

    # --- Run extractors ---
    pymupdf_raw = PyMuPDFExtractor().extract(pdf)
    pdfplumber_raw = PDFPlumberExtractor().extract(pdf)

    docai_raw = None
    if docai_processor_id:
        docai_raw = DocumentAIExtractor(processor_id=docai_processor_id).extract(pdf)

    # --- Merge into SuperJSON ---
    merger = SuperJSONMerger()
    superjson = merger.merge(
        doc_id=doc_id,
        source_uri=pdf.source_uri,
        base_metadata=pdf.metadata,
        pymupdf_raw=pymupdf_raw,
        pdfplumber_raw=pdfplumber_raw,
        docai_raw=docai_raw,
    )

    # --- Store SuperJSON in BigQuery ---
    writer = SuperJSONWriter()
    writer.write_raw(superjson)

    # --- Vectorize and store in Chroma ---
    splitter = SimpleTextSplitter()
    chunks = splitter.split(superjson)

    store = ChromaVectorStore()
    store.upsert_chunks(chunks)

# src/config/settings.py
from __future__ import annotations

from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # --- GCP / BigQuery ---
    gcp_project: str = Field(..., env="GCP_PROJECT")
    bigquery_dataset: str = Field(..., env="BIGQUERY_DATASET")
    bigquery_raw_table: str = Field("documents_raw", env="BIGQUERY_RAW_TABLE")

    # Optional: where raw PDFs or SuperJSONs are stored
    gcs_bucket: str | None = Field(None, env="GCS_BUCKET")

    # --- Vector store / Chroma ---
    chroma_persist_dir: str = Field("./chroma_data", env="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field("documents", env="CHROMA_COLLECTION_NAME")

    # --- LLM / Gemini ---
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model_name: str = Field("gemini-1.5-pro", env="GEMINI_MODEL_NAME")

    # --- General ---
    environment: str = Field("dev", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

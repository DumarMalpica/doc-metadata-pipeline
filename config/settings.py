import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class Settings:
    # General
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # GCP / BigQuery
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    BQ_DATASET: str = os.getenv("BQ_DATASET", "pdf_processing")
    BQ_TABLE: str = os.getenv("BQ_TABLE", "super_json_docs")

    # Document AI (optional)
    DOC_AI_PROJECT_ID: str = os.getenv("DOC_AI_PROJECT_ID", "")
    DOC_AI_LOCATION: str = os.getenv("DOC_AI_LOCATION", "us")
    DOC_AI_PROCESSOR_ID: str = os.getenv("DOC_AI_PROCESSOR_ID", "")


settings = Settings()

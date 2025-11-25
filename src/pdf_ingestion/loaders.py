from __future__ import annotations

import os
from pathlib import Path
from typing import List


def list_pdfs(raw_dir: str) -> List[Path]:
    """Return all PDF files under data/raw (non-recursive for now)."""
    p = Path(raw_dir)
    return [f for f in p.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def get_processed_json_path(processed_dir: str, doc_id: str) -> Path:
    return Path(processed_dir) / f"{doc_id}.json"

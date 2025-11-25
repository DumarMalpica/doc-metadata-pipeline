# src/llm/schema_output.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ExtractedField(BaseModel):
    name: str
    value: Any
    confidence: Optional[float] = None
    source_page: Optional[int] = None
    source_snippet: Optional[str] = None


class FinalExtraction(BaseModel):
    """
    Example final JSON schema.
    Adapt this to your real field list.
    """
    doc_id: str
    fields: List[ExtractedField]
    extra: Dict[str, Any] = {}

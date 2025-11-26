from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TextSpan(BaseModel):
    page: int
    text: str
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1] if available
    source: str = Field(..., description="Which extractor produced this text span")


class TableCell(BaseModel):
    row: int
    col: int
    text: str


class Table(BaseModel):
    page: int
    cells: List[TableCell]
    source: str


class SuperJSON(BaseModel):
    doc_id: str
    filename: str
    source_path: str
    num_pages: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    text_spans: List[TextSpan] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)

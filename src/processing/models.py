# src/processing/models.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class TextBlock(BaseModel):
    id: str
    page_index: int
    text: str
    bbox: Optional[BoundingBox] = None
    tool: str
    extra: Dict[str, Any] = Field(default_factory=dict)


class TableCell(BaseModel):
    row: int
    col: int
    text: str
    bbox: Optional[BoundingBox] = None


class Table(BaseModel):
    id: str
    page_index: int
    cells: List[TableCell]
    tool: str
    extra: Dict[str, Any] = Field(default_factory=dict)


class Page(BaseModel):
    index: int
    text: str = ""          # Full concatenated text
    blocks: List[TextBlock] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    doc_id: str
    source_uri: str
    source: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class SuperJSON(BaseModel):
    """
    Canonical representation of a PDF after merging all extractors.
    """
    metadata: DocumentMetadata
    pages: List[Page]
    # Optional: track provenance of tools
    tools_used: List[str] = Field(default_factory=list)
    version: str = "1.0.0"

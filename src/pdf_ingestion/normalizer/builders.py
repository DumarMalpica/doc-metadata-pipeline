from __future__ import annotations

from typing import Any, Dict

from src.models.super_json_schema import SuperJSON, TextSpan, Table, TableCell


def build_super_json(
    merged_data: Dict[str, Any],
    doc_id: str,
    filename: str,
    source_path: str,
) -> SuperJSON:
    meta = merged_data.get("meta", {})
    num_pages = int(meta.get("num_pages", 0))

    text_span_models = [
        TextSpan(**span_dict) for span_dict in merged_data.get("text_spans", [])
    ]

    table_models = []
    for table_dict in merged_data.get("tables", []):
        cells = [TableCell(**c) for c in table_dict.get("cells", [])]
        table_models.append(
            Table(
                page=table_dict.get("page", 0),
                cells=cells,
                source=table_dict.get("source", "unknown"),
            )
        )

    super_json = SuperJSON(
        doc_id=doc_id,
        filename=filename,
        source_path=source_path,
        num_pages=num_pages,
        metadata=meta,
        text_spans=text_span_models,
        tables=table_models,
    )
    return super_json

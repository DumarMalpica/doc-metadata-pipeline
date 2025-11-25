from __future__ import annotations


CONTRACT_METADATA_PROMPT = """
Act as an expert assistant in contract analysis and corporate metadata normalization.
You have access to a record in BigQuery whose content is a JSON object.

Your task is:

1. Read the provided JSON.
2. Validate its structure.
3. Extract exactly the following fields:

Required fields in the filter_fields section:

- supplier_legal_name
- supplier_names
- sap_contract_number
- scipartner
- effective_date
- agreement_type
- agreement_names
- parent_document
- document_type
- is_evergreen
- expiration_date
- sap_supplier
- url
- file_name
- expiration_email_recipients

Required fields in the file_data section:

- mime_type
- url_source

Output instructions:

Return the information in the following uniform, clean, and validated JSON format, without modifying original values:

{
  "supplier_legal_name": "",
  "supplier_names": "",
  "sap_contract_number": "",
  "scipartner": "",
  "effective_date": "",
  "agreement_type": "",
  "agreement_names": "",
  "parent_document": "",
  "document_type": "",
  "is_evergreen": "",
  "expiration_date": "",
  "sap_supplier": "",
  "document_url": "",
  "file_name": "",
  "expiration_email_recipients": [],
  "mime_type": "",
  "file_source_url": ""
}

Additional rules:

- If a field does not exist in the original JSON, return it as null.
- If it exists but has an empty value, keep it as is.
- Do not invent, do not infer, do not complete information.
- Do not include comments, only the final JSON.
- If the JSON is malformed, specify exactly the error.

You will now receive the JSON to process.
You MUST respond ONLY with the final JSON or an error JSON, nothing else (no explanations).
"""
def build_contract_metadata_prompt(json_payload: str) -> str:
    """
    Combine instructions with the actual JSON payload.
    We wrap the payload in a JSON code block to make parsing easier for the model.
    """
    return f"""{CONTRACT_METADATA_PROMPT}

JSON to analyze:

```json
{json_payload}
```"""

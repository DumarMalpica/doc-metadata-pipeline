from __future__ import annotations

CONTRACT_METADATA_PROMPT = """
### ROLE
Act as a Senior Legal Contract Analyst and Data Quality Engineer.
You will receive a JSON object containing data extracted from a PDF via OCR tools.
This input usually contains a field with the full raw text (e.g., "fullContent", "text", "content") and potentially pre-extracted metadata fields that may be INACCURATE.

### OBJECTIVE
Your goal is to generate a "Golden Record" JSON by validating, correcting, and extracting specific metadata based strictly on the semantic analysis of the document's raw text.

### CRITICAL RULES (Read Carefully)
1. **Source of Truth:** The raw text of the document is the absolute authority. If the input JSON claims the Supplier is "NRG" but the text says "ADP provides services to NRG", you MUST correct the Supplier to "ADP".
2. **Entity Logic:**
   - **Supplier:** The entity selling goods, providing services, or receiving payment (e.g., ADP, Vendor, Consultant).
   - **Client:** The entity buying, paying, or receiving services (e.g., NRG, Buyer, Customer).
   - **SC Partner (Supply Chain Partner):** The specific person signing the document on behalf of the **CLIENT/NRG**. Look for signatures, names, and titles at the end of the document.
3. **Date Logic:**
   - Convert all dates to ISO 8601 format (YYYY-MM-DD).
   - **Expiration Date:** If not explicitly stated as a date, CALCULATE it based on the term duration (e.g., if "Effective Date" is 2019-01-01 and term is "3 years", Expiration is 2022-01-01).
4. **Correction:** Do not simply copy input values. Analyze, Verify, and Correct.
5. **Null Handling:** If a field cannot be found or inferred from the text, return `null`.

### FIELD DEFINITIONS & EXTRACTION LOGIC

- **supplier_legal_name**: Full legal name of the Service Provider (e.g., "ADP, LLC").
- **supplier_names**: Comma-separated list of variations found (e.g., "ADP, ADP Inc, ADP LLC").
- **scipartner**: Name of the individual signing for the CLIENT entity (e.g., "Aimee Spinillo"). NOT the Supplier's signer.
- **effective_date**: The start date of the agreement.
- **expiration_date**: The end date of the agreement.
- **agreement_type**: Classify as "MSA", "Amendment", "SOW", "Order Form", etc.
- **agreement_names**: Title of the document (e.g., "First Amendment to Master Services Agreement").
- **parent_document**: Reference to a previous agreement being modified (e.g., "Master Services Agreement dated Sept 16, 2013").
- **is_evergreen**: Boolean (true/false). True if the contract auto-renews indefinitely or has no end date.

### OUTPUT FORMAT
Return **ONLY** the valid JSON object below. No markdown formatting, no explanations.

{
  "supplier_legal_name": "",
  "supplier_names": "",
  "sap_contract_number": null,
  "scipartner": "",
  "effective_date": "",
  "agreement_type": "",
  "agreement_names": "",
  "parent_document": "",
  "document_type": "",
  "is_evergreen": false,
  "expiration_date": "",
  "sap_supplier": null,
  "document_url": null,
  "file_name": "",
  "expiration_email_recipients": [],
  "mime_type": "application/pdf",
  "file_source_url": null
}
"""

def build_contract_metadata_prompt(json_payload: str) -> str:
    """
    Combines the expert logic instructions with the raw OCR payload.
    """
    return f"""{CONTRACT_METADATA_PROMPT}

### INPUT DATA TO PROCESS
(Analyze the 'fullContent' or text fields within this JSON to populate the output)

```json
{json_payload}
```"""
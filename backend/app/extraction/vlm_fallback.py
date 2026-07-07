from typing import List

# Stub for a Gemini vision-model pass over the resume's rendered pages. Deliberately
# returns fields unresolved (confidence 0) rather than fabricating values, so
# extraction_failed still reflects reality until this is wired up for real.


def extract_with_vlm_mock(pdf_path: str, missing_fields: List[str]) -> dict:
    return {
        field: {"value": None, "confidence": 0.0, "method": "vlm_mock"}
        for field in missing_fields
    }

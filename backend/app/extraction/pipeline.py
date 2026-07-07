from app.extraction.groq_extractor import extract_with_groq
from app.extraction.schemas import ALL_FIELDS, CONFIDENCE_THRESHOLD
from app.extraction.vlm_fallback import extract_with_vlm_mock


def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


def run_extraction_pipeline(resume_text: str, file_ext: str, file_path: str) -> dict:
    result = extract_with_groq(resume_text)

    fields = {field: getattr(result, field).value for field in ALL_FIELDS}
    confidence_scores = {
        field: {"confidence": getattr(result, field).confidence, "method": "groq"}
        for field in ALL_FIELDS
    }

    def needs_fallback(field: str) -> bool:
        return (
            _is_empty(fields[field])
            or confidence_scores[field]["confidence"] < CONFIDENCE_THRESHOLD
        )

    missing_fields = [field for field in ALL_FIELDS if needs_fallback(field)]

    if missing_fields and file_ext == "pdf":
        vlm_results = extract_with_vlm_mock(file_path, missing_fields)
        for field, vlm_field in vlm_results.items():
            if vlm_field["confidence"] > confidence_scores[field]["confidence"]:
                fields[field] = vlm_field["value"]
                confidence_scores[field] = {
                    "confidence": vlm_field["confidence"],
                    "method": vlm_field["method"],
                }

    other_fields = [field for field in ALL_FIELDS if field != "email"]
    still_failed = [field for field in other_fields if needs_fallback(field)]
    status = (
        "extraction_failed"
        if _is_empty(fields["email"]) or len(still_failed) >= 2
        else "extracted"
    )

    return {"fields": fields, "confidence_scores": confidence_scores, "status": status}

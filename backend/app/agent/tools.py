import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from langchain_core.tools import tool

from app.extensions import db
from app.models import Candidate, DocumentRequest
from config import Config


@tool
def get_candidate_profile(candidate_id: str) -> dict:
    """Fetch a candidate's name, email, phone, company, and designation."""
    candidate = db.session.get(Candidate, candidate_id)
    if candidate is None:
        return {"error": "Candidate not found"}

    return {
        "name":        candidate.name,
        "email":       candidate.email,
        "phone":       candidate.phone,
        "company":     candidate.company,
        "designation": candidate.designation,
    }


@tool
def check_existing_requests(candidate_id: str) -> dict:
    """Check whether a non-expired, non-bounced document request already exists for this candidate."""
    existing = (
        DocumentRequest.query.filter(
            DocumentRequest.candidate_id == candidate_id,
            DocumentRequest.token_expiry > datetime.now(timezone.utc),
            DocumentRequest.status.notin_(["expired", "bounced"]),
        )
        .order_by(DocumentRequest.sent_at.desc())
        .first()
    )
    if existing is None:
        return {"exists": False}

    return {
        "exists":       True,
        "message_body": existing.message_body,
        "upload_link":  f"{Config.BASE_URL}/upload/{existing.token}",
        "token_expiry": existing.token_expiry.isoformat(),
    }


@tool
def create_document_request(candidate_id: str, channel: Literal["email", "phone"], message_body: str) -> dict:
    """Log a new personalized document request for the candidate via the given channel."""
    token = secrets.token_urlsafe(32)
    token_expiry = datetime.now(timezone.utc) + timedelta(days=Config.REQUEST_TTL_DAYS)

    db.session.add(DocumentRequest(
        candidate_id=candidate_id,
        channel=channel,
        message_body=message_body,
        token=token,
        token_expiry=token_expiry,
        status="pending",
    ))

    candidate = db.session.get(Candidate, candidate_id)
    candidate.status = "docs_requested"

    db.session.commit()

    return {
        "message_body": message_body,
        "upload_link":  f"{Config.BASE_URL}/upload/{token}",
        "token_expiry": token_expiry.isoformat(),
    }

import uuid
from datetime import datetime, timezone

from app.extensions import db
from config import Config


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    email = db.Column(db.String(255), nullable=True, index=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(32))
    company = db.Column(db.String(255))
    designation = db.Column(db.String(255))
    skills = db.Column(db.JSON)
    resume_path = db.Column(db.String(512), nullable=False)
    resume_raw_text = db.Column(db.Text)
    confidence_scores = db.Column(db.JSON)
    status = db.Column(
        db.Enum(
            "uploaded",
            "extraction_failed",
            "extracted",
            "docs_requested",
            "docs_submitted",
            "verified",
            name="candidate_status",
        ),
        nullable=False,
        default="uploaded",
    )
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )

    document_requests = db.relationship(
        "DocumentRequest", backref="candidate", cascade="all, delete-orphan"
    )
    documents = db.relationship(
        "Document", backref="candidate", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "company": self.company,
            "designation": self.designation,
            "skills": self.skills,
            "confidence_scores": self.confidence_scores,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "documents": [d.to_dict() for d in self.documents],
        }


class DocumentRequest(db.Model):
    __tablename__ = "document_requests"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    candidate_id = db.Column(
        db.String(36), db.ForeignKey("candidates.id"), nullable=False, index=True
    )
    channel = db.Column(db.Enum("email", "phone", name="request_channel"), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    token_expiry = db.Column(db.DateTime(timezone=True), nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    status = db.Column(
        db.Enum("pending", "delivered", "bounced", "expired", name="request_status"),
        nullable=False,
        default="pending",
    )

    documents = db.relationship("Document", backref="request")


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    candidate_id = db.Column(
        db.String(36), db.ForeignKey("candidates.id"), nullable=False, index=True
    )
    request_id = db.Column(
        db.String(36), db.ForeignKey("document_requests.id"), nullable=True
    )
    doc_type = db.Column(db.Enum("PAN", "Aadhaar", name="doc_type"), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    is_latest = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "doc_type": self.doc_type,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "is_latest": self.is_latest,
            "file_url": f"{Config.BASE_URL}/documents/{self.id}/file",
        }

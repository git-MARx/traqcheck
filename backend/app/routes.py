import os
import traceback
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, render_template, request, send_file
from markitdown import MarkItDown

from app.agent.executor import run_document_request_agent
from app.documents import save_candidate_document
from app.extensions import db
from app.extraction.pipeline import run_extraction_pipeline
from app.models import Candidate, Document, DocumentRequest
from app.storage import UnsupportedFileType, save_upload_file

candidates_bp = Blueprint("candidates", __name__, url_prefix="/candidates")
documents_bp  = Blueprint("documents", __name__, url_prefix="/documents")
public_bp     = Blueprint("public", __name__)


@candidates_bp.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No 'resume' file in request"}), 400

    file_storage = request.files["resume"]
    if not file_storage.filename:
        return jsonify({"error": "No file selected"}), 400

    try:
        file_path, ext = save_upload_file(
            file_storage,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["ALLOWED_RESUME_EXTENSIONS"],
        )
    except UnsupportedFileType as e:
        return jsonify({"error": str(e)}), 400

    md_text = MarkItDown().convert(file_path).text_content

    md_path = os.path.splitext(file_path)[0] + ".md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    try:
        extraction = run_extraction_pipeline(resume_text=md_text, file_ext=ext, file_path=file_path)
    except Exception:
        traceback.print_exc()
        extraction = {"fields": {}, "confidence_scores": {}, "status": "extraction_failed"}

    fields = extraction["fields"]
    email = fields.get("email")

    candidate = Candidate.query.filter_by(email=email).first() if email else None
    if candidate is None:
        candidate = Candidate(email=email)
        db.session.add(candidate)

    candidate.name = fields.get("name")
    candidate.phone = fields.get("phone")
    candidate.company = fields.get("company")
    candidate.designation = fields.get("designation")
    candidate.skills = fields.get("skills") or []
    candidate.resume_path = file_path
    candidate.resume_raw_text = md_text
    candidate.confidence_scores = extraction["confidence_scores"]
    candidate.status = extraction["status"]

    db.session.commit()

    return jsonify(candidate.to_dict()), 201


@candidates_bp.route("", methods=["GET"])
def list_candidates():
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return jsonify([c.to_dict() for c in candidates]), 200


@candidates_bp.route("/<candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    candidate = db.session.get(Candidate, candidate_id)
    if candidate is None:
        return jsonify({"error": "Candidate not found"}), 404

    return jsonify(candidate.to_dict()), 200


@candidates_bp.route("/<candidate_id>/request-documents", methods=["POST"])
def request_documents(candidate_id):
    candidate = db.session.get(Candidate, candidate_id)
    if candidate is None:
        return jsonify({"error": "Candidate not found"}), 404

    result = run_document_request_agent(candidate_id)
    return jsonify(result), 200


@candidates_bp.route("/<candidate_id>/submit-documents", methods=["POST"])
def submit_documents(candidate_id):
    candidate = db.session.get(Candidate, candidate_id)
    if candidate is None:
        return jsonify({"error": "Candidate not found"}), 404

    doc_type = request.form.get("doc_type")
    if doc_type not in ("PAN", "Aadhaar"):
        return jsonify({"error": "doc_type must be 'PAN' or 'Aadhaar'"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No 'file' in request"}), 400

    file_storage = request.files["file"]
    if not file_storage.filename:
        return jsonify({"error": "No file selected"}), 400

    active_request = (
        DocumentRequest.query.filter(
            DocumentRequest.candidate_id == candidate_id,
            DocumentRequest.token_expiry > datetime.now(timezone.utc),
        )
        .order_by(DocumentRequest.sent_at.desc())
        .first()
    )

    try:
        save_candidate_document(
            candidate_id,
            doc_type,
            file_storage,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"],
            request_id=active_request.id if active_request else None,
        )
    except UnsupportedFileType as e:
        return jsonify({"error": str(e)}), 400

    candidate.status = "docs_submitted"

    db.session.commit()

    return jsonify(candidate.to_dict()), 201


@documents_bp.route("/<document_id>/file", methods=["GET"])
def get_document_file(document_id):
    document = db.session.get(Document, document_id)
    if document is None:
        return jsonify({"error": "Document not found"}), 404

    return send_file(document.file_path)


def _valid_request_for_token(token):
    doc_request = DocumentRequest.query.filter_by(token=token).first()
    if doc_request is None or doc_request.token_expiry <= datetime.now(timezone.utc):
        return None
    return doc_request


@public_bp.route("/upload/<token>", methods=["GET"])
def upload_form(token):
    doc_request = _valid_request_for_token(token)
    if doc_request is None:
        return render_template("upload_invalid.html"), 400

    candidate = db.session.get(Candidate, doc_request.candidate_id)
    return render_template("upload_form.html", candidate=candidate)


@public_bp.route("/upload/<token>", methods=["POST"])
def upload_submit(token):
    doc_request = _valid_request_for_token(token)
    if doc_request is None:
        return jsonify({"error": "Invalid or expired link"}), 400

    candidate = db.session.get(Candidate, doc_request.candidate_id)
    pan_file = request.files.get("pan")
    aadhaar_file = request.files.get("aadhaar")

    if not (pan_file and pan_file.filename) and not (aadhaar_file and aadhaar_file.filename):
        return jsonify({"error": "No files provided"}), 400

    try:
        if pan_file and pan_file.filename:
            save_candidate_document(
                candidate.id, "PAN", pan_file,
                current_app.config["UPLOAD_FOLDER"],
                current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"],
                request_id=doc_request.id,
            )
        if aadhaar_file and aadhaar_file.filename:
            save_candidate_document(
                candidate.id, "Aadhaar", aadhaar_file,
                current_app.config["UPLOAD_FOLDER"],
                current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"],
                request_id=doc_request.id,
            )
    except UnsupportedFileType as e:
        return jsonify({"error": str(e)}), 400

    doc_request.status = "delivered"
    candidate.status = "docs_submitted"

    db.session.commit()

    return render_template("upload_success.html", candidate=candidate)

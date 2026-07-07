from app.extensions import db
from app.models import Document
from app.storage import save_upload_file


def save_candidate_document(candidate_id, doc_type, file_storage, upload_folder, allowed_extensions, request_id=None):
    file_path, _ext = save_upload_file(file_storage, upload_folder, allowed_extensions)

    Document.query.filter_by(
        candidate_id=candidate_id, doc_type=doc_type, is_latest=True
    ).update({"is_latest": False})

    document = Document(
        candidate_id=candidate_id,
        request_id=request_id,
        doc_type=doc_type,
        file_path=file_path,
    )
    db.session.add(document)
    return document

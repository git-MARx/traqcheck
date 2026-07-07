import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://traqcheck:traqcheck@localhost:5433/traqcheck"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "docx"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}

    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5001")
    REQUEST_TTL_DAYS = 3

    # comma-separated list of origins allowed to call this API cross-origin
    FRONTEND_ORIGINS = os.environ.get("FRONTEND_ORIGINS", "http://localhost:5173").split(",")

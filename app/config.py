import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_database_url():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Default to SQLite only when not running on Vercel (writable filesystem)
        return f"sqlite:///{BASE_DIR / 'app.db'}"
    # Rewrite postgres:// → postgresql:// (Supabase / Heroku use old scheme)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url


def _get_upload_folder():
    configured = os.getenv("UPLOAD_FOLDER")
    if configured:
        return configured
    # On Vercel the filesystem is read-only except /tmp
    if os.environ.get("VERCEL"):
        return "/tmp/uploads"
    return str(BASE_DIR / "app" / "static" / "uploads")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = _get_upload_folder()
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "webm"}
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

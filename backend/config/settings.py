"""
settings.py — Application configuration loaded from environment variables.

Usage:
    from config.settings import settings
    print(settings.GROQ_API_KEY)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory (one level up from backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Central configuration loaded from environment variables with sensible defaults."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'docxpert.db'}")
    DATABASE_PATH: Path = BASE_DIR / "database" / "docxpert.db"

    # File uploads
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    TEMP_DIR: Path = BASE_DIR / "temp"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {"doc", "docx", "pdf"}

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:5000,http://localhost:3000,http://127.0.0.1:5000"
    ).split(",")

    # Secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")

    # Groq AI
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    # LanguageTool
    LANGUAGETOOL_URL: str = os.getenv("LANGUAGETOOL_URL", "https://api.languagetool.org/v2/check")
    LANGUAGETOOL_LANGUAGE: str = os.getenv("LANGUAGETOOL_LANGUAGE", "en-US")

    # LibreOffice — auto-detect on macOS
    LIBREOFFICE_PATH: str = os.getenv("LIBREOFFICE_PATH", "")

    def get_libreoffice_path(self) -> str:
        """Return the path to the LibreOffice binary, auto-detecting if not set."""
        if self.LIBREOFFICE_PATH:
            return self.LIBREOFFICE_PATH

        # macOS default
        mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        if Path(mac_path).exists():
            return mac_path

        # Linux / generic
        for name in ("soffice", "libreoffice"):
            import shutil
            path = shutil.which(name)
            if path:
                return path

        return ""

    def ensure_dirs(self) -> None:
        """Create required directories if they don't exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()

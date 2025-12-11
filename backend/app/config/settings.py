import os
import sys
from dotenv import load_dotenv

load_dotenv()

# =============================================================
# 1. Tentukan BASE_DIR dengan cara yang paling stabil
# =============================================================
# Lokasi file ini: project_root/backend/app/config/settings.py
CURRENT_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE))  # backend/app/config → backend/app
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)                   # backend → project_root

BASE_DIR = PROJECT_ROOT

# =============================================================
# 2. Settings Class
# =============================================================
class Settings:
    BASE_DIR = BASE_DIR

    DB_PATH = os.path.join(BASE_DIR, os.getenv("DB_PATH", "data/data.db"))

    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

    UPLOAD_DIR = os.path.join(BASE_DIR, os.getenv("UPLOAD_DIR", "uploads"))
    BACKUP_DIR = os.path.join(BASE_DIR, os.getenv("BACKUP_DIR", "backup"))
    LOG_DIR = os.path.join(BASE_DIR, os.getenv("LOG_DIR", "logs"))
    EXPORT_DIR = os.path.join(BASE_DIR, os.getenv("EXPORT_DIR", "exports"))

    APP_NAME = os.getenv("APP_NAME", "Sistem Repository dan Monitoring Tindak Lanjut Hukdis")
    APP_ENV = os.getenv("APP_ENV", "development")

settings = Settings()

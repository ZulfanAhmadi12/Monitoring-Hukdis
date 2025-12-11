# frontend/services/restore_service.py
from services.api_client import api_get_raw, api_post

API_PREFIX = "/hukdis"


# -----------------------------
# 🔍 1. LAST BACKUP TIME
# GET /hukdis/last_backup_time/{table_name}
# -----------------------------
def get_last_backup_time(table_name="current_data"):
    return api_get_raw(f"{API_PREFIX}/last_backup_time/{table_name}")


# -----------------------------
# ♻️ 2. RESTORE CURRENT DATA
# POST /hukdis/restore
# -----------------------------
def restore_current_data():
    return api_post(f"{API_PREFIX}/restore")


# -----------------------------
# 💾 3. BACKUP INTERNAL (backup_table)
# POST /hukdis/backup?table_name=current_data
# -----------------------------
def backup_internal():
    return api_post(f"{API_PREFIX}/backup?table_name=current_data")


# -----------------------------
# 📦 4. BACKUP SNAPSHOT (.db)
# POST /hukdis/backup/snapshot
# -----------------------------
def backup_snapshot():
    return api_post(f"{API_PREFIX}/backup/snapshot")



try:
    from backend.app.config.database import (
        engine,
        backup_table,
        restore_table,
        get_last_backup_time,
        log_event
    )
except ModuleNotFoundError:
    from app.config.database import (
        engine,
        backup_table,
        restore_table,
        get_last_backup_time,
        log_event
    )
try:
    from backend.app.config.settings import settings
except ModuleNotFoundError:
    from app.config.settings import settings
import os
import sqlite3
from datetime import datetime

class RestoreRepository:

    @staticmethod
    def backup(table_name: str):
        result = backup_table(engine, table_name)
        return result
    
    @staticmethod
    def backup_snapshot():
        """Physical SQLite snapshot stored in /backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = settings.BACKUP_DIR
        os.makedirs(backup_dir, exist_ok=True)

        src = settings.DB_PATH
        dst = os.path.join(backup_dir, f"current_data_{timestamp}.db")

        # sqlite backup API (atomic + safe)
        src_conn = sqlite3.connect(src)
        dst_conn = sqlite3.connect(dst)
        src_conn.backup(dst_conn)

        src_conn.close()
        dst_conn.close()

        return {
            "status": "success",
            "message": f"Snapshot saved to {dst}",
            "path": dst
        }

    @staticmethod
    def restore_current_data():
        result = restore_table(engine, "current_data")
        if result.get("status") == "success":
            log_event("Restore", "Restored current_data from backup")
        return result

    @staticmethod
    def last_backup_time(table_name: str):
        return get_last_backup_time(engine, table_name)

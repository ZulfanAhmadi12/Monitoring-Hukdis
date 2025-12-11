# database.py
import os
import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
try:
    from backend.app.config.settings import settings
except ModuleNotFoundError:
    from app.config.settings import settings

Base = declarative_base()

DB_PATH = settings.DB_PATH

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False}
)

print(f"Using SQLite DB at: {DB_PATH}")   # <— tampil di terminal uvicorn

def save_to_db(df, table_name: str, mode: str = "append"):
    """Save DataFrame to database."""
    try:
        df.to_sql(table_name, con=engine, if_exists=mode, index=False)
        return {"status": "success", "table": table_name, "rows": len(df)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def backup_table(engine, table_name: str):
    with engine.begin() as conn:
        backup_name = f"{table_name}_backup"
        conn.execute(text(f"DROP TABLE IF EXISTS {backup_name}"))
        conn.execute(text(f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS backup_log (
                table_name TEXT,
                backup_time TEXT
            )
        """))
        conn.execute(text("DELETE FROM backup_log WHERE table_name = :table"), {"table": table_name})
        conn.execute(text("""
            INSERT INTO backup_log (table_name, backup_time)
            VALUES (:table, datetime('now', 'localtime'))
        """), {"table": table_name})
    return {"status": "success", "message": f"Backup created: {backup_name}"}

def restore_table(engine, table_name: str):
    with engine.begin() as conn:
        backup_name = f"{table_name}_backup"
        exists = conn.execute(
            text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{backup_name}'")
        ).fetchone()
        if not exists:
            return {"status": "error", "message": f"No backup found for {table_name}"}

        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        conn.execute(text(f"CREATE TABLE {table_name} AS SELECT * FROM {backup_name}"))
    return {"status": "success", "message": f"Table '{table_name}' restored from backup"}

def get_last_backup_time(engine, table_name: str):
    with engine.begin() as conn:

        # 🔥 always ensure backup_log exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS backup_log (
                table_name TEXT,
                backup_time TEXT
            )
        """))

        result = conn.execute(
            text("""
                SELECT backup_time 
                FROM backup_log 
                WHERE table_name = :table
                ORDER BY backup_time DESC 
                LIMIT 1
            """),
            {"table": table_name}
        ).fetchone()

        return result[0] if result else None


def log_event(action, details=None):
    """Record timestamped events like Upload or Restore."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                details TEXT,
                timestamp DATETIME
            )
        """))
        conn.execute(
            text("INSERT INTO event_logs (action, details, timestamp) VALUES (:a, :d, :t)"),
            {
                "a": action,
                "d": details or "",
                "t": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )


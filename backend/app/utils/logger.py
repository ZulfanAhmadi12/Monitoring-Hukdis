import datetime
from sqlalchemy import text
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine

def log_event(action, details=None):
    """Record timestamped events like Upload, Restore, etc."""
    with engine.begin() as conn:
        # Ensure table exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                details TEXT,
                timestamp TEXT
            )
        """))

        # Insert log entry
        conn.execute(
            text("""
                INSERT INTO event_logs (action, details, timestamp)
                VALUES (:action, :details, :timestamp)
            """),
            {
                "action": action,
                "details": details or "",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )


def get_latest_event(action: str):
    """Fetch the latest timestamp for a specific action."""
    with engine.begin() as conn:
        # Ensure table exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                details TEXT,
                timestamp TEXT
            )
        """))

        # Fetch most recent entry
        result = conn.execute(
            text("""
                SELECT timestamp
                FROM event_logs
                WHERE action = :action
                ORDER BY timestamp DESC
                LIMIT 1
            """),
            {"action": action}
        ).fetchone()

        return result[0] if result else None

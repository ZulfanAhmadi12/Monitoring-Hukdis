import pandas as pd
from sqlalchemy import text
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine

class SQLService:

    @staticmethod
    def run_query(query: str) -> pd.DataFrame:
        # Safety: prevent DROP/DELETE/UPDATE/INSERT
        forbidden = ["drop", "delete", "update", "insert", "alter"]
        q_low = query.lower()

        if any(cmd in q_low for cmd in forbidden):
            raise Exception("Query not allowed for safety. Only SELECT queries permitted.")

        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn)

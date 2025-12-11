# backend/app/repository/hukdis_repository.py
from sqlalchemy import text, inspect
from datetime import datetime
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine


class HukdisRepository:

    @staticmethod
    def ensure_upload_tables():
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS upload_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    table_name TEXT,
                    upload_time TEXT,
                    total_rows INTEGER,
                    inserted_rows INTEGER,
                    updated_rows INTEGER
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    upload_id INTEGER,
                    row_id INTEGER,
                    column_name TEXT,
                    before_value TEXT,
                    after_value TEXT,
                    change_time TEXT,
                    FOREIGN KEY(upload_id) REFERENCES upload_history(id)
                );
            """))

            # ensure event_logs exists (used to store errors / events)
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS event_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    details TEXT,
                    timestamp TEXT
                );
            """))

    @staticmethod
    def log_upload_start(filename, upload_ts):
        with engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO upload_history (filename, upload_time, total_rows, inserted_rows, updated_rows)
                VALUES (:filename, :upload_time, 0, 0, 0)
            """), {
                "filename": filename,
                "upload_time": upload_ts
            })
            # SQLAlchemy DB-API result usually supports lastrowid for SQLite
            return result.lastrowid

    @staticmethod
    def update_upload_summary(upload_id, total, inserted, updated, table_name ,conn=None):
        # allow caller provide conn to remain in same transaction
        if conn is None:
            with engine.begin() as c:
                c.execute(text("""
                    UPDATE upload_history
                    SET total_rows = :total_rows,
                        inserted_rows = :inserted_rows,
                        updated_rows = :updated_rows,
                        table_name = :table_name
                    WHERE id = :id
                """), {
                    "total_rows": total,
                    "inserted_rows": inserted,
                    "updated_rows": updated,
                    "table_name": table_name,
                    "id": upload_id
                })
        else:
            conn.execute(text("""
                UPDATE upload_history
                SET total_rows = :total_rows,
                    inserted_rows = :inserted_rows,
                    updated_rows = :updated_rows
                WHERE id = :id
            """), {
                "total_rows": total,
                "inserted_rows": inserted,
                "updated_rows": updated,
                "id": upload_id
            })

    @staticmethod
    def ensure_main_table(table_name, df):
        inspector = inspect(engine)

        # ---------------------------
        # CASE 1 — Table doesn't exist -> CREATE new table
        # ---------------------------
        if table_name not in inspector.get_table_names():

            col_defs = ", ".join([f'"{c}" TEXT' for c in df.columns])

            create_sql = f"""
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {col_defs},

                    -- Metadata
                    updated_at TEXT,

                    -- Soft delete
                    is_deleted INTEGER DEFAULT 0,
                    deleted_at TEXT
                );
            """

            with engine.begin() as conn:
                conn.execute(text(create_sql))
            return

        # ---------------------------
        # CASE 2 — Table exists -> ADD missing columns
        # ---------------------------
        existing_cols = [col["name"] for col in inspector.get_columns(table_name)]

        alter_statements = []

        if "updated_at" not in existing_cols:
            alter_statements.append("ALTER TABLE {table} ADD COLUMN updated_at TEXT")

        if "is_deleted" not in existing_cols:
            alter_statements.append("ALTER TABLE {table} ADD COLUMN is_deleted INTEGER DEFAULT 0")

        if "deleted_at" not in existing_cols:
            alter_statements.append("ALTER TABLE {table} ADD COLUMN deleted_at TEXT")

        # Apply one by one because SQLite doesn't support multi-column ALTER
        if alter_statements:
            with engine.begin() as conn:
                for stmt in alter_statements:
                    sql = stmt.format(table=table_name)
                    conn.execute(text(sql))

    @staticmethod
    def find_existing(conn, table_name, nomor_lha, pn):
        find_sql = text(f"""
            SELECT * FROM {table_name}
            WHERE nomor_lha = :nomor_lha AND pn = :pn AND is_deleted = 0
        """)
        return conn.execute(find_sql, {"nomor_lha": nomor_lha, "pn": pn}).mappings().fetchone()

    @staticmethod
    def update_row(conn, table_name, row, row_id):
        # 1. Convert row into dict
        params = row.to_dict()

        # 2. Add 'tanggal_upload' override (format dd/mm/YYYY)
        today = datetime.now().strftime("%d/%m/%Y")
        params["tanggal_upload"] = today

        # 3. Build SET clause (including tanggal_upload)
        set_clause = ", ".join([f"{col} = :{col}" for col in params.keys()])

        update_sql = text(f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE id = :id
        """)

        # 4. Add ID
        params["id"] = row_id

        # 5. Execute update
        conn.execute(update_sql, params)

    @staticmethod
    def insert_row(conn, table_name, row):
        cols = ", ".join(row.index)
        vals = ", ".join([f":{c}" for c in row.index])
        insert_sql = text(f"""
            INSERT INTO {table_name} ({cols})
            VALUES ({vals})
        """)
        conn.execute(insert_sql, row.to_dict())

    @staticmethod
    def log_changes(conn, upload_id, row_id, changes, upload_ts):
        for col, diff in changes.items():
            conn.execute(text("""
                INSERT INTO change_log (upload_id, row_id, column_name, before_value, after_value, change_time)
                VALUES (:upload_id, :row_id, :column_name, :before_value, :after_value, :change_time)
            """), {
                "upload_id": upload_id,
                "row_id": row_id,
                "column_name": col,
                "before_value": diff["before"],
                "after_value": diff["after"],
                "change_time": upload_ts
            })

    # ----------------------------
    # Event log utilities (use caller conn to avoid locking)
    # ----------------------------
    @staticmethod
    def insert_event(conn, action, details=None):
        conn.execute(text("""
            INSERT INTO event_logs (action, details, timestamp)
            VALUES (:action, :details, :timestamp)
        """), {"action": action, 
               "details": details or "", 
               "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

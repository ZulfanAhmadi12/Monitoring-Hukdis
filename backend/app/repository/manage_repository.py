from sqlalchemy import text
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine
from datetime import datetime

class ManageRepository:

    @staticmethod
    def filter_data(
        keyword, pn, nomor_lha, nama_unit_kerja, status_tindak_lanjut,
        tanggal_exit_start, tanggal_exit_end,
        limit, offset
    ):

        filters = ["is_deleted = 0"]  # always hide soft-deleted rows
        params = {}

        # -------- FULL TEXT SEARCH (LIKE across columns) --------
        if keyword:
            filters.append("""
                (
                    pn LIKE :kw OR
                    nomor_lha LIKE :kw OR
                    nama_unit_kerja LIKE :kw OR
                    status_tindak_lanjut LIKE :kw OR
                    nama_pelaku LIKE :kw
                )
            """)
            params["kw"] = f"%{keyword}%"

        # -------- COLUMN FILTERS --------
        if pn:
            filters.append("pn LIKE :pn")
            params["pn"] = f"%{pn}%"

        if nomor_lha:
            filters.append("nomor_lha LIKE :lha")
            params["lha"] = f"%{nomor_lha}%"

        if nama_unit_kerja:
            filters.append("nama_unit_kerja LIKE :uk")
            params["uk"] = f"%{nama_unit_kerja}%"

        if status_tindak_lanjut:
            filters.append("status_tindak_lanjut LIKE :status")
            params["status"] = f"%{status_tindak_lanjut}%"

        # -------- DATE RANGE FILTER --------
        if tanggal_exit_start:
            filters.append("tanggal_exit >= :tstart")
            params["tstart"] = tanggal_exit_start

        if tanggal_exit_end:
            filters.append("tanggal_exit <= :tend")
            params["tend"] = tanggal_exit_end

        # Merge WHERE clause
        where_clause = " AND ".join(filters)

        sql = text(f"""
            SELECT *
            FROM current_data
            WHERE {where_clause}
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """)

        params["limit"] = limit
        params["offset"] = offset

        with engine.connect() as conn:
            rows = conn.execute(sql, params).mappings().fetchall()
            return [dict(r) for r in rows]



    @staticmethod
    def update_row_with_timestamp(conn, table_name: str, row_id: int, changes: dict):
        set_clause = ", ".join([f"{col} = :{col}" for col in changes.keys()])
        params = changes.copy()

        # add updated_at
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        set_clause += ", updated_at = :updated_at"
        params["updated_at"] = now_str

        params["id"] = row_id

        sql = text(f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE id = :id
        """)

        conn.execute(sql, params)

    @staticmethod
    def edit_row_with_timestamp(row_id: int, payload: dict, table_name):
        with engine.begin() as conn:

            # validate
            exists = conn.execute(
                text(f"SELECT id FROM {table_name} WHERE id = :id AND is_deleted = 0"),
                {"id": row_id}
            ).fetchone()

            if not exists:
                return {"status": "error", "message": "Row not found or deleted"}

            ManageRepository.update_row_with_timestamp(conn, table_name, row_id, payload)

        return {
            "status": "success",
            "updated_fields": list(payload.keys()),
            "row_id": row_id
        }

    @staticmethod
    def soft_delete(conn, table, row_id):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            text(f"""
                UPDATE {table}
                SET is_deleted = 1, deleted_at = :deleted_at
                WHERE id = :id
            """),
            {"deleted_at": now, "id": row_id}
        )

    @staticmethod
    def soft_delete_bulk(conn, table, ids):
        if not ids:
            return

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # dynamic placeholders: ?, ?, ?, ...
        placeholders = ",".join([f":id{i}" for i in range(len(ids))])

        params = {f"id{i}": ids[i] for i in range(len(ids))}
        params["deleted_at"] = now

        conn.execute(
            text(f"""
                UPDATE {table}
                SET is_deleted = 1,
                    deleted_at = :deleted_at
                WHERE id IN ({placeholders})
            """),
            params
        )


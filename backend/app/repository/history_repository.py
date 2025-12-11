from sqlalchemy import text
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine

class HistoryRepository:

    @staticmethod
    def list_upload_history(limit: int = 200, offset: int = 0, filename: str = None,
                            date_start: str = None, date_end: str = None):
        """
        date_start / date_end expected format: 'YYYY-MM-DD' OR 'dd/mm/YYYY' (we accept YYYY-MM-DD preferred).
        We convert to comparable YYYYMMDD string for upload_time stored as 'dd/mm/YYYY HH:MM:SS'.
        """
        filters = []
        params = {"limit": limit, "offset": offset}

        if filename:
            filters.append("filename LIKE :filename")
            params["filename"] = f"%{filename}%"

        # If date filters present, convert to YYYYMMDD for comparison
        if date_start:
            # accept YYYY-MM-DD or dd/mm/YYYY. Normalize to YYYYMMDD string:
            ds = HistoryRepository._normalize_date_to_yyyymmdd(date_start)
            filters.append("(substr(upload_time,7,4) || substr(upload_time,4,2) || substr(upload_time,1,2)) >= :ds")
            params["ds"] = ds

        if date_end:
            de = HistoryRepository._normalize_date_to_yyyymmdd(date_end)
            filters.append("(substr(upload_time,7,4) || substr(upload_time,4,2) || substr(upload_time,1,2)) <= :de")
            params["de"] = de

        where = " AND ".join(filters) if filters else "1=1"

        sql = text(f"""
            SELECT *
            FROM upload_history
            WHERE {where}
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """)
        with engine.connect() as conn:
            rows = conn.execute(sql, params).mappings().fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_upload_detail(upload_id: int, include_changes: bool = False, change_limit: int = 1000, change_offset: int = 0):
        with engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM upload_history WHERE id = :id"), {"id": upload_id}).mappings().fetchone()
            if not row:
                return None

            result = {"upload": dict(row)}

            if include_changes:
                changes = conn.execute(
                    text("""
                        SELECT * FROM change_log
                        WHERE upload_id = :u
                        ORDER BY id ASC
                        LIMIT :limit OFFSET :offset
                    """),
                    {"u": upload_id, "limit": change_limit, "offset": change_offset}
                ).mappings().fetchall()
                result["changes"] = [dict(r) for r in changes]

            return result

    @staticmethod
    def list_change_log(upload_id: int, column_name: str = None, group_by_row: bool = False,
                        limit: int = 1000, offset: int = 0):
        # base filter
        params = {"u": upload_id, "limit": limit, "offset": offset}
        if group_by_row:
            # return grouped summary per row_id with list of changes aggregated as JSON-like string
            # SQLite doesn't have built-in JSON aggregation in older versions, so we return rows grouped
            sql = text("""
                SELECT row_id, nomor_lha, pn,
                       GROUP_CONCAT(column_name || '||' || COALESCE(before_value,'') || '||' || COALESCE(after_value,''), ';;') AS changes_concat
                FROM change_log
                WHERE upload_id = :u
                GROUP BY row_id, nomor_lha, pn
                ORDER BY row_id
                LIMIT :limit OFFSET :offset
            """)
            with engine.connect() as conn:
                rows = conn.execute(sql, params).mappings().fetchall()
                # parse changes_concat into list of dicts
                out = []
                for r in rows:
                    changes = []
                    raw = r["changes_concat"] or ""
                    for item in raw.split(";;"):
                        if not item:
                            continue
                        parts = item.split("||")
                        col = parts[0] if len(parts) > 0 else ""
                        before = parts[1] if len(parts) > 1 else ""
                        after = parts[2] if len(parts) > 2 else ""
                        changes.append({"column": col, "before": before, "after": after})
                    out.append({
                        "row_id": r["row_id"],
                        "nomor_lha": r.get("nomor_lha"),
                        "pn": r.get("pn"),
                        "changes": changes
                    })
                return out
        else:
            q = "SELECT * FROM change_log WHERE upload_id = :u"
            if column_name:
                q += " AND column_name = :col"
                params["col"] = column_name
            q += " ORDER BY id ASC LIMIT :limit OFFSET :offset"
            with engine.connect() as conn:
                rows = conn.execute(text(q), params).mappings().fetchall()
                return [dict(r) for r in rows]

    @staticmethod
    def _normalize_date_to_yyyymmdd(dstr: str) -> str:
        """
        Accept 'YYYY-MM-DD' or 'dd/mm/YYYY' or 'dd-mm-YYYY'.
        Return 'YYYYMMDD' string for comparisons.
        """
        d = dstr.strip()
        if "-" in d and len(d.split("-")[0]) == 4:
            # assume YYYY-MM-DD
            return d.replace("-", "")
        if "/" in d and len(d.split("/")[2]) == 4:
            # dd/mm/YYYY -> YYYYMMDD
            parts = d.split("/")
            return f"{parts[2]}{parts[1].zfill(2)}{parts[0].zfill(2)}"
        if "-" in d and len(d.split("-")[2]) == 4:
            parts = d.split("-")
            return f"{parts[2]}{parts[1].zfill(2)}{parts[0].zfill(2)}"
        # fallback: try remove non-digit
        digits = "".join(ch for ch in d if ch.isdigit())
        return digits

    @staticmethod
    def fetch_logs(start_dt, end_dt):
        with engine.begin() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, action, details, timestamp
                    FROM event_logs
                    WHERE timestamp BETWEEN :s AND :e
                    ORDER BY timestamp DESC
                """),
                {
                    "s": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "e": end_dt.strftime("%Y-%m-%d %H:%M:%S")
                }
            ).mappings().all()

            return list(rows)
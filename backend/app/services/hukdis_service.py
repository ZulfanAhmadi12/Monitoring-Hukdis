# backend/app/services/hukdis_service.py
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import text
from fastapi import UploadFile

# imports tolerant for dev vs exe package paths
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine

try:
    from backend.app.repository.hukdis_repository import HukdisRepository
except ModuleNotFoundError:
    from app.repository.hukdis_repository import HukdisRepository

try:
    from backend.app.utils.data_cleaning import parse_excel_date, detect_changes, tentukan_sla
except ModuleNotFoundError:
    from app.utils.data_cleaning import parse_excel_date, detect_changes, tentukan_sla

try:
    from backend.app.utils.kategori_utils import penentuan_kategori_pelanggaran
except ModuleNotFoundError:
    from app.utils.kategori_utils import penentuan_kategori_pelanggaran


class HukdisService:

    @staticmethod
    async def upload_excel(file: UploadFile, format_type: str):
        """
        Refactored upload:
         - sanitize/normalize columns
         - ensure tables
         - create upload_history entry
         - process rows one-by-one inside one connection using SAVEPOINT (begin_nested)
         - collect per-row errors (and write to event_logs using same conn)
         - update upload summary and write a summary event
        Returns dict with status, inserted, updated, errors (list)
        """

        try:
            # --- 1. Load Excel ---
            df = pd.read_excel(file.file, dtype=str)

            # normalize column names (sudah ada)
            df.columns = (
                df.columns.str.strip()
                          .str.replace(" ", "_")
                          .str.replace("-", "_")
                          .str.replace(".", "_")
                          .str.lower()
            )

            # ensure key columns exist
            df["nomor_lha"] = df.get("nomor_lha", "").astype(str).fillna("").replace("nan", "").str.strip()
            df["pn"] = df.get("pn", "").astype(str).fillna("").replace("nan", "").str.strip()

            # Normalize entire DF: convert literal 'nan' and empty strings to None for reliable checks
            # (helps because dtype=str turns NaN into 'nan' string in some environments)
            df = df.replace({np.nan: None})
            # also treat bare "nan", "none", "" as None
            def _normalize_cell(v):
                if v is None:
                    return None
                s = str(v).strip()
                if s.lower() in ("", "nan", "none"):
                    return None
                return v
            
            for col in df.columns:
                df[col] = df[col].map(_normalize_cell)

            # Upload timestamps
            today = datetime.now()
            today_str = today.strftime("%d/%m/%Y")
            upload_ts = today.strftime("%d/%m/%Y %H:%M:%S")
            df["tanggal_upload"] = today_str

            # normalize date columns (existing code remains)
            if format_type == "new":
                DATE_COLUMNS = [
                    # "tanggal_exit",
                    "tanggal_lha",
                    "tanggal_surat_nota_rekomendasi",
                    "tanggal_lembar_putusan_pejabat_pemutus",
                    "tanggal_sk_putusan"
                ]
                for col in DATE_COLUMNS:
                    if col in df.columns:
                        df[col] = df[col].apply(parse_excel_date)

                df = tentukan_sla(df)

            table_name = "current_data" if format_type == "new" else "old_data"

            # --- 2. Ensure Logging Tables Exist ---
            HukdisRepository.ensure_upload_tables()

            # --- 3. Create upload log entry ---
            upload_id = HukdisRepository.log_upload_start(
                filename=file.filename,
                upload_ts=upload_ts
            )
            # --- 4. Ensure destination table exists ---
            HukdisRepository.ensure_main_table(table_name, df)

            inserted = 0
            updated = 0
            errors = []

            # helper: detect "empty" values robustly
            def is_missing(val):
                if val is None:
                    return True
                if isinstance(val, float) and pd.isna(val):
                    return True
                s = str(val).strip().lower()
                return s in ("", "nan", "none")

            # --- 5. UPSERT + CHANGE LOGGING for s14 (per-row savepoint) ---
            if table_name == 'current_data':
                with engine.begin() as conn:
                    # Ensure kategori_pelanggaran column exists so row.get works
                    if "kategori_pelanggaran" not in df.columns:
                        df["kategori_pelanggaran"] = None
                    for idx, row in df.iterrows():
                        nomor_lha = row.get("nomor_lha", "") or ""
                        pn = row.get("pn", "") or ""

                        # start savepoint for this row
                        save = conn.begin_nested()
                        try:
                            # If kategori is missing-ish -> compute it
                            raw_kat = row.get("kategori_pelanggaran")
                            if is_missing(raw_kat):
                                try:
                                    # penentuan_kategori_pelanggaran expects a dict-like row
                                    result = penentuan_kategori_pelanggaran(row.to_dict())
                                    row["kategori_pelanggaran"] = result["kategori"]
                                    # APPLY sanitized ke DataFrame row
                                    for col, val in result["sanitized"].items():
                                        row[col] = val
                                except Exception as e:
                                    # log error, record and skip this row (don't abort whole upload)
                                    err_msg = f"Row nomor_lha={nomor_lha}, pn={pn}: kategori error: {e}"
                                    errors.append({"nomor_lha": nomor_lha, "pn": pn, "error": str(e)})
                                    # write event log using the same connection to avoid locking
                                    try:
                                        HukdisRepository.insert_event(conn, "upload_error", err_msg, upload_ts)
                                    except Exception:
                                        # best-effort; don't fail the whole upload if logging fails
                                        pass
                                    save.rollback()
                                    continue  # skip to next row

                            existing = HukdisRepository.find_existing(conn, table_name, nomor_lha, pn)

                            if existing:
                                # update path
                                row_id = existing["id"]
                                changes = detect_changes(dict(existing), row.to_dict())
                                if changes:
                                    updated += 1
                                    HukdisRepository.update_row(conn, table_name, row, row_id)
                                    HukdisRepository.log_changes(conn, upload_id, row_id, changes, upload_ts)
                            else:
                                # insert path
                                inserted += 1
                                HukdisRepository.insert_row(conn, table_name, row)

                            save.commit()

                        except Exception as inner_e:
                            # rollback and record error for this row
                            try:
                                save.rollback()
                            except Exception:
                                pass
                            err_detail = f"Row nomor_lha={nomor_lha}, pn={pn}: DB error: {inner_e}"
                            errors.append({"nomor_lha": nomor_lha, "pn": pn, "error": str(inner_e)})
                            try:
                                HukdisRepository.insert_event(conn, "upload_error", err_detail, upload_ts)
                            except Exception:
                                pass
                            continue

                # optional: record a summary event
                    try:
                        HukdisRepository.insert_event(conn, "Upload", f"Inserted={inserted} Updated={updated}")
                    except Exception:
                        pass
            # --- UPSERT + LOGGING for OLD_DATA S48 ---
            else:
                with engine.begin() as conn:
                    for idx, row in df.iterrows():
                        nomor_lha = row.get("nomor_lha", "") or ""
                        pn = row.get("pn", "") or ""

                        # start savepoint for this row
                        save = conn.begin_nested()
                        try:
                            existing = HukdisRepository.find_existing(conn, table_name, nomor_lha, pn)

                            if existing:
                                # update path
                                row_id = existing["id"]
                                changes = detect_changes(dict(existing), row.to_dict())
                                if changes:
                                    updated += 1
                                    HukdisRepository.update_row(conn, table_name, row, row_id)
                                    HukdisRepository.log_changes(conn, upload_id, row_id, changes, upload_ts)
                            else:
                                # insert path
                                inserted += 1
                                HukdisRepository.insert_row(conn, table_name, row)

                            save.commit()

                        except Exception as inner_e:
                            print("OLD INSERT ERROR:", inner_e)
                            # rollback and record error for this row
                            try:
                                save.rollback()
                            except Exception:
                                pass
                            err_detail = f"Row nomor_lha={nomor_lha}, pn={pn}: DB error: {inner_e}"
                            errors.append({"nomor_lha": nomor_lha, "pn": pn, "error": str(inner_e)})
                            try:
                                HukdisRepository.insert_event(conn, "upload_error", err_detail, upload_ts)
                            except Exception:
                                pass
                            continue
                # optional: record a summary event
                    try:
                        HukdisRepository.insert_event(conn, "Upload", f"Inserted={inserted} Updated={updated}")
                    except Exception:
                        pass

            # --- 6. Update log summary ---
            HukdisRepository.update_upload_summary(upload_id, len(df), inserted, updated, table_name)

            # --- 7. Return result ---
            result = {
                "status": "success",
                "message": "Upload finished with upsert + change logging.",
                "inserted": inserted,
                "updated": updated,
                "errors": errors
            }
            return result

        except Exception as e:
            return {"status": "error", "message": str(e)}

try:
    from backend.app.repository.manage_repository import ManageRepository
except ModuleNotFoundError:
    from app.repository.manage_repository import ManageRepository
try:
    from backend.app.config.database import engine
except ModuleNotFoundError:
    from app.config.database import engine
from sqlalchemy import text


class ManageService:

    @staticmethod
    def filter_data(
        keyword, pn, nomor_lha, nama_unit_kerja, status_tindak_lanjut,
        tanggal_exit_start, tanggal_exit_end,
        limit, offset
    ):
        return ManageRepository.filter_data(
            keyword, pn, nomor_lha, nama_unit_kerja, status_tindak_lanjut,
            tanggal_exit_start, tanggal_exit_end,
            limit, offset
        )

    @staticmethod
    def edit_row(row_id: int, payload: dict, table_name="current_data"):
        if not payload:
            return {"status": "error", "message": "Empty payload"}

        return ManageRepository.edit_row_with_timestamp(row_id, payload, table_name)

    @staticmethod
    def soft_delete(row_id: int, table="current_data"):
        with engine.begin() as conn:
            ManageRepository.soft_delete(conn, table, row_id)
        return {"status": "success", "deleted_id": row_id}

    @staticmethod
    def soft_delete_bulk(ids: list, table="current_data"):
        if not ids:
            return {"status": "error", "message": "Empty ID list"}

        with engine.begin() as conn:
            ManageRepository.soft_delete_bulk(conn, table, ids)

        return {"status": "success", "deleted_count": len(ids)}

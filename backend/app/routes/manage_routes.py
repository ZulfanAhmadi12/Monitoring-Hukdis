from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
try:
    from backend.app.services.manage_service import ManageService
except ModuleNotFoundError:
    from app.services.manage_service import ManageService

router = APIRouter(prefix="/manage", tags=["Manage"])

class BulkDeleteRequest(BaseModel):
    ids: list[int]

@router.get("/current_data/filter")
def filter_data(
    keyword: str = None,
    pn: str = None,
    nomor_lha: str = None,
    nama_unit_kerja: str = None,
    status_tindak_lanjut: str = None,
    tanggal_exit_start: str = None,
    tanggal_exit_end: str = None,
    limit: int = 500,
    offset: int = 0
):
    return ManageService.filter_data(
        keyword, pn, nomor_lha, nama_unit_kerja, status_tindak_lanjut,
        tanggal_exit_start, tanggal_exit_end,
        limit, offset
    )

@router.patch("/current_data/{row_id}")
def patch_current_data(row_id: int, payload: dict):
    return ManageService.edit_row(row_id, payload)

@router.delete("/current_data/{row_id}")
def delete_row(row_id: int):
    return ManageService.soft_delete(row_id)

@router.post("/current_data/bulk_delete")
def bulk_delete(payload: BulkDeleteRequest):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    return ManageService.soft_delete_bulk(payload.ids)

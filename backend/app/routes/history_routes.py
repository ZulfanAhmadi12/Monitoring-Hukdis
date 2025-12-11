from fastapi import APIRouter, HTTPException, Query
try:
    from backend.app.services.history_service import HistoryService
except ModuleNotFoundError:
    from app.services.history_service import HistoryService
from typing import Optional

router = APIRouter(prefix="/hukdis", tags=["Upload History"])

@router.get("/upload_history")
def upload_history(limit: int = 200, offset: int = 0, filename: str = None,
                   date_start: str = None, date_end: str = None):
    return HistoryService.list_upload_history(limit, offset, filename, date_start, date_end)


@router.get("/upload_history/{upload_id}")
def upload_detail(upload_id: int, include_changes: bool = Query(False)):
    detail = HistoryService.get_upload_detail(upload_id, include_changes)
    if not detail:
        raise HTTPException(status_code=404, detail="Upload not found")
    return detail


@router.get("/change_log")
def change_log(upload_id: int = Query(...), column_name: str = None,
               group_by_row: bool = Query(False), limit: int = 1000, offset: int = 0):
    return HistoryService.list_change_log(upload_id, column_name, group_by_row, limit, offset)


@router.get("/event_logs")
def get_event_logs(start: Optional[str] = Query(None), end: Optional[str] = Query(None)):
    return HistoryService.get_logs(start, end)


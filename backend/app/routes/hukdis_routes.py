from fastapi import APIRouter, UploadFile, File, Query
try:
    from backend.app.services.hukdis_service import HukdisService
except ModuleNotFoundError:
    from app.services.hukdis_service import HukdisService
from typing import Optional

router = APIRouter(prefix="/hukdis", tags=["Hukdis"])

@router.post("/upload_excel")
async def upload_excel(
    file: UploadFile = File(...),
    format_type: str = Query("new", enum=["new", "old"])
):
    return await HukdisService.upload_excel(file, format_type)

@router.get("/latest_event")
def latest_event(action: Optional[str] = Query(None)):
    try:
        from backend.app.utils.logger import get_latest_event
    except ModuleNotFoundError:
        from app.utils.logger import get_latest_event
    if not action:
        return {"timestamp": None}
    ts = get_latest_event(action)
    return {"timestamp": ts}



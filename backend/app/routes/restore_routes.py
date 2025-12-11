from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
try:
    from backend.app.services.restore_service import RestoreService
except ModuleNotFoundError:
    from app.services.restore_service import RestoreService

router = APIRouter(prefix="/hukdis", tags=["Restore"])

@router.post("/backup")
def backup(table_name: str = Query(...)):
    try:
        result = RestoreService.backup_table(table_name)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
def restore_current_data():
    try:
        result = RestoreService.restore_current_data()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/last_backup_time/{table_name}")
def last_backup_time(table_name: str):
    try:
        t = RestoreService.get_last_backup_time(table_name)
        if not t:
            return {"status": "error", "message": "No backup found"}
        return {"status": "success", "table": table_name, "last_backup_time": t}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/backup/snapshot")
def backup_snapshot():
    return RestoreService.backup_snapshot()

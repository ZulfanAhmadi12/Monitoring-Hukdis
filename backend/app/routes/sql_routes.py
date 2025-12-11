from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
try:
    from backend.app.services.sql_service import SQLService
except ModuleNotFoundError:
    from app.services.sql_service import SQLService

router = APIRouter(prefix="/sql", tags=["SQL"])

class SQLRequest(BaseModel):
    query: str

@router.post("/run")
def run_query(payload: SQLRequest):
    try:
        df = SQLService.run_query(payload.query)
        return {
            "columns": df.columns.tolist(),
            "rows": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

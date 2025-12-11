from fastapi import APIRouter
try:
    from backend.app.config.settings import settings
except ModuleNotFoundError:
    from app.config.settings import settings

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/app_info")
def app_info():
    return {
        "environment": settings.APP_ENV,
        "db_path": settings.DB_PATH,
        "version": "1.0.0",
        "creator": "Panjuu"
    }

# frontend/services/history_service.py
from services.api_client import api_get

def get_upload_history(params):
    return api_get("/hukdis/upload_history", params=params)

def get_upload_detail(upload_id, include_changes=False):
    return api_get(
        f"/hukdis/upload_history/{upload_id}",
        params={"include_changes": include_changes}
    )

def get_change_log(params):
    return api_get("/hukdis/change_log", params=params)

def get_event_logs(start: str = None, end: str = None):
    """
    Wrapper untuk memanggil endpoint backend:
        GET /event_logs?start=YYYY-MM-DD&end=YYYY-MM-DD

    Backend akan otomatis fallback ke 30 hari terakhir
    jika `start` dan `end` = None.
    """
    params = {}

    if start:
        params["start"] = start
    if end:
        params["end"] = end

    return api_get("/hukdis/event_logs", params=params)

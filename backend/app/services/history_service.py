try:
    from backend.app.repository.history_repository import HistoryRepository
except ModuleNotFoundError:
    from app.repository.history_repository import HistoryRepository
from datetime import datetime, timedelta


class HistoryService:

    @staticmethod
    def list_upload_history(limit=200, offset=0, filename=None, date_start=None, date_end=None):
        return HistoryRepository.list_upload_history(limit, offset, filename, date_start, date_end)

    @staticmethod
    def get_upload_detail(upload_id: int, include_changes: bool = False, change_limit: int = 1000, change_offset: int = 0):
        return HistoryRepository.get_upload_detail(upload_id, include_changes, change_limit, change_offset)

    @staticmethod
    def list_change_log(upload_id: int, column_name: str = None, group_by_row: bool = False, limit: int = 1000, offset: int = 0):
        return HistoryRepository.list_change_log(upload_id, column_name, group_by_row, limit, offset)

    @staticmethod
    def get_logs(start, end):

        # Default = last 30 days
        if not start or not end:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
            default_used = True
        else:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            default_used = False

        logs = HistoryRepository.fetch_logs(start_dt, end_dt)

        return {
            "default_range_used": default_used,
            "start": start_dt.strftime("%Y-%m-%d"),
            "end": end_dt.strftime("%Y-%m-%d"),
            "logs": logs,
        }

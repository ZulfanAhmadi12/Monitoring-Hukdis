try:
    from backend.app.repository.restore_repository import RestoreRepository
except ModuleNotFoundError:
    from app.repository.restore_repository import RestoreRepository
try:
    from backend.app.utils.logger import log_event
except ModuleNotFoundError:
    from app.utils.logger import log_event

class RestoreService:

    @staticmethod
    def backup_table(table_name: str):
        """Backup logis ke tabel current_data_backup."""
        log_event('backup table', 'Backup Table Data S14 saat ')
        return RestoreRepository.backup(table_name)
    
    @staticmethod
    def backup_snapshot():
        """Backup fisik .db snapshot."""
        return RestoreRepository.backup_snapshot()

    @staticmethod
    def restore_current_data():
        return RestoreRepository.restore_current_data()

    @staticmethod
    def get_last_backup_time(table_name: str):
        return RestoreRepository.last_backup_time(table_name)

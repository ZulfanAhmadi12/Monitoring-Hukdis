from services.api_client import api_get

def get_app_info():
    return api_get("/system/app_info")

import requests
from dotenv import load_dotenv
import os

load_dotenv(override=False)

API_BASE = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
print("API_BASE =", API_BASE)

def api_get(path, params=None):
    res = requests.get(f"{API_BASE}{path}", params=params)
    res.raise_for_status()
    return res.json()

def api_get_raw(path, params=None):
    return requests.get(f"{API_BASE}{path}", params=params)


def api_post(path, json=None, files=None):
    res = requests.post(f"{API_BASE}{path}", json=json, files=files)
    res.raise_for_status()
    return res.json()

def api_patch(path, json=None):
    res = requests.patch(f"{API_BASE}{path}", json=json)
    res.raise_for_status()
    return res.json()

def api_delete(path):
    res = requests.delete(f"{API_BASE}{path}")
    res.raise_for_status()
    return res.json()

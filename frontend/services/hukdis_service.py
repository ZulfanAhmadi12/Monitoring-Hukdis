from services.api_client import api_get, api_post, api_patch, api_delete


def upload_excel(file, format_type: str):
    files = {
        "file": (
            file.name,
            file,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    return api_post(f"/hukdis/upload_excel?format_type={format_type}", files=files)


def get_latest_event(action: str):
    return api_get("/hukdis/latest_event", params={"action": action})


def get_filtered_data(params):
    return api_get("/hukdis/current_data/filter", params)


def delete_row(row_id):
    return api_delete(f"/hukdis/current_data/{row_id}")


def delete_bulk(ids):
    return api_post("/hukdis/current_data/bulk_delete", json={"ids": ids})


def patch_row(row_id, payload):
    return api_patch(f"/hukdis/current_data/{row_id}", json=payload)

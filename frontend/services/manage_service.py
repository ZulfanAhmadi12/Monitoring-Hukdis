from services.api_client import api_get, api_patch, api_delete, api_post

def get_filtered_data(filters):
    return api_get("/manage/current_data/filter", params=filters)

def patch_row(row_id, changes):
    return api_patch(f"/manage/current_data/{row_id}", json=changes)

def delete_row(row_id):
    return api_delete(f"/manage/current_data/{row_id}")

def delete_bulk(ids):
    return api_post("/manage/current_data/bulk_delete", json={"ids": ids})

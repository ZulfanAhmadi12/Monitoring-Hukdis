from services.api_client import api_post

def run_sql_query(query: str):
    """
    Send a SELECT SQL query to the backend.
    Backend returns { columns: [...], rows: [...] }
    """
    return api_post("/sql/run", json={"query": query})

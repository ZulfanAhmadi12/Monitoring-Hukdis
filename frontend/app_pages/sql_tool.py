import streamlit as st
import pandas as pd
import time

from services.sql_service import run_sql_query
from components.export_button import export_buttons


def render():
    st.header("🧠 SQL Query Tool")
    st.caption("Run safe, SELECT-only SQL queries against your Hukdis database.")

    # ============================================================
    # 1. Query Input Panel
    # ============================================================
    with st.container(border=True):
        st.subheader("📝 SQL Editor")

        col1, col2 = st.columns([4, 1])

        with col1:
            st.caption("Write your SELECT query below.")
        with col2:
            if st.button("🧹 Clear Query"):
                st.session_state["sql_input"] = ""

        default_query = "SELECT * FROM current_data LIMIT 10;"

        query_input = st.text_area(
            "SQL Query",
            value=st.session_state.get("sql_input", default_query),
            height=180,
            help="Only SELECT statements are allowed for safety."
        )

        st.session_state["sql_input"] = query_input

        run_clicked = st.button("▶️ Run Query", type="primary")

    if not run_clicked:
        return

    # ============================================================
    # 2. Execute Query
    # ============================================================
    start_time = time.time()

    try:
        result = run_sql_query(query_input)
        columns = result.get("columns", [])
        rows = result.get("rows", [])

        df = pd.DataFrame(rows, columns=columns)

    except Exception as e:
        st.error(f"❌ Error while executing query: {e}")
        return

    exec_time_ms = (time.time() - start_time) * 1000

    # ============================================================
    # 3. Result Summary Panel
    # ============================================================
    with st.container(border=True):
        st.subheader("📊 Query Summary")

        if df.empty:
            st.warning("⚠️ Query executed successfully but returned **0 rows**.")
        else:
            st.success(f"Returned **{len(df)} rows** in **{exec_time_ms:.2f} ms**")

        st.caption("Below is a preview of your SQL query results:")

    # ============================================================
    # 4. Result Table
    # ============================================================
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=350
    )

    # ============================================================
    # 5. Export Panel
    # ============================================================
    with st.container(border=True):
        st.subheader("📥 Export Results")

        if df.empty:
            st.info("Nothing to export.")
        else:
            export_buttons(df)

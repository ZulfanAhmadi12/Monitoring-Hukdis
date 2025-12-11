import streamlit as st
import pandas as pd
from datetime import date

from services.history_service import (
    get_upload_history,
    get_upload_detail,
    get_change_log,
    get_event_logs   # <<< TAMBAHKAN INI
)

from components.export_button import export_buttons


def render():
    st.header("📚 Upload History & Change Log")
    st.caption("View upload events, inspect metadata, and review column-level changes.")

    # ============================================================
    # 1. FILTER PANEL (Upload History)
    # ============================================================
    with st.container(border=True):
        st.subheader("🔍 Filter Upload History")
        st.caption("Apply filters to narrow down upload events.")

        c1, c2, c3 = st.columns([3, 2, 2])

        with c1:
            filename = st.text_input("Filename contains", "")

        with c2:
            start_date_history = st.date_input("Upload Date — Start", None)

        with c3:
            end_date_history = st.date_input("Upload Date — End", None)

        row_per_page = st.number_input("Rows per page", min_value=20, max_value=2000, value=200)
        page = st.number_input("Page", min_value=0, step=1, value=0)

    params_history = {
        "filename": filename or None,
        "date_start": start_date_history.strftime("%Y-%m-%d") if start_date_history else None,
        "date_end": end_date_history.strftime("%Y-%m-%d") if end_date_history else None,
        "limit": int(row_per_page),
        "offset": int(page) * int(row_per_page),
    }

    # ============================================================
    # 2. FETCH HISTORY
    # ============================================================
    try:
        history = get_upload_history(params_history)
    except Exception as e:
        st.error(f"❌ Unable to load upload history: {e}")
        return

    df_hist = pd.DataFrame(history)

    if df_hist.empty:
        st.info("No upload history found with current filters.")
        return

    with st.container(border=True):
        st.subheader("📌 Upload History")

        display_cols = [
            c for c in ["id", "filename", "upload_time", "total_rows", "inserted_rows", "updated_rows"]
            if c in df_hist.columns
        ]

        st.dataframe(
            df_hist[display_cols],
            use_container_width=True,
            height=300
        )

    # ============================================================
    # 3. SELECT UPLOAD ID
    # ============================================================
    labels = df_hist.apply(
        lambda r: f"{r['id']} — {r.get('filename','')} — {r.get('upload_time','')}",
        axis=1
    ).tolist()

    st.markdown("### 📎 Select Upload")
    idx_selected = st.selectbox(
        "Choose an upload event to view metadata & change logs:",
        list(range(len(labels))),
        format_func=lambda i: labels[i],
        key="upload_select"
    )

    upload_row = df_hist.iloc[idx_selected]
    upload_id = int(upload_row["id"])

    st.divider()

    # ============================================================
    # 4. UPLOAD DETAIL
    # ============================================================
    with st.container(border=True):
        st.subheader(f"📄 Upload Detail — ID {upload_id}")

        try:
            detail = get_upload_detail(upload_id, include_changes=False)
            upload_meta = detail.get("upload", detail)
            st.json(upload_meta)
        except Exception as e:
            st.warning(f"Unable to load upload detail: {e}")

    # ============================================================
    # 5. CHANGE LOG
    # ============================================================
    with st.container(border=True):
        st.subheader("🔍 Change Log")

        col_filter = st.text_input("Filter by Column Name (optional)", "")

        params_change = {
            "upload_id": upload_id,
            "column_name": col_filter or None,
            "limit": 2000,
            "offset": 0
        }

        try:
            changes = get_change_log(params_change)
        except Exception as e:
            st.error(f"Unable to load change log: {e}")
            return

        if not changes:
            st.info("No change log available for this upload.")
        else:
            df_log = pd.DataFrame(changes)

            df_log.rename(columns={
                "column_name": "Column",
                "before_value": "Before",
                "after_value": "After"
            }, inplace=True)

            cols_log = [
                c for c in ["row_id", "nomor_lha", "pn", "Column", "Before", "After", "change_time"]
                if c in df_log.columns
            ]

            st.dataframe(df_log[cols_log], use_container_width=True, height=300)

            # EXPORT
            st.markdown("### 📥 Export Change Log")
            export_buttons(df_log[cols_log])
    
    st.divider()

    with st.container(border=True):
        st.subheader("📜 Event Log History")
        st.caption("If no dates are chosen, the system will automatically show the last 30 days.")

        col1, col2 = st.columns(2)

        start_date = col1.date_input("Start Date", value=None)
        end_date   = col2.date_input("End Date", value=None)

        # Convert to yyyy-mm-dd or keep None
        s = start_date.strftime("%Y-%m-%d") if start_date else None
        e = end_date.strftime("%Y-%m-%d") if end_date else None

        result = get_event_logs(s, e)

        # Informasikan jika backend menggunakan default range
        if result.get("default_range_used"):
            st.info(f"Menampilkan log **30 hari terakhir** "
                    f"({result['start']} → {result['end']}).")

        logs = result["logs"]

        if not logs:
            st.warning("Tidak ada log ditemukan dalam rentang tanggal tersebut.")
        else:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Ditemukan **{len(df)} event log**.")


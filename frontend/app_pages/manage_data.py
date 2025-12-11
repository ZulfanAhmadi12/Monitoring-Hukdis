import streamlit as st
import pandas as pd

from services.manage_service import (
    get_filtered_data,
    patch_row,
    delete_row,
    delete_bulk,
)

from components.filter_bar import render_filter_bar
from components.export_button import export_buttons
from utils.normalize import normalize


def render():
    st.header("📝 Manage Current Data")
    st.caption("View, edit, soft-delete and export disciplinary records.")

    # ============================================================
    # 1. FILTER PANEL
    # ============================================================
    with st.container(border=True):
        st.subheader("🔍 Filter Records")
        st.caption("Use filters below to narrow down the dataset.")
        filters = render_filter_bar()

    # ============================================================
    # 2. LOAD DATA
    # ============================================================
    records = get_filtered_data(filters)
    df = pd.DataFrame(records)

    if df.empty:
        st.warning("No records match your filters.")
        return

    df_orig = df.copy()

    # Add delete column for UI
    df["delete"] = False

    # ============================================================
    # 3. DATA EDITOR (STATIC KEY)
    # ============================================================
    with st.container(border=True):
        st.subheader("📄 Data Viewer & Editor")
        st.caption("You can freely edit values or mark rows for deletion.")

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "delete": st.column_config.CheckboxColumn(
                    "Delete?",
                    help="Mark this row for soft delete",
                )
            },
            key="data_editor",  # static key = stable table
        )

    # ============================================================
    # 4. ACTION BAR
    # ============================================================
    st.markdown("---")
    st.markdown("### ⚙️ Actions")

    colA, colB = st.columns([1, 1])

    # ============================================================
    # SOFT DELETE (SELECTED ROWS)
    # ============================================================
    with colA:
        st.markdown("#### 🗑️ Soft Delete")
        delete_ids = edited_df[edited_df["delete"] == True]["id"].tolist()

        if st.button("Delete Selected Rows", type="primary", key="btn_delete_selected"):
            if not delete_ids:
                st.warning("No rows selected.")
            else:
                if len(delete_ids) == 1:
                    delete_row(delete_ids[0])
                else:
                    delete_bulk(delete_ids)

                st.success(f"Successfully deleted {len(delete_ids)} record(s).")
                st.rerun()   # refresh table

    # ============================================================
    # APPLY EDITS (PATCH)
    # ============================================================
    with colB:
        st.markdown("#### 💾 Apply Edits")

        if st.button("Save Changes", type="primary", key="btn_save_changes"):

            changes_to_apply = []

            for idx, row in edited_df.iterrows():
                orig = df_orig.loc[idx]
                diff = {}

                for col in df.columns:
                    if col == "delete":
                        continue
                    if normalize(orig[col]) != normalize(row[col]):
                        diff[col] = row[col]

                if diff:
                    changes_to_apply.append({"id": row["id"], "changes": diff})

            if not changes_to_apply:
                st.info("No changes detected.")
                return

            progress = st.progress(0)
            for i, item in enumerate(changes_to_apply, start=1):
                patch_row(item["id"], item["changes"])
                progress.progress(i / len(changes_to_apply))

            st.success(f"{len(changes_to_apply)} row(s) updated.")
            st.rerun()

    # ============================================================
    # 5. DELETE ALL FILTERED ROWS (Danger Zone)
    # ============================================================
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")

    if "confirm_delete_all" not in st.session_state:
        st.session_state.confirm_delete_all = False

    total_rows = len(df_orig)

    with st.container(border=True):
        st.error("This will delete ALL filtered rows permanently.")

        c1, c2 = st.columns([1, 1])

        # FIRST CLICK — show confirmation
        if not st.session_state.confirm_delete_all:
            if st.button(
                f"🗑️ Delete ALL {total_rows} Filtered Rows",
                type="primary",
                key="btn_delete_all_show"
            ):
                st.session_state.confirm_delete_all = True
                st.rerun()

        # CONFIRMATION UI
        else:
            st.warning("Are you absolutely sure? This action cannot be undone.")

            with c1:
                if st.button("✅ Yes, delete everything", key="btn_delete_all_confirm"):

                    ids_to_delete = df_orig["id"].tolist()
                    delete_bulk(ids_to_delete)

                    st.success(f"Deleted {len(ids_to_delete)} rows.")
                    st.session_state.confirm_delete_all = False
                    st.rerun()

            with c2:
                if st.button("❌ Cancel", key="btn_delete_all_cancel"):
                    st.session_state.confirm_delete_all = False
                    st.info("Delete All canceled.")
                    st.rerun()

    # ============================================================
    # 6. EXPORT
    # ============================================================
    with st.container(border=True):
        st.subheader("📥 Export Results")
        st.caption("Exports use the **original filtered data** (no delete column).")
        export_buttons(df_orig)

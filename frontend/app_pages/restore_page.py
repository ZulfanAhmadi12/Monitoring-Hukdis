import streamlit as st

from services.restore_service import (
    get_last_backup_time,
    restore_current_data,
    backup_internal,
    backup_snapshot,
    )

def render():
    st.header("♻️ Restore Current Data (S14)")

    # -------------------------------------
    # 1. Last Backup Information
    # -------------------------------------
    resp = get_last_backup_time()
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") == "success":
            st.info(f"🕒 Last Backup Time: **{data['last_backup_time']}**")
        else:
            st.warning("⚠ No backup found for current_data.")
    else:
        st.error("Failed to fetch backup info from the backend.")

    st.markdown("""
    Restoring will replace the **current_data** table using the **latest backup**.  
    The `legacy_data (s48)` table will not be affected.
    """)

    # -------------------------------------
    # 2. RESTORE BUTTON
    # -------------------------------------
    if st.button("♻️ Restore Latest Backup"):
        with st.spinner("Restoring from the latest backup...."):
            try:
                result = restore_current_data()   # <- now returns dict, not Response

                if result.get("status") == "success":
                    st.success(result.get("message", "Restore completed successfully."))
                else:
                    st.warning(result.get("message", "Restore finished with warnings."))

            except Exception as e:
                st.error(f"Restore failed: {e}")

    st.divider()

      # -------------------------------------
    # 3. MANUAL BACKUP (Improved UI)
    # -------------------------------------
    st.subheader("💾 Manual Backup Options")
    st.write("Choose one of the backup methods below:")

    st.markdown("### 📦 Backup Methods")

    # Card-style layout using columns
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🗄 Internal Backup")
            st.caption("""
            Creates an **SQL-based backup** inside the database server.  
            Suitable for automatic scheduled backups.
            """)

            if st.button("Run Internal Backup", key="btn_internal_backup"):
                with st.spinner("Running internal SQL backup..."):
                    res = backup_internal()
                    st.success(res.get("message", "Internal backup completed."))

    with col2:
        with st.container(border=True):
            st.markdown("#### 💾 Snapshot Backup (.db file)")
            st.caption("""
            Creates a **physical .db snapshot file** in your `/backup` folder.  
            Best for manual copies or portable backups.
            """)

            if st.button("Create Snapshot", key="btn_snapshot_backup"):
                with st.spinner("Creating database snapshot..."):
                    res = backup_snapshot()
                    st.success(res.get("message", "Snapshot created successfully."))

import streamlit as st
from services.system_service import get_app_info
from services.restore_service import get_last_backup_time

def render_sidebar():
    st.sidebar.markdown("## 📊 Hukdis Monitoring System")

    # Navigation
    page = st.sidebar.radio(
        "Menu",
        [
            "🏠 Home",
            "📤 Upload Excel File",
            "📝 Manage Current Data",
            "📚 Upload History & Change Log",
            "🧠 SQL Query Tool",
            "🛠️ Restore S14 Data",
        ],
        key="_sidebar_page_"
    )

    # ---------------------------
    # SYSTEM INFO
    # ---------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙ System Info")

    try:
        info = get_app_info()
        st.sidebar.caption(f"**Environment:** {info.get('environment')}")
        st.sidebar.caption(f"**DB Path:** {info.get('db_path')}")
        st.sidebar.caption(f"**Version:** {info.get('version')}")
        st.sidebar.caption(f"**Creator:** {info.get('creator')}")
    except:
        st.sidebar.caption("Unable to load system info")

    # Last backup
    try:
        resp = get_last_backup_time()
        if resp.status_code == 200 and resp.json().get("status") == "success":
            st.sidebar.caption(f"**Last Backup:** {resp.json()['last_backup_time']}")
        else:
            st.sidebar.caption("**Last Backup:** None")
    except:
        st.sidebar.caption("**Last Backup:** Error")

    if page == "🏠 Home":
        return "home"
    if page == "📤 Upload Excel File":
        return "upload"
    if page == "📝 Manage Current Data":
        return "manage"
    if page == "📚 Upload History & Change Log":
        return "history"
    if page == "🧠 SQL Query Tool":
        return "sql"
    if page == "🛠️ Restore S14 Data":
        return "restore"

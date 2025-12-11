import streamlit as st
from layouts.sidebar import render_sidebar

from app_pages import (
    upload_page,
    upload_history_log,
    sql_tool,
    restore_page,
    manage_data
)

st.set_page_config(
    page_title="📊 Hukdis Monitoring System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar returns which page the user selected
page = render_sidebar()

PAGE_MAP = {
    "home": None,
    "upload": upload_page,
    "history": upload_history_log,
    "sql": sql_tool,
    "restore": restore_page,
    "manage": manage_data
}

if page == "home":
    # Render Home Dashboard
    st.markdown("# 👋 Welcome to Hukdis Repository & Monitoring System")

    st.markdown("""
    This system helps you store, manage and analyze **Hukuman Disiplin (S14)** data efficiently.
    Use the menu on the left to upload files, review history, restore data, and more.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📤 Upload new Excel files anytime.")
    with col2:
        st.info("📝 Edit & manage current records easily.")
    with col3:
        st.info("📚 Track changes with full audit logs.")
else:
    PAGE_MAP[page].render()

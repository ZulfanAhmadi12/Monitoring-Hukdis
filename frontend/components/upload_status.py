import streamlit as st

def render_upload_status(latest_event: dict):
    ts = latest_event.get("timestamp")
    if ts:
        st.info(f"🕒 Last Upload: {ts}")
    else:
        st.info("🕒 No upload recorded yet.")

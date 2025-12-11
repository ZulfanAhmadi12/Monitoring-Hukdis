import streamlit as st
from services.hukdis_service import upload_excel, get_latest_event
from components.upload_status import render_upload_status

def render():
    st.header("📤 Upload Excel File")
    st.caption("Use this form to upload S14 (new) or S48 (old) format disciplinary data.")

    # ============================================================
    # 1. Last Upload Status
    # ============================================================
    with st.container(border=True):
        st.subheader("🕒 Last Upload Status")
        try:
            latest_event = get_latest_event("Upload")
            render_upload_status(latest_event)
        except Exception:
            st.warning("Unable to fetch the latest upload status from backend.")

    st.divider()

    # ============================================================
    # 2. Upload Form
    # ============================================================
    with st.container(border=True):
        st.subheader("📁 Upload New Excel File")

        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=["xlsx"],
            help="Only .xlsx files are supported."
        )

        format_type = st.selectbox(
            "Select format type",
            ["new", "old"],
            format_func=lambda x: "New Format (S14)" if x == "new" else "Old Format (S48)"
        )

        # Show metadata preview if file is selected
        if uploaded_file:
            st.caption("📦 File Info")
            st.write({
                "filename": uploaded_file.name,
                "size (KB)": round(len(uploaded_file.getvalue()) / 1024, 2),
                "format": format_type,
            })

        st.markdown("")

        # ============================================================
        # 3. Upload Action
        # ============================================================
        upload_btn = st.button("🚀 Upload File", type="primary")

        if upload_btn:
            if not uploaded_file:
                st.error("Please choose a file before uploading.")
                return

            with st.spinner("Uploading and processing data..."):
                try:
                    result = upload_excel(uploaded_file, format_type)

                    status = result.get("status")
                    msg = result.get("message", "")

                    if status == "success":
                        inserted = result.get("inserted", 0)
                        updated = result.get("updated", 0)

                        st.success(
                            f"✅ Upload completed successfully!\n\n"
                            f"• Inserted rows: **{inserted}**\n"
                            f"• Updated rows: **{updated}**"
                        )
                    else:
                        st.warning(msg)
                        st.warning(f"{len(result['errors'])} row(s) had issues; see Event Log or details below.")
                        st.json(result["errors"])

                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

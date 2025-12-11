import streamlit as st

def render_filter_bar():
    cols = st.columns(3)

    with cols[0]:
        keyword = st.text_input("Keyword (all columns)", "")
        pn = st.text_input("PN", "")
        nomor_lha = st.text_input("Nomor LHA", "")

    with cols[1]:
        unit = st.text_input("Unit Kerja", "")
        status = st.text_input("Status", "")

    with cols[2]:
        tgl_start = st.date_input("Tanggal Exit Start", None)
        tgl_end = st.date_input("Tanggal Exit End", None)

    return {
        "keyword": keyword or None,
        "pn": pn or None,
        "nomor_lha": nomor_lha or None,
        "nama_unit_kerja": unit or None,
        "status_tindak_lanjut": status or None,
        "tanggal_exit_start": tgl_start.strftime("%Y-%m-%d") if tgl_start else None,
        "tanggal_exit_end": tgl_end.strftime("%Y-%m-%d") if tgl_end else None
    }

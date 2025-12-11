import streamlit as st
import pandas as pd
from io import BytesIO


def export_buttons(df):    
    format = st.radio("Format", ["CSV", "Excel"], horizontal=True)

    if format == "CSV":
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="export.csv",
            mime="text/csv",
        )

    else:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            label="📥 Download Excel",
            data=buffer.getvalue(),
            file_name="export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
